#!/usr/bin/env python3
"""Patch Hermes bundled Langfuse guard for BCM/internal endpoints."""
from __future__ import annotations

import argparse
import difflib
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_PLUGIN_FILES = (
    Path("/usr/local/lib/hermes-agent/plugins/observability/langfuse/__init__.py"),
    Path.home() / ".hermes/hermes-agent/plugins/observability/langfuse/__init__.py",
)

DEFAULT_BASE_URL_LINE = (
    '    base_url = _env("HERMES_LANGFUSE_BASE_URL") or '
    '_env("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"\n'
)

PATCH_MARKER = '_is_cloud = urlsplit(base_url).hostname == "cloud.langfuse.com"'


def _find_plugin_file(explicit: str | None) -> Path:
    """定位 Hermes Langfuse 插件文件路径。"""
    if explicit:
        path = Path(explicit).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"plugin file not found: {path}")
        return path
    for path in DEFAULT_PLUGIN_FILES:
        if path.exists():
            return path
    searched = ", ".join(str(p) for p in DEFAULT_PLUGIN_FILES)
    raise FileNotFoundError(f"could not find Hermes Langfuse plugin; searched: {searched}")


def _ensure_urlsplit_import(lines: list[str]) -> tuple[list[str], bool]:
    """确保源码中存在 urlsplit 的 import 语句。"""
    if any(line.strip() == "from urllib.parse import urlsplit" for line in lines):
        return lines, False
    insert_at = None
    for index, line in enumerate(lines):
        if line.startswith("from typing import "):
            insert_at = index + 1
            break
    if insert_at is None:
        for index, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = index + 1
    if insert_at is None:
        raise ValueError("could not find import block for urlsplit insertion")
    return lines[:insert_at] + ["from urllib.parse import urlsplit\n"] + lines[insert_at:], True


def _function_end(lines: list[str], start: int) -> int:
    """查找函数定义的结束行号。"""
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("def ") or line.startswith("@dataclass") or line.startswith("class "):
            return index
    return len(lines)


def _patch_lines(lines: list[str]) -> tuple[list[str], bool]:
    """对源码行列表执行 BCM 内部网关兼容性补丁。"""
    lines, changed = _ensure_urlsplit_import(lines)
    text = "".join(lines)
    if PATCH_MARKER in text and "] if _is_cloud else []" in text:
        return lines, changed

    try:
        func_start = next(i for i, line in enumerate(lines) if line.startswith("def _get_langfuse("))
    except StopIteration as exc:
        raise ValueError("could not find _get_langfuse()") from exc
    func_end = _function_end(lines, func_start)

    base_url_indices = [
        i
        for i in range(func_start, func_end)
        if lines[i].lstrip().startswith("base_url = ")
        and "LANGFUSE_BASE_URL" in lines[i]
        and "cloud.langfuse.com" in lines[i]
    ]
    base_url_line = lines[base_url_indices[0]] if base_url_indices else DEFAULT_BASE_URL_LINE
    for index in reversed(base_url_indices):
        del lines[index]
        changed = True
        if index < func_end:
            func_end -= 1

    try:
        missing_if = next(
            i for i in range(func_start, func_end) if "if not (public_key and secret_key):" in lines[i]
        )
        insert_at = next(i for i in range(missing_if, func_end) if lines[i].strip() == "return None") + 1
    except StopIteration as exc:
        raise ValueError("could not find credential-missing return block") from exc
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1
    lines[insert_at:insert_at] = ["\n", base_url_line, "\n"]
    changed = True

    func_end = _function_end(lines, func_start)
    try:
        placeholder_start = next(
            i for i in range(func_start, func_end) if lines[i].lstrip().startswith("placeholder_issues = [")
        )
        if_placeholder = next(
            i
            for i in range(placeholder_start, func_end)
            if lines[i].startswith("    if placeholder_issues:")
        )
    except StopIteration as exc:
        raise ValueError("could not find placeholder_issues guard block") from exc

    if not any(PATCH_MARKER in lines[i] for i in range(func_start, placeholder_start)):
        guard_lines = [
            "    # Prefix validation applies only to Langfuse Cloud; internal gateways\n",
            "    # such as BCM issue Authentication tokens without pk-lf-/sk-lf-.\n",
            '    _is_cloud = urlsplit(base_url).hostname == "cloud.langfuse.com"\n',
        ]
        lines[placeholder_start:placeholder_start] = guard_lines
        changed = True
        placeholder_start += len(guard_lines)
        if_placeholder += len(guard_lines)

    closing = None
    for index in range(placeholder_start, if_placeholder):
        if lines[index].strip() == "]":
            closing = index
    if closing is None:
        raise ValueError("could not find placeholder_issues closing bracket")
    if "if _is_cloud else []" not in lines[closing]:
        lines[closing] = "    ] if _is_cloud else []\n"
        changed = True

    return lines, changed


def patch_text(text: str) -> tuple[str, bool]:
    """对完整源码文本执行补丁，返回补丁后文本和是否变更标志。"""
    lines = text.splitlines(keepends=True)
    patched, changed = _patch_lines(lines)
    return "".join(patched), changed


def _backup(path: Path) -> Path:
    """创建目标文件的备份副本。"""
    primary = path.with_name(path.name + ".bak")
    if not primary.exists():
        backup = primary
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path.with_name(path.name + f".bak.{stamp}")
    shutil.copy2(path, backup)
    return backup


def _self_test() -> int:
    """运行内置的补丁自测用例，验证补丁正确性和幂等性。"""
    fixture = '''"""test plugin."""
import os
from typing import Any, Dict, Optional

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()

def _get_langfuse():
    global _LANGFUSE_CLIENT
    public_key = _env("HERMES_LANGFUSE_PUBLIC_KEY") or _env("LANGFUSE_PUBLIC_KEY")
    secret_key = _env("HERMES_LANGFUSE_SECRET_KEY") or _env("LANGFUSE_SECRET_KEY")
    if not (public_key and secret_key):
        _LANGFUSE_CLIENT = _INIT_FAILED
        return None

    placeholder_issues = [
        msg
        for msg in (
            _validate_langfuse_key("HERMES_LANGFUSE_PUBLIC_KEY", public_key),
            _validate_langfuse_key("HERMES_LANGFUSE_SECRET_KEY", secret_key),
        )
        if msg
    ]
    if placeholder_issues:
        _LANGFUSE_CLIENT = _INIT_FAILED
        return None

    base_url = _env("HERMES_LANGFUSE_BASE_URL") or _env("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
    return base_url
'''
    patched, changed = patch_text(fixture)
    required = [
        "from urllib.parse import urlsplit",
        PATCH_MARKER,
        "] if _is_cloud else []",
    ]
    if not changed or any(item not in patched for item in required):
        print("self-test failed: expected patch markers missing", file=sys.stderr)
        return 1
    again, changed_again = patch_text(patched)
    if changed_again or again != patched:
        print("self-test failed: patch is not idempotent", file=sys.stderr)
        return 1
    try:
        compile(patched, "<self-test>", "exec")
    except Exception as exc:
        print(f"self-test failed: {exc}", file=sys.stderr)
        return 1
    print("self-test ok")
    return 0


def main() -> int:
    """命令行入口，解析参数并执行对应操作。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-file", help="Path to Hermes observability/langfuse/__init__.py")
    parser.add_argument("--check", action="store_true", help="Only verify whether the guard patch is present")
    parser.add_argument("--dry-run", action="store_true", help="Print a unified diff without writing")
    parser.add_argument("--self-test", action="store_true", help="Run the script's built-in patch test")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    try:
        path = _find_plugin_file(args.plugin_file)
        original = path.read_text()
        patched, changed = patch_text(original)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    has_patch = PATCH_MARKER in patched and "] if _is_cloud else []" in patched
    if args.check:
        print(f"plugin_file={path}")
        print(f"guard_patch_present={has_patch}")
        return 0 if has_patch else 1

    if not changed:
        print(f"already patched: {path}")
        return 0

    if args.dry_run:
        diff = difflib.unified_diff(
            original.splitlines(True),
            patched.splitlines(True),
            fromfile=str(path),
            tofile=str(path) + " (patched)",
        )
        sys.stdout.writelines(diff)
        return 0

    backup = _backup(path)
    path.write_text(patched)
    print(f"patched: {path}")
    print(f"backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

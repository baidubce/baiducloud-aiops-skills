#!/usr/bin/env bash
# 解析当前平台的 cce-agent CLI 路径，成功时把绝对路径打到 stdout。
# 用法：export CCE="$(bash scripts/cce-agent-env.sh)"
# 查找顺序：CCE_AGENT_BIN -> PATH 上的 cce-agent -> $CCE_AGENT_HOME -> ~/.local/bin -> ~/.cce-agent/bin
set -euo pipefail

die() {
  for line in "$@"; do printf '%s\n' "$line" >&2; done
  exit 1
}

if [ -n "${CCE_AGENT_BIN:-}" ]; then
  [ -x "$CCE_AGENT_BIN" ] || die "CCE_AGENT_BIN=$CCE_AGENT_BIN 不存在或不可执行。"
  printf '%s\n' "$CCE_AGENT_BIN"
  exit 0
fi

if command -v cce-agent >/dev/null 2>&1; then
  command -v cce-agent
  exit 0
fi

os="$(uname -s | tr 'A-Z' 'a-z')"
arch="$(uname -m)"
case "$arch" in
  x86_64 | amd64) arch=amd64 ;;
  aarch64 | arm64) arch=arm64 ;;
esac

for dir in "${CCE_AGENT_HOME:-}" "$HOME/.local/bin" "$HOME/.cce-agent/bin"; do
  [ -n "$dir" ] || continue
  for candidate in "$dir/cce-agent" "$dir/cce-agent-${os}-${arch}"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      exit 0
    fi
  done
done

die "未找到 cce-agent CLI（当前平台：${os}-${arch}）。" \
    "本 Skill 不分发二进制，请先获取对应平台的可执行文件（见 references/usage.md「一、获取 CLI」），" \
    "然后任选一种方式让它可被发现：" \
    "  1) export CCE_AGENT_BIN=/absolute/path/to/cce-agent-${os}-${arch}" \
    "  2) 放到 PATH 上并命名为 cce-agent，例如 install -m 755 cce-agent-${os}-${arch} ~/.local/bin/cce-agent"

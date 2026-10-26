#!/usr/bin/env python3
"""BCE-signed DBSC Agent SSE client (historical entry filename retained)."""
from __future__ import annotations

import argparse
import codecs
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid

_HERE = os.path.dirname(os.path.abspath(__file__))
for _candidate in (os.path.join(_HERE, "..", "..", "_common"), _HERE):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import bce_openapi_core as _core  # noqa: E402
import requests  # noqa: E402

ENDPOINT = "http://10.143.163.25:8018"
CHAT_PATH = "/v1/ai-agent/chat/stream"
BceIamAuth = _core.BceIamAuth
load_credentials = _core.load_credentials

# 服务端会返回的错误码；只回显白名单内的 code，其余一律折叠成通用错误，避免回显任意错误页。
SAFE_ERROR_CODES = {
    "ConversationNotFound",
    "ConversationTenantRequired",
    "AuthenticationFailed",
    "IdempotencyDuplicate",
    "IdempotencyInFlight",
    "ParameterBindError",
    "TurnInProgress",
    "RateLimited",
    "ServerDraining",
    "QuotaExceeded",
    "ServiceError",
}
NO_CREDENTIALS = "DBSC 凭据不可用，请检查现有 BCE 凭据配置；勿在对话中提供密钥。"
THINKING_FLUSH_CHARS = 1000  # trpc 引擎逐字下发 thinking，按 agent 合并到约这么长再输出一条
# --background 的输出文件名；目录由 tempfile 按 TMPDIR/TEMP/TMP 选择，兼容 macOS/Linux/Windows。
OUTPUT_PREFIX, OUTPUT_SUFFIX = "dbsc-", ".ndjson"
# 已并入 result（session_id/turn_id/answer/completed）的事件，--poll 不再列入 steps。
FOLDED_EVENTS = {"session_init", "turn_init", "answer", "answer_done"}
POLL_WAIT = 10  # --poll 默认最多等待秒数，完成即提前返回；让两次播报间隔保持在 20 秒内
STEP_TEXT_LIMIT = 1200  # steps 里单段思路/工具结果最多保留的字符数，超长时保留首尾（结论常在末尾）
STEP_ARGS_LIMIT = 300  # 工具参数单段文本上限：子任务 prompt 这类长参数对播报帮助不大
STATE_SUFFIX = ".state"  # 轮询进度文件：{"seen": 已播报的事件数, "started": 发起时间}


def iter_sse(chunks):
    """Decode UTF-8 across chunks, CRLF, comments, multiline data and EOF."""
    decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    event, data = "message", []

    def lines():
        nonlocal buffer
        for chunk in chunks:
            buffer += decoder.decode(chunk)
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line.rstrip("\r")
        buffer += decoder.decode(b"", final=True)
        if buffer:
            yield buffer.rstrip("\r")
        yield ""

    for line in lines():
        if not line:
            if data:
                text = "\n".join(data)
                try:
                    value = json.loads(text)
                except ValueError:
                    value = text
                yield event, value
            event, data = "message", []
        elif not line.startswith(":"):
            field, sep, value = line.partition(":")
            if value.startswith(" "):
                value = value[1:]
            if sep and field == "event":
                event = value or "message"
            elif sep and field == "data":
                data.append(value)


def coalesce_thinking(events, limit=THINKING_FLUSH_CHARS):
    """Merge ``thinking`` deltas per agent into chunks of about ``limit`` characters.

    The trpc engine streams thinking token by token (hundreds of events per turn) and
    parallel sub-agents interleave theirs. A chunk is flushed once it reaches ``limit``,
    before any other event and at the end, so order relative to tool calls is kept.
    """
    pending = {}
    for event, data in events:
        if event == "thinking" and isinstance(data, dict) and isinstance(data.get("content"), str):
            key = (data.get("agent"), data.get("parentCallId"))
            if key in pending:
                pending[key]["content"] += data["content"]
            else:
                pending[key] = dict(data)
            if len(pending[key]["content"]) >= limit:
                yield "thinking", pending.pop(key)
            continue
        for chunk in pending.values():
            yield "thinking", chunk
        pending.clear()
        yield event, data
    for chunk in pending.values():
        yield "thinking", chunk


def safe_output(value, secrets=()):
    """Reuse field redaction, also mask credentials echoed inside SSE text."""
    value = _core.redact(value)
    if isinstance(value, str):
        value = re.sub(r"bce-auth-v1/[^\s\"<>]+", "<redacted>", value)
        for secret in secrets:
            if secret:
                value = value.replace(secret, "<redacted>")
        return value
    if isinstance(value, dict):
        return {key: safe_output(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [safe_output(item, secrets) for item in value]
    return value


def _emit(on_event, event, data, credentials):
    """Forward one event to the caller with secrets redacted."""
    if on_event:
        on_event({"event": event, "data": safe_output(data, credentials)})


def _error_code(response):
    """Return the error code from a non-2xx body only when it is on the safe list."""
    try:
        payload = response.json()
    except ValueError:
        return None
    code = payload.get("code") if isinstance(payload, dict) else None
    return code if code in SAFE_ERROR_CODES else None


def _post_stream(message, session_id, timeout, on_event, credentials):
    """POST one chat request and fold its SSE stream into a result dict.

    Never retries by itself and never executes anything the stream returns.
    """
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    result = {"status": None, "session_id": session_id, "turn_id": None, "answer": "",
              "completed": False, "errors": []}
    try:
        with requests.post(
            ENDPOINT + CHAT_PATH, json=payload,
            headers={"Accept": "text/event-stream",
                     "Content-Type": "application/json",
                     "Idempotency-Key": str(uuid.uuid4())},
            auth=BceIamAuth(credentials[0], credentials[1],
                            security_token=credentials[2]),
            stream=True, timeout=(10, timeout), allow_redirects=False,
        ) as response:
            result["status"] = response.status_code
            if not 200 <= response.status_code < 300:
                # Do not echo an arbitrary error page or request headers.
                result["errors"].append({"code": _error_code(response) or "HTTP_ERROR",
                                         "message": f"HTTP {response.status_code}"})
            elif response.headers.get("Content-Type", "").split(";")[0].strip().lower() != "text/event-stream":
                result["errors"].append({"code": "CONTENT_TYPE_ERROR",
                                         "message": "响应不是 text/event-stream"})
            else:
                for event, data in coalesce_thinking(iter_sse(response.iter_content(chunk_size=1024))):
                    _emit(on_event, event, data, credentials)
                    if data == "[DONE]":
                        result["completed"] = True
                        break
                    record = data if isinstance(data, dict) else {}
                    if event == "session_init":
                        sid = record.get("sessionId") or record.get("session_id")
                        if isinstance(sid, str) and sid:
                            result["session_id"] = sid
                    elif event == "turn_init":
                        tid = record.get("turnId")
                        if isinstance(tid, str) and tid:
                            result["turn_id"] = tid
                    elif event == "answer":
                        content = record.get("content", "") if isinstance(data, dict) else data
                        if isinstance(content, str):
                            result["answer"] += content
                    elif event == "error":
                        result["errors"].append(data)
                    elif event == "answer_done":
                        result["completed"] = True
                if not result["completed"]:
                    result["errors"].append({"code": "INCOMPLETE_STREAM",
                                             "message": "连接结束但未收到 answer_done 或 [DONE]"})
                elif not result["answer"] and not result["errors"]:
                    result["errors"].append({"code": "EMPTY_ANSWER",
                                             "message": "流结束但没有有效回答"})
    except (requests.RequestException, UnicodeError):
        result["errors"].append({"code": "STREAM_ERROR",
                                 "message": "连接、读取超时或流解码失败；已有结果可能不完整，未自动重试"})
    return safe_output(result, credentials)


def run_chat(message, *, session_id=None, timeout=600, on_event=None):
    """Ask one question, optionally continuing an existing session.

    续写语义（与 DBSC 会话中心一致）：不传 ``session_id`` 即新建会话，服务端在
    ``session_init`` 里返回会话 id；传入该 id 即续写，服务端校验「存在 + 归属当前
    租户（IAM 子账号）+ 未软删除」，否则返回 ``404 ConversationNotFound``；此时本函数
    会自动去掉 ``session_id`` 重发一次新会话，并在结果里标记 ``session_replaced``。
    """
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message 不能为空")
    if timeout <= 0:
        raise ValueError("timeout 必须大于 0")
    session_id = session_id.strip() if isinstance(session_id, str) else session_id
    credentials = load_credentials()
    result = _post_stream(message.strip(), session_id, timeout, on_event, credentials)
    if session_id and any(
        isinstance(err, dict) and err.get("code") == "ConversationNotFound"
        for err in result["errors"]
    ):
        _emit(on_event, "session_not_found",
              {"code": "SESSION_NOT_FOUND",
               "message": "上一轮会话不存在（未落库或已删除），已按新会话重发"},
              credentials)
        result = _post_stream(message.strip(), None, timeout, on_event, credentials)
        result["session_replaced"] = True
    return result


def start_background(message, session_id=None, timeout=600):
    """Re-run this CLI detached, its NDJSON stdout/stderr going to a new temp-dir file.

    For hosts that only see a command's output after it exits: returns ``(path, pid)``
    at once and the caller polls ``path`` with ``--poll``. The child gets its own
    session (POSIX) / process group (Windows) so it outlives the launching shell.
    """
    fd, path = tempfile.mkstemp(prefix=OUTPUT_PREFIX, suffix=OUTPUT_SUFFIX)
    argv = [sys.executable, os.path.abspath(__file__),
            "--message", message, "--timeout", str(timeout)]
    if session_id:
        argv += ["--session-id", session_id]
    if os.name == "nt":
        detach = {"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
    else:
        detach = {"start_new_session": True}
    with open(path + STATE_SUFFIX, "w", encoding="utf-8") as fh:
        json.dump({"seen": 0, "started": time.time()}, fh)
    with os.fdopen(fd, "wb") as out:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out,
                                 stderr=subprocess.STDOUT, **detach)
    return path, child.pid


def _checked_output_path(path):
    """Resolve ``path``; only ``start_background`` files in the temp dir are accepted.

    A finished file is deleted after being read, so arbitrary paths must be refused.
    """
    real = os.path.realpath(path)
    name = os.path.basename(real)
    if (os.path.normcase(os.path.dirname(real))
            != os.path.normcase(os.path.realpath(tempfile.gettempdir()))
            or not name.startswith(OUTPUT_PREFIX) or not name.endswith(OUTPUT_SUFFIX)):
        raise ValueError("只接受 --background 在系统临时目录生成的输出文件")
    return real


def _read_output(path):
    """Split a ``--background`` output file into event records and the final result."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")  # not splitlines(): answers may contain U+2028
    events, result = [], None
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue  # stderr text (warnings, tracebacks) or a half-written last line
        if isinstance(record, dict) and "result" in record:
            result = record["result"]
        elif isinstance(record, dict):
            events.append(record)
    return events, result


def _clip(value, limit=STEP_TEXT_LIMIT):
    """Shorten long strings (recursively), keeping head and tail where findings sit."""
    if isinstance(value, str):
        if len(value) <= limit:
            return value
        half = limit // 2
        return "%s…（共 %d 字，中间已省略）…%s" % (value[:half], len(value), value[-half:])
    if isinstance(value, dict):
        return {key: _clip(item, limit) for key, item in value.items()}
    if isinstance(value, list):
        return [_clip(item, limit) for item in value[:20]]
    return value


def _step(record):
    """Progress view of one non-answer event; tool-call arguments are decoded first."""
    data = record.get("data")
    if not isinstance(data, dict):
        return {"event": record.get("event"), "data": _clip(data)}
    args = data.get("arguments")
    if isinstance(args, str):
        with contextlib.suppress(ValueError):
            args = json.loads(args)
    view = _clip({key: item for key, item in data.items() if key != "arguments"})
    if "arguments" in data:
        view["arguments"] = _clip(args, STEP_ARGS_LIMIT)
    return {"event": record.get("event"), "data": view}


def _running(events):
    """Tool calls still waiting for their result, labelled by name plus their target.

    Sub-tasks are ``delegate_domain`` calls (``domain`` / ``goal``); older engines used
    ``subagent`` with a ``description``.
    """
    pending = {}
    for record in events:
        data = record.get("data")
        if not isinstance(data, dict):
            continue
        if record.get("event") == "tool_call":
            args = _step(record)["data"].get("arguments")
            label = None
            if isinstance(args, dict):
                label = args.get("description") or "，".join(
                    str(args[key]) for key in ("domain", "goal") if args.get(key))
            pending[data.get("id")] = "%s：%s" % (data.get("name"), label) if label else data.get("name")
        elif record.get("event") == "tool_result":
            pending.pop(data.get("id"), None)
    return list(pending.values())


def _same_thinker(prev, data):
    """True when two thinking payloads come from the same (sub-)agent and can be joined."""
    return (isinstance(prev, dict) and isinstance(data, dict)
            and isinstance(prev.get("content"), str) and isinstance(data.get("content"), str)
            and all(prev.get(key) == data.get(key) for key in ("agent", "parentCallId")))


def poll_background(path, wait=POLL_WAIT):
    """Wait up to ``wait`` seconds, then report what DBSC did since the previous poll.

    ``steps`` lists the new non-answer events (thinking joined per agent, steps, tool
    calls and results, clarify / confirmations, errors; long text clipped),
    ``answer_delta`` the newly streamed answer and ``running`` the tool calls /
    sub-tasks still in flight. Where the previous poll stopped is kept in
    ``<file>.state``, so callers need no cursor. Once the final ``result`` line is in
    (finishing during the wait returns at once), it is returned and both files are
    deleted.
    """
    real = _checked_output_path(path)
    deadline = time.monotonic() + wait
    events, result = _read_output(real)
    while result is None and time.monotonic() < deadline:
        time.sleep(1)
        events, result = _read_output(real)
    state_path = real + STATE_SUFFIX
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        state = None
    state = state if isinstance(state, dict) else {}
    seen = state.get("seen") if isinstance(state.get("seen"), int) else 0
    started = state.get("started") if isinstance(state.get("started"), (int, float)) else time.time()
    raw, delta = [], ""
    for record in events[seen:]:
        event, data = record.get("event"), record.get("data")
        if event == "answer":
            content = data.get("content", "") if isinstance(data, dict) else data
            delta += content if isinstance(content, str) else ""
        elif event in FOLDED_EVENTS or data == "[DONE]":
            continue
        elif (event == "thinking" and raw and raw[-1].get("event") == "thinking"
              and _same_thinker(raw[-1].get("data"), data)):
            # one thinking paragraph per agent per poll instead of a chunk per line
            merged = dict(raw[-1]["data"], content=raw[-1]["data"]["content"] + data["content"])
            raw[-1] = {"event": "thinking", "data": merged}
        else:
            raw.append(record)
    steps = [_step(record) for record in raw]
    status = {"done": result is not None, "elapsed_seconds": int(time.time() - started),
              "events": len(events), "steps": steps}
    if result is None:
        status.update(answer_delta=delta, running=_running(events))
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump({"seen": len(events), "started": started}, fh)
    else:
        status["result"] = result  # result.answer already holds the full answer
        for leftover in (real, state_path):
            with contextlib.suppress(OSError):  # Windows: the exiting child may still hold it
                os.remove(leftover)
    return status


def main(argv=None):
    """CLI 入口：解析参数、校验凭据，向 DBSC Agent 发起一次问答（或后台发起/轮询）并打印结果。"""
    _core._ensure_utf8_output()
    parser = argparse.ArgumentParser(description="DBSC Agent 流式问答（复用 BCE AK/SK 签名）")
    parser.add_argument("--message", help="用户问题；涉及变更时须先取得用户明确确认")
    parser.add_argument("--session-id", help="续写会话：上一次 session_init 返回的 session_id")
    parser.add_argument("--timeout", type=int, default=600, help="流读取空闲超时秒数（默认 600）")
    parser.add_argument("--background", action="store_true",
                        help="后台运行：NDJSON 写入系统临时目录并立即返回 output_file，再用 --poll 轮询")
    parser.add_argument("--poll", metavar="OUTPUT_FILE",
                        help="读取 --background 的输出：自上次轮询以来的新进展，或最终 result")
    parser.add_argument("--wait", type=int, default=POLL_WAIT,
                        help="--poll 最多等待秒数（默认 10），完成时提前返回")
    parser.add_argument("--check-credentials", action="store_true")
    args = parser.parse_args(argv)
    if args.check_credentials:
        configured = _core.credentials_status()["configured"]
        print(json.dumps({"configured": configured}))
        return 0 if configured else 2
    if args.poll:
        try:
            status = poll_background(args.poll, wait=max(args.wait, 0))
        except FileNotFoundError:
            status = {"error": "输出文件不存在：可能已读到 result 并删除，或路径有误"}
        except (OSError, ValueError) as exc:
            status = {"error": str(exc)}
        print(json.dumps({"poll": status}, ensure_ascii=False), flush=True)
        return 2 if "error" in status else 0
    if not args.message or not args.message.strip() or args.timeout <= 0:
        parser.error("需要非空 --message 和正数 --timeout")
    if args.background:
        if not _core.credentials_status()["configured"]:
            print(NO_CREDENTIALS, file=sys.stderr)
            return 2
        path, pid = start_background(args.message, args.session_id, args.timeout)
        print(json.dumps({"output_file": path, "pid": pid}, ensure_ascii=False), flush=True)
        return 0
    try:
        result = run_chat(
            args.message, session_id=args.session_id, timeout=args.timeout,
            on_event=lambda event: print(json.dumps(event, ensure_ascii=False), flush=True))
    except SystemExit:
        print(NO_CREDENTIALS, file=sys.stderr)
        return 2
    print(json.dumps({"result": result}, ensure_ascii=False), flush=True)
    return 0 if result["completed"] and not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

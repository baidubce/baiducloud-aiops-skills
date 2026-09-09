---
name: baiducloud-hermes-llm-monitoring
description: Configure and verify Hermes Agent observability through the bundled Langfuse plugin and internal LLM/APM monitoring endpoints. Use when the user asks to connect Hermes to LLM monitoring, APM monitoring, Langfuse, observability/langfuse, OTEL trace ingestion, standard LANGFUSE_BASE_URL endpoints, the BCM "通过 Langfuse SDK 接入" guide, the required Hermes Langfuse key-prefix guard source patch for BCM/internal Authentication tokens, trace gateways, trace push verification, or to troubleshoot missing Hermes traces, placeholder key warnings, 404 auth_check responses, plugin enablement, SDK installation, or ~/.hermes/.env observability variables.
---

# Hermes LLM Monitoring

## Overview

Use this skill to connect an installed Hermes Agent to APM monitoring through the bundled `observability/langfuse` plugin. For Baidu Cloud BCM LLM application monitoring, obtain the current access endpoint and Authentication token from the BCM console's "接入应用" page, write the endpoint as `LANGFUSE_BASE_URL` and the token as `LANGFUSE_PUBLIC_KEY` in `~/.hermes/.env`, then patch Hermes' bundled Langfuse plugin so key-prefix validation runs only for `cloud.langfuse.com`.

For fresh BCM onboarding, start with the console access-doc page:

- [LLM应用监控接入文档](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc)

If the user needs the public documentation version, use:

- BCM LLM 应用监控总览：
  https://cloud.baidu.com/doc/BCM/s/sm8zvx0qx
- [通过 Langfuse SDK 接入](https://cloud.baidu.com/doc/BCM/s/vmpcbftwt)

The console page is the primary onboarding path; the public doc is a stable backup. Together they cover the access point/token flow, SDK install step, initialization shape, and verification path before editing `~/.hermes/.env`.

Do not store real APM/Langfuse keys in this skill or in the repository. Ask users to provide keys through their shell, `~/.hermes/.env`, an approved secret store, or a redacted screenshot.

When asking the user for BCM monitoring values, use these labels exactly:

- 接入端点（`LANGFUSE_BASE_URL`）
- 接入鉴权 Token（`LANGFUSE_PUBLIC_KEY`，即 Authentication 字段）
- 应用名称（`OTEL_SERVICE_NAME`）
- 追踪用户名（`HERMES_LANGFUSE_USER_ID`）

Do not ask for or recommend `LANGFUSE_HOST` in the primary BCM flow.

## Workflow

### 1. Inspect Existing State

Run read-only checks first:

```bash
hermes --version
hermes plugins list --plain | grep -i langfuse || true
test -f ~/.hermes/.env && grep -nE 'LANGFUSE|OTEL|APM|TRACE' ~/.hermes/.env || true
tail -n 120 ~/.hermes/logs/agent.log | grep -iE 'langfuse|observability|trace|warning|error' || true
```

Mask any key values in chat output. If `hermes` is not installed or broken, use the `install-hermes` skill first.

### 2. Install SDK In Hermes venv

The SDK must be installed in Hermes' own Python environment, not the system Python:

```bash
~/.hermes/hermes-agent/venv/bin/pip install langfuse
~/.hermes/hermes-agent/venv/bin/python - <<'PY'
import langfuse
print(getattr(langfuse, "__version__", "unknown"))
PY
```

### 3. Configure Environment

> **地域匹配要求**：虚机所在地域必须与 BCM 鉴权端点的地域一致。不同地域的 endpoint 和 Authentication 不通用，使用错误地域的配置会导致鉴权失败或 trace 数据无法上报。
>
> 获取步骤：
> 1. 打开 [BCM 控制台 - LLM应用监控](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc)
> 2. 在控制台顶部切换到虚机所属地域（如华北-北京、华南-广州、华东-苏州等）
> 3. 进入「接入应用」页面，获取该地域对应的 **接入端点（endpoint）** 和 **Authentication**
> 4. 将获取到的值填入下方 `~/.hermes/.env` 配置

For BCM/internal APM/Langfuse-compatible ingestion, get the endpoint and Authentication from the official BCM "通过 Langfuse SDK 接入" guide or the console page it points to, then write this shape to `~/.hermes/.env`:

```bash
LANGFUSE_PUBLIC_KEY=<authentication> # 替换为接入点获取的Authentication
LANGFUSE_SECRET_KEY=xxx
LANGFUSE_BASE_URL=<endpoint> # 替换接入获取的endpoint

OTEL_SERVICE_NAME=<server.name> # 设置当前应用的名称
HERMES_LANGFUSE_USER_ID=xxx #设置为需要追踪的用户名
```

`LANGFUSE_SECRET_KEY` only needs to be non-empty for BCM Langfuse-compatible ingestion unless the service owner gives a specific value. Use the endpoint from the BCM console, official documentation, or the service owner.

For Langfuse Cloud, use official keys and base URL instead:

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Prefer Hermes-prefixed variables for cloud. For BCM/internal endpoints, use the standard `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` + `LANGFUSE_BASE_URL` shape. Do not require `pk-lf-` / `sk-lf-` prefixes for BCM Authentication tokens, and do not suggest `LANGFUSE_HOST` as a setup value.

### 4. Patch Hermes Langfuse Guard

For BCM/internal endpoints, patch the bundled Hermes `observability/langfuse` plugin before enabling or verifying traces. Current Hermes builds validate key prefixes before respecting the resolved base URL; BCM Authentication tokens do not use `pk-lf-` / `sk-lf-`, so the unpatched guard can set `_INIT_FAILED` and prevent Hermes session traces from sending.

Use the bundled patch script from this skill directory. It is idempotent, creates a sibling backup next to `__init__.py`, and only changes the guard so prefix validation applies when the resolved host is `cloud.langfuse.com`:

```bash
python3 scripts/patch_hermes_langfuse_guard.py
```

If Hermes is installed in a non-standard location, pass the plugin file explicitly:

```bash
python3 scripts/patch_hermes_langfuse_guard.py \
  --plugin-file /usr/local/lib/hermes-agent/plugins/observability/langfuse/__init__.py
```

After patching, restart any running Hermes session. If the patch script reports that the file is already patched, continue.

### 5. Enable Plugin

```bash
hermes plugins enable observability/langfuse
hermes plugins list --plain | grep -i langfuse
```

The plugin takes effect in the next Hermes process. Restart TUI/CLI sessions after enabling or changing `.env`.

### 6. Verify Guard And Trace Push

Before testing a conversation, confirm the patched guard behavior:

```bash
python3 scripts/patch_hermes_langfuse_guard.py --check
```

Then use a short prompt that will not trigger tools:

```bash
hermes chat -q "hi"
tail -n 120 ~/.hermes/logs/agent.log | grep -iE 'langfuse|started trace|credentials look|error|warning'
```

Success signal in Hermes logs:

```text
Langfuse tracing: started trace <trace_id> ...
```

For transport-level proof, use the SDK status probe in `references/hermes-langfuse-apm.md`; it temporarily wraps the OTLP exporter at runtime and prints the actual POST URL and HTTP status. A successful endpoint should return `otel_status 200` for an SDK-built OTLP POST to the endpoint-derived `/api/public/otel/v1/traces` path, for example:

```text
<configured-apm-endpoint>/api/public/otel/v1/traces
```

## Common Misreads

- `curl <configured-apm-endpoint>` returning `404 page not found` does not prove failure. Root GET often has no route.
- `client.auth_check()` returning 404 does not prove trace ingestion failure. It checks standard Langfuse Projects API, which may not exist on an internal ingestion gateway.
- Manual `curl -X POST --data '{}'` can return `401 empty token`; the real SDK sends OTLP protobuf plus Basic auth and `x-langfuse-public-key`.
- `flush_returned` only means the SDK queue flushed locally. Use the status probe when transport certainty matters.

## Reference

Read `references/hermes-langfuse-apm.md` when diagnosing 404/401 responses, proving that OTEL export reached the internal APM gateway, reviewing the guard patch, or recovering from Hermes updates that overwrite the bundled plugin source. Use the console access-doc link above when the user wants the exact BCM onboarding flow.

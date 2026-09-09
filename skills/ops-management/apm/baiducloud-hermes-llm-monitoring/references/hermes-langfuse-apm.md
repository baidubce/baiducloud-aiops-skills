# Hermes Langfuse/APM Reference

Use this reference when the main skill needs exact commands, the required Hermes Langfuse guard patch, or transport-level verification for BCM/internal LLM monitoring.

## Official BCM Onboarding Guide

For users starting from the BCM console, the primary onboarding page is:

- [LLM应用监控接入文档](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc)

If they need the public documentation mirror, use:

- [通过 Langfuse SDK 接入](https://cloud.baidu.com/doc/BCM/s/vmpcbftwt)

These pages cover access point and Authentication token retrieval, `pip install langfuse>=3.0.0`, initialization, and verification for BCM LLM application monitoring.

## BCM / Internal Endpoint Baseline

Baidu Cloud BCM LLM application monitoring is Langfuse-protocol compatible. The official "通过 Langfuse SDK 接入" documentation says to obtain the access endpoint and Authentication from the BCM console "接入应用" page; these values vary by region and user. In Langfuse SDK environment variables:

- `LANGFUSE_PUBLIC_KEY` = BCM `Authentication`
- `LANGFUSE_SECRET_KEY` = any non-empty string such as `sk-placeholder`, unless the service owner provides a specific value
- `LANGFUSE_BASE_URL` = BCM access endpoint

User-facing prompts must ask for `接入端点（LANGFUSE_BASE_URL）`. Do not ask for `LANGFUSE_HOST` in the BCM flow.

Configuration pattern:

```bash
LANGFUSE_PUBLIC_KEY=<authentication> # 替换为接入点获取的Authentication
LANGFUSE_SECRET_KEY=xxx
LANGFUSE_BASE_URL=<endpoint> # 替换接入获取的endpoint

OTEL_SERVICE_NAME=<server.name> # 设置当前应用的名称
HERMES_LANGFUSE_USER_ID=xxx #设置为需要追踪的用户名
```

The Authentication format may not start with `pk-lf-`. Treat it as a real key if it was obtained from BCM or provided by the APM/Langfuse service owner.

Do not hard-code local test endpoints. Prefer the console-provided endpoint or the official BCM documentation.

## Required Hermes Plugin Guard Patch

For BCM/internal endpoints, apply the Hermes bundled plugin source patch even on current Hermes builds. The observed guard bug is:

1. `observability/langfuse/__init__.py` defines `pk-lf-` / `sk-lf-` expected prefixes for Langfuse keys.
2. `_get_langfuse()` validates those prefixes before gating validation on the resolved `base_url`.
3. BCM `Authentication` values, for example `yXAWhf...`, are real internal credentials but do not carry `pk-lf-` / `sk-lf-` prefixes.
4. The guard logs `credentials look like placeholders`, sets `_INIT_FAILED`, and Hermes session traces are not emitted.

The required behavior is:

1. Resolve `base_url` from `HERMES_LANGFUSE_BASE_URL`, then `LANGFUSE_BASE_URL`, then `https://cloud.langfuse.com`.
2. Apply `pk-lf-` / `sk-lf-` prefix validation only when `urlsplit(base_url).hostname == "cloud.langfuse.com"`.
3. Keep fail-open behavior: tracing errors must not block Hermes responses.

Use the bundled script from the skill directory:

```bash
python3 scripts/patch_hermes_langfuse_guard.py
python3 scripts/patch_hermes_langfuse_guard.py --check
```

For non-standard installs:

```bash
python3 scripts/patch_hermes_langfuse_guard.py \
  --plugin-file /usr/local/lib/hermes-agent/plugins/observability/langfuse/__init__.py
```

The script creates a sibling backup such as `__init__.py.bak` before writing. Re-run it after `hermes update`, reinstall, or any operation that replaces `/usr/local/lib/hermes-agent/plugins/observability/langfuse/__init__.py`.

Manual patch shape, for source review:

```diff
+from urllib.parse import urlsplit
@@
+    base_url = _env("HERMES_LANGFUSE_BASE_URL") or _env("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
+    _is_cloud = urlsplit(base_url).hostname == "cloud.langfuse.com"
     placeholder_issues = [
@@
-    ]
+    ] if _is_cloud else []
@@
-    base_url = _env("HERMES_LANGFUSE_BASE_URL") or _env("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
```

## Read-Only Diagnostics

```bash
which hermes
hermes --version
hermes plugins list --plain | grep -i langfuse || true

~/.hermes/hermes-agent/venv/bin/python - <<'PY'
import importlib.util, sys
spec = importlib.util.find_spec("langfuse")
print("langfuse_spec", spec.origin if spec else None)
if spec:
    import langfuse
    print("langfuse_version", getattr(langfuse, "__version__", "unknown"))
PY

python3 - <<'PY'
from pathlib import Path
p = Path.home() / ".hermes/.env"
for i, raw in enumerate(p.read_text(errors="replace").splitlines(), 1):
    s = raw.strip()
    if not s or s.startswith("#") or "=" not in s:
        continue
    key, value = s.split("=", 1)
    if any(x in key.upper() for x in ["LANGFUSE", "OTEL", "APM", "TRACE"]):
        value = value.strip().strip('"').strip("'")
        if any(x in key.upper() for x in ["KEY", "SECRET", "TOKEN", "AUTH", "PASSWORD"]):
            value = value[:6] + "..." + value[-4:] + f" (len={len(value)})" if value else "<empty>"
        print(f"{i}:{key}={value}")
PY
```

## Transport-Level Status Probe

This probe proves whether the SDK's OTLP export reaches the APM endpoint. It prints the real POST URL, HTTP status, and selected headers without exposing full secrets.

```bash
set -a
. ~/.hermes/.env
set +a

LANGFUSE_DEBUG=true ~/.hermes/hermes-agent/venv/bin/python - <<'PY'
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

original_export = OTLPSpanExporter._export


def debug_export(self, serialized_data, timeout_sec=None):
    response = original_export(self, serialized_data, timeout_sec)
    print("otel_post_url", getattr(self, "_endpoint", None))
    print("otel_status", response.status_code)
    print("otel_body", response.text[:500])
    headers = {}
    for key, value in self._session.headers.items():
        lower = key.lower()
        if lower in {"authorization", "x-langfuse-public-key", "content-type"}:
            headers[key] = "<present>" if lower == "authorization" else value
    print("otel_sent_headers", headers)
    return response


OTLPSpanExporter._export = debug_export

from langfuse import Langfuse

client = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    base_url=os.environ["LANGFUSE_BASE_URL"],
    debug=True,
)

with client.start_as_current_observation(name="hermes-apm-status-check", as_type="span") as span:
    span.update(input={"source": "skill"}, output="status-check")

client.flush()
print("flush_done")
PY
```

Expected success, with the URL adjusted to the configured endpoint:

```text
otel_post_url <configured-apm-endpoint>/api/public/otel/v1/traces
otel_status 200
flush_done
```

If the probe returns `401 empty token`, check whether the probe sent OTLP protobuf through the SDK. Plain `curl --data '{}'` is not equivalent.

## Endpoint Behavior Notes

| Check | Expected Meaning |
| --- | --- |
| `GET /` returns 404 | Usually normal; root route is not implemented |
| `GET /api/public/otel/v1/traces` returns 404 | Usually normal; endpoint expects POST |
| SDK OTLP POST returns 200 | Trace ingestion transport is working |
| `Langfuse.auth_check()` returns 404 | Not decisive; internal gateway may not expose Projects API |
| Hermes log has `credentials look like placeholders` | Plugin prefix guard is still blocking internal keys |
| Hermes log has `Langfuse tracing: started trace ...` | Plugin initialized and created trace state |

## Official Documentation Anchors

- BCM overview page lists LLM application monitoring and the Langfuse SDK access path under Cloud Monitoring BCM:
  https://cloud.baidu.com/doc/BCM/s/sm8zvx0qx
- BCM Langfuse SDK guide:
  https://cloud.baidu.com/doc/BCM/s/vmpcbftwt

Use the official guide for the live endpoint and Authentication acquisition path. Keep local examples only as troubleshooting evidence.

## Clean Verification

Use a short prompt so Hermes does not start tool work:

```bash
hermes chat -q "hi"
tail -n 120 ~/.hermes/logs/agent.log | grep -iE 'langfuse|started trace|credentials look|error|warning'
```

If the prompt contains words like `langfuse check`, Hermes may treat it as a work request and run search/tools, making the verification noisy.

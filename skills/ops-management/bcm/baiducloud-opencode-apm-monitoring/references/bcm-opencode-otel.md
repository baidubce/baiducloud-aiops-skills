# BCM OpenCode OTel Reference

Use this reference when the main skill needs exact BCM console routing, OpenTelemetry parameter mapping, or troubleshooting details.

## Source Baseline

Local validation confirms this OpenCode path:

1. Install `opencode`.
2. Add `@devtheops/opencode-plugin-otel` to `~/.config/opencode/opencode.json`.
3. Run `npm install @devtheops/opencode-plugin-otel --save` from `~/.config/opencode`.
4. Set `OPENCODE_ENABLE_TELEMETRY`, `OPENCODE_OTLP_ENDPOINT`, `OPENCODE_OTLP_PROTOCOL`, `OPENCODE_OTLP_HEADERS`, `OPENCODE_RESOURCE_ATTRIBUTES`, and optionally `OPENCODE_DISABLE_LOGS`.
5. Run `opencode run "say ok"` and verify in APM.

The same validation warns not to use `opencode plugin @devtheops/opencode-plugin-otel` as the installation source of truth because it may claim success without creating `node_modules`.

Official BCM documentation confirms:

- BCM APM supports standard OpenTelemetry.
- OpenTelemetry examples use protocol `http/protobuf`.
- The OTLP header shape is `Authentication=<Authentication>`.
- Endpoint and Authentication are obtained from the console `接入应用` page and vary by region/user.
- After traffic is generated, data can take about 30 seconds to appear in the application list.

## BCM Product Routing

Choose the console area based on what the user wants to observe:

| User goal | BCM area | Console route |
| --- | --- | --- |
| LLM calls, model latency, token usage, cost, call chains | LLM application monitoring | `云监控BCM -> LLM应用性能监控 -> 应用列表 -> 接入应用` |
| Generic process traces, request latency, errors, topology | APM application monitoring | `云监控BCM -> 应用性能监控 -> 应用列表 -> 新建应用` or `接入应用` |

OpenCode emits AI-agent telemetry, so prefer LLM application monitoring when the user explicitly cares about token/cost/model-call analysis.

## Parameter Mapping

| BCM/OpenTelemetry concept | OpenCode plugin environment |
| --- | --- |
| Enable telemetry | `OPENCODE_ENABLE_TELEMETRY=1` |
| BCM `接入点` | `OPENCODE_OTLP_ENDPOINT=<endpoint>` |
| Protocol | `OPENCODE_OTLP_PROTOCOL=http/protobuf` |
| BCM `Authentication` | `OPENCODE_OTLP_HEADERS=Authentication=<Authentication>` |
| Service/application name | `OPENCODE_RESOURCE_ATTRIBUTES=service.name=<name>,host.name=<host>` |
| Disable log export | `OPENCODE_DISABLE_LOGS=1` |

Keep the header key as `Authentication` unless the plugin documentation or BCM console explicitly says otherwise. The OpenClaw guide's JSON example shows lowercase `authentication`, but the BCM OpenTelemetry examples use `Authentication=<Authentication>`. Environment header strings should follow the OpenTelemetry examples.

## Config Files

Global OpenCode config:

```text
~/.config/opencode/opencode.json
```

Minimal plugin config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@devtheops/opencode-plugin-otel"]
}
```

OpenCode also loads project-level config. If a project-level `opencode.json` overrides plugins, merge the OTel plugin instead of replacing existing entries.

## Shell Setup

Prefer a quoted single-line header value:

```bash
export OPENCODE_OTLP_HEADERS="Authentication=${BCM_APM_AUTHENTICATION}"
```

Use variables to avoid writing secrets into shell history:

```bash
export BCM_APM_ENDPOINT="<endpoint-from-BCM-console>"
read -r -s BCM_APM_AUTHENTICATION
export OPENCODE_ENABLE_TELEMETRY=1
export OPENCODE_OTLP_ENDPOINT="$BCM_APM_ENDPOINT"
export OPENCODE_OTLP_PROTOCOL="http/protobuf"
export OPENCODE_OTLP_HEADERS="Authentication=$BCM_APM_AUTHENTICATION"
export OPENCODE_RESOURCE_ATTRIBUTES="service.name=opencode,host.name=$(hostname)"
export OPENCODE_DISABLE_LOGS=1
opencode run "say ok"
```

When writing persistent shell profiles, store placeholders or source a private file with restrictive permissions:

```bash
mkdir -p ~/.config/opencode
chmod 700 ~/.config/opencode
cat >> ~/.zshrc <<'EOF'
# opencode OpenTelemetry export
export OPENCODE_ENABLE_TELEMETRY=1
export OPENCODE_OTLP_ENDPOINT="${BCM_APM_ENDPOINT}"
export OPENCODE_OTLP_PROTOCOL="http/protobuf"
export OPENCODE_OTLP_HEADERS="Authentication=${BCM_APM_AUTHENTICATION}"
export OPENCODE_RESOURCE_ATTRIBUTES="service.name=opencode,host.name=$(hostname)"
export OPENCODE_DISABLE_LOGS=1
EOF
```

## Read-Only Diagnostics

```bash
opencode --version
which opencode
node --version
npm --version

python3 - <<'PY'
from pathlib import Path
import json
p = Path.home() / ".config/opencode/opencode.json"
print("config_exists", p.exists(), p)
if p.exists():
    data = json.loads(p.read_text())
    print("plugin", data.get("plugin"))
PY

test -d ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel && \
  find ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel -maxdepth 3 -type f | sort | head -50

env | grep -E '^OPENCODE_(ENABLE_TELEMETRY|OTLP|RESOURCE|DISABLE_LOGS)' | \
  sed -E 's/(Authentication=)[^, ]+/\1<redacted>/g'
```

If `opencode.json` has comments or trailing commas, `json.loads` will fail even if OpenCode tolerates the file. Inspect manually before editing.

## Verification Signals

Successful local setup:

- `opencode --version` works.
- `~/.config/opencode/opencode.json` includes `@devtheops/opencode-plugin-otel`.
- `~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel/dist/` contains `index.js` or equivalent built output.
- The current shell has all `OPENCODE_*` telemetry variables.
- `opencode run "say ok"` completes.

Successful BCM ingestion:

- Application appears under the selected BCM application list after traffic and about 30 seconds of processing delay.
- Application details show overview data.
- LLM view shows model call analysis, token analysis, LLM operation spans, or trace details when the request includes model calls.
- Trace detail attributes include model name, token consumption, or related request attributes when exported by the plugin.

## Common Failure Modes

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `dist/` directory missing | Plugin was not actually installed | Run `cd ~/.config/opencode && npm install @devtheops/opencode-plugin-otel --save` |
| `opencode plugin ...` said installed but no package exists | Known unreliable install path | Ignore that result and install with npm |
| No app in BCM after run | Wrong endpoint/Auth, plugin not loaded, no model call, or processing delay | Recheck env, run `opencode run "say ok"`, wait 30 seconds, verify console region |
| Browser or `curl <endpoint>` returns 404 | Root route or GET is not implemented | Do not treat root 404 as ingestion failure; OTLP export uses POST protobuf |
| 401 or authentication error | Wrong/missing Authentication header | Ensure `OPENCODE_OTLP_HEADERS="Authentication=<token>"` is present in the same shell that launches opencode |
| Service name is unexpected | `service.name` missing or set differently | Set `OPENCODE_RESOURCE_ATTRIBUTES="service.name=<expected>,host.name=$(hostname)"` |
| Multiple machines collapse together | Same service name and missing host identity | Include stable `host.name`, `service.instance.id`, or another distinguishing resource attribute |
| Logs are noisy or rejected | Log export unsupported or unwanted | Keep `OPENCODE_DISABLE_LOGS=1` unless the endpoint explicitly supports logs |

## Official Documentation Anchors

- BCM APM overview: https://cloud.baidu.com/doc/BCM/s/qm7cyfilr
- BCM OpenClaw observability guide: https://cloud.baidu.com/doc/BCM/s/3mmybwcw1
- BCM Python OpenTelemetry APM guide: https://cloud.baidu.com/doc/BCM/s/Vmpcdqq2k
- BCM Traceloop/OpenLLMetry guide: https://cloud.baidu.com/doc/BCM/s/tm8zur2cg
- OpenCode plugins: https://opencode.ai/docs/plugins/

Use live console values for endpoint and Authentication; examples in documentation are illustrative and may be masked.

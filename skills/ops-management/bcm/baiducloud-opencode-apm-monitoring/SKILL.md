---
name: baiducloud-opencode-apm-monitoring
description: Configure and verify OpenCode telemetry export to Baidu Cloud BCM APM (Application Performance Monitoring) through the @devtheops/opencode-plugin-otel OpenTelemetry plugin. Use when the user asks to connect opencode/OpenCode to APM monitoring, BCM cloud monitoring, OTLP/OTel trace export, OPENCODE_OTLP_* environment variables, or to troubleshoot missing opencode traces, plugin installation, endpoint/authentication headers, service names, or telemetry not appearing in the BCM console.
---

# OpenCode APM Monitoring

## Overview

Use this skill to connect an installed `opencode` CLI to Baidu Cloud BCM APM (Application Performance Monitoring) with the community `@devtheops/opencode-plugin-otel` plugin. The normal path is to install the plugin in `~/.config/opencode`, enable it in `opencode.json`, set OTLP environment variables from the BCM console, run a short `opencode run` request, and verify traces in the BCM console.

Do not store real APM Authentication tokens or model API keys in this skill or the repository. Ask users to provide secrets through their shell, profile file, local secret store, or a redacted screenshot.

## Workflow

### 1. Inspect Existing State

Run read-only checks first:

```bash
opencode --version
which opencode
node --version
npm --version
test -f ~/.config/opencode/opencode.json && sed -n '1,200p' ~/.config/opencode/opencode.json || true
test -d ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel && \
  ls ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel/dist || true
env | grep -E '^OPENCODE_(ENABLE_TELEMETRY|OTLP|RESOURCE|DISABLE_LOGS)' | sed -E 's/(AUTH|TOKEN|KEY|PASSWORD|Authentication=)[^ ]+/\1<redacted>/g' || true
```

If `opencode` is missing, install it first:

```bash
brew install anomalyco/tap/opencode
opencode --version
```

If Homebrew is unavailable, use the official installer. If GitHub anonymous API rate limiting causes `Failed to fetch version information`, retry with an explicit version:

```bash
curl -fsSL https://opencode.ai/install | bash
curl -fsSL https://opencode.ai/install | bash -s -- --version <known-good-version>
```

### 2. Install The OTel Plugin

Enable the npm plugin in `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@devtheops/opencode-plugin-otel"]
}
```

Then install the package into the opencode config directory:

```bash
mkdir -p ~/.config/opencode
cd ~/.config/opencode
npm install @devtheops/opencode-plugin-otel --save
ls ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel/dist/
```

Do not rely on `opencode plugin @devtheops/opencode-plugin-otel`; internal validation found it can report `Installed` without placing the package in `node_modules`.

### 3. Get BCM Endpoint And Authentication

用户需要根据虚机所在地域，从 BCM 控制台获取对应地域的接入点（endpoint）和鉴权令牌（Authentication）。

> **地域匹配要求**：虚机所在地域必须与 BCM 鉴权端点的地域一致。不同地域的 endpoint 和 Authentication 不通用，使用错误地域的配置会导致鉴权失败或 trace 数据无法上报。
>
> 操作路径：
> 1. 打开 BCM 控制台
> 2. 在控制台顶部切换到虚机所属地域（如华北-北京、华南-广州、华东-苏州等）
> 3. 进入对应监控入口获取该地域的 **接入端点（endpoint）** 和 **Authentication**

获取方式参考以下文档：

- 控制台接入页面（推荐，直接获取 endpoint 和 Authentication）：
  [APM应用监控](https://console.bce.baidu.com/bcm/#/bcm/apmApplication/list) -> 应用列表 -> 新建应用/接入应用
- 公开文档（备用）：
  - BCM 应用性能监控总览：https://cloud.baidu.com/doc/BCM/s/qm7cyfilr
  - 通过 OpenTelemetry SDK 接入：https://cloud.baidu.com/doc/BCM/s/Vmpcdqq2k

操作步骤：

- Open `云监控BCM -> 应用性能监控 -> 应用列表 -> 新建应用` or `接入应用`.
  控制台直达链接：https://console.bce.baidu.com/bcm/#/bcm/apmApplication/list
- Copy the console-provided `接入点` as the OTLP endpoint.
- Copy the console-provided `Authentication` as the OTLP header value.

The endpoint and Authentication vary by region and user. Do not hard-code endpoint values; always use the values shown in the user's own BCM console for the target region.

Read `references/bcm-opencode-otel.md` before changing the endpoint/header format or diagnosing 401/404 behavior.

### 4. Configure Environment

Write the runtime environment in the user's shell profile (`~/.zshrc` for zsh, `~/.bashrc` for bash) or export it only for the current session when testing:

```bash
export OPENCODE_ENABLE_TELEMETRY=1
export OPENCODE_OTLP_ENDPOINT="<endpoint-from-BCM>"
export OPENCODE_OTLP_PROTOCOL="http/protobuf"
export OPENCODE_OTLP_HEADERS="Authentication=<Authentication-from-BCM>"
export OPENCODE_RESOURCE_ATTRIBUTES="service.name=<service-name>,host.name=$(hostname)"
export OPENCODE_DISABLE_LOGS=1
```

Use a stable `service.name`. This is the service/application name shown in the BCM application list; multiple opencode processes with the same name appear under the same service.

Prefer current-session exports when experimenting:

```bash
OPENCODE_ENABLE_TELEMETRY=1 \
OPENCODE_OTLP_ENDPOINT="<endpoint-from-BCM>" \
OPENCODE_OTLP_PROTOCOL="http/protobuf" \
OPENCODE_OTLP_HEADERS="Authentication=<Authentication-from-BCM>" \
OPENCODE_RESOURCE_ATTRIBUTES="service.name=opencode,host.name=$(hostname)" \
OPENCODE_DISABLE_LOGS=1 \
opencode run "say ok"
```

Important: After changing the OTEL configuration, start a new `opencode` conversation/session before testing or expecting traces. Existing sessions do not pick up telemetry changes retroactively.

### 5. Verify

Run a short prompt that triggers a model call:

```bash
opencode run "say ok"
```

Then check BCM:

- `云监控BCM -> 应用性能监控 -> 应用列表` -> 点击对应应用查看详情。
- Open the application details and inspect application overview, trace/call-chain pages when available.
- Wait about 30 seconds before declaring failure; BCM documentation notes processing delay after traffic is generated.

## Troubleshooting

Read `references/bcm-opencode-otel.md` for detailed diagnostics when:

- `node_modules/@devtheops/opencode-plugin-otel/dist/index.js` is missing.
- Traces do not appear after a successful `opencode run`.
- The endpoint returns 404 on a browser or plain `curl` GET.
- BCM reports authentication/token errors.
- You need to compare OpenCode plugin settings with the official BCM OpenClaw or OpenTelemetry examples.

## References

- Baidu Cloud BCM APM overview: https://cloud.baidu.com/doc/BCM/s/qm7cyfilr
- Baidu Cloud BCM OpenClaw observability guide: https://cloud.baidu.com/doc/BCM/s/3mmybwcw1
- OpenCode plugin loading guide: https://opencode.ai/docs/plugins/
- Read `references/bcm-opencode-otel.md` for endpoint/Auth acquisition, config details, and failure modes.

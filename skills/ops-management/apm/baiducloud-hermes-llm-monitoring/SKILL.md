---
name: baiducloud-hermes-llm-monitoring
description: 通过内置的 Langfuse 插件与内部 LLM/APM 监控接入点，配置并验证 Hermes Agent 的可观测能力。适用于用户需要把 Hermes 接入 LLM 监控、APM 监控、Langfuse、observability/langfuse、OTEL trace 上报、标准 LANGFUSE_BASE_URL 接入点、BCM「通过 Langfuse SDK 接入」文档、为 BCM/内部 Authentication token 打上必需的 Hermes Langfuse key 前缀校验补丁、trace 网关、trace 上报验证，或排查 Hermes trace 缺失、占位 key 告警、404 auth_check 响应、插件启用、SDK 安装、~/.hermes/.env 可观测变量等问题的场景。
---

# Hermes LLM 监控

## 概述

使用本 skill 可通过内置的 `observability/langfuse` 插件，把已安装的 Hermes Agent 接入 APM 监控。对于百度智能云 BCM 的 LLM 应用监控，需先从 BCM 控制台「接入应用」页面获取当前的接入点和 Authentication token，把接入点写入 `~/.hermes/.env` 的 `LANGFUSE_BASE_URL`、把 token 写入 `LANGFUSE_PUBLIC_KEY`，然后给 Hermes 内置的 Langfuse 插件打补丁，使 key 前缀校验只对 `cloud.langfuse.com` 生效。

首次接入 BCM 时，请从控制台的接入文档页开始：

- [LLM应用监控接入文档](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc)

如果用户需要公开文档版本，请使用：

- BCM LLM 应用监控总览：
  https://cloud.baidu.com/doc/BCM/s/sm8zvx0qx
- [通过 Langfuse SDK 接入](https://cloud.baidu.com/doc/BCM/s/vmpcbftwt)

控制台页面是主要接入路径，公开文档作为稳定的备用来源。两者合起来涵盖了接入点/token 获取流程、SDK 安装步骤、初始化写法，以及编辑 `~/.hermes/.env` 之前的验证路径。

不要把真实的 APM/Langfuse 密钥存放在本 skill 或代码仓库中。请让用户通过自己的 shell、`~/.hermes/.env`、经批准的密钥存储，或打码后的截图来提供密钥。

向用户索要 BCM 监控相关值时，请严格使用以下称谓：

- 接入端点（`LANGFUSE_BASE_URL`）
- 接入鉴权 Token（`LANGFUSE_PUBLIC_KEY`，即 Authentication 字段）
- 应用名称（`OTEL_SERVICE_NAME`）
- 追踪用户名（`HERMES_LANGFUSE_USER_ID`）

在 BCM 主流程中，不要索要或推荐 `LANGFUSE_HOST`。

## 工作流程

### 1. 检查现有状态

先执行只读检查：

```bash
hermes --version
hermes plugins list --plain | grep -i langfuse || true
test -f ~/.hermes/.env && grep -nE 'LANGFUSE|OTEL|APM|TRACE' ~/.hermes/.env || true
tail -n 120 ~/.hermes/logs/agent.log | grep -iE 'langfuse|observability|trace|warning|error' || true
```

在对话输出中要对所有密钥值做脱敏。如果 `hermes` 未安装或已损坏，请先使用 `install-hermes` skill。

### 2. 在 Hermes venv 中安装 SDK

SDK 必须安装在 Hermes 自带的 Python 环境中，而不是系统 Python：

```bash
~/.hermes/hermes-agent/venv/bin/pip install langfuse
~/.hermes/hermes-agent/venv/bin/python - <<'PY'
import langfuse
print(getattr(langfuse, "__version__", "unknown"))
PY
```

### 3. 配置环境变量

> **地域匹配要求**：虚机所在地域必须与 BCM 鉴权端点的地域一致。不同地域的 endpoint 和 Authentication 不通用，使用错误地域的配置会导致鉴权失败或 trace 数据无法上报。
>
> 获取步骤：
> 1. 打开 [BCM 控制台 - LLM应用监控](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc)
> 2. 在控制台顶部切换到虚机所属地域（如华北-北京、华南-广州、华东-苏州等）
> 3. 进入「接入应用」页面，获取该地域对应的 **接入端点（endpoint）** 和 **Authentication**
> 4. 将获取到的值填入下方 `~/.hermes/.env` 配置

对于 BCM/内部的 APM/Langfuse 兼容上报通道，请从 BCM 官方「通过 Langfuse SDK 接入」文档或其指向的控制台页面获取 endpoint 和 Authentication，然后按以下格式写入 `~/.hermes/.env`：

```bash
LANGFUSE_PUBLIC_KEY=<authentication> # 替换为接入点获取的Authentication
LANGFUSE_SECRET_KEY=xxx
LANGFUSE_BASE_URL=<endpoint> # 替换接入获取的endpoint

OTEL_SERVICE_NAME=<server.name> # 设置当前应用的名称
HERMES_LANGFUSE_USER_ID=xxx #设置为需要追踪的用户名
```

对于 BCM 的 Langfuse 兼容上报通道，除服务方另有指定值外，`LANGFUSE_SECRET_KEY` 只需保证非空即可。endpoint 请从 BCM 控制台、官方文档或服务负责人处获取。

如果接入的是 Langfuse Cloud，则应改用官方密钥和 base URL：

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

接入 Langfuse Cloud 时优先使用带 Hermes 前缀的变量；接入 BCM/内部 endpoint 时，使用标准的 `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` + `LANGFUSE_BASE_URL` 组合。不要要求 BCM Authentication token 带 `pk-lf-` / `sk-lf-` 前缀，也不要建议把 `LANGFUSE_HOST` 作为配置项。

### 4. 给 Hermes Langfuse 校验逻辑打补丁

接入 BCM/内部 endpoint 时，请在启用插件或验证 trace 之前，先给 Hermes 内置的 `observability/langfuse` 插件打补丁。当前 Hermes 版本会在采用解析出的 base URL 之前先校验 key 前缀；而 BCM Authentication token 并不使用 `pk-lf-` / `sk-lf-` 前缀，未打补丁的校验逻辑会设置 `_INIT_FAILED`，导致 Hermes 会话 trace 无法上报。

请使用本 skill 目录下自带的补丁脚本。该脚本可重复执行，会在 `__init__.py` 同级目录生成备份，且只改动校验逻辑——使前缀校验仅在解析出的 host 为 `cloud.langfuse.com` 时才生效：

```bash
python3 scripts/patch_hermes_langfuse_guard.py
```

如果 Hermes 安装在非标准路径下，请显式指定插件文件：

```bash
python3 scripts/patch_hermes_langfuse_guard.py \
  --plugin-file /usr/local/lib/hermes-agent/plugins/observability/langfuse/__init__.py
```

打完补丁后，重启所有正在运行的 Hermes 会话。如果补丁脚本提示该文件已打过补丁，直接继续后续步骤即可。

### 5. 启用插件

```bash
hermes plugins enable observability/langfuse
hermes plugins list --plain | grep -i langfuse
```

插件会在下一个 Hermes 进程中生效。启用插件或修改 `.env` 后，请重启 TUI/CLI 会话。

### 6. 验证校验逻辑与 trace 上报

在测试对话之前，先确认打补丁后的校验行为：

```bash
python3 scripts/patch_hermes_langfuse_guard.py --check
```

然后用一条不会触发工具调用的简短 prompt 测试：

```bash
hermes chat -q "hi"
tail -n 120 ~/.hermes/logs/agent.log | grep -iE 'langfuse|started trace|credentials look|error|warning'
```

Hermes 日志中的成功标志：

```text
Langfuse tracing: started trace <trace_id> ...
```

如需传输层面的确凿证据，请使用 `references/hermes-langfuse-apm.md` 中的 SDK 状态探测方法；它会在运行时临时包装 OTLP exporter，并打印真实的 POST URL 和 HTTP 状态码。endpoint 正常时，SDK 构造的 OTLP POST 请求发往由 endpoint 推导出的 `/api/public/otel/v1/traces` 路径应返回 `otel_status 200`，例如：

```text
<configured-apm-endpoint>/api/public/otel/v1/traces
```

## 常见误判

- `curl <configured-apm-endpoint>` 返回 `404 page not found` 并不能证明接入失败。根路径 GET 通常本就没有对应路由。
- `client.auth_check()` 返回 404 并不能证明 trace 上报失败。它检查的是标准 Langfuse Projects API，而内部上报网关上可能并不存在该接口。
- 手动执行 `curl -X POST --data '{}'` 可能返回 `401 empty token`；真实 SDK 发送的是 OTLP protobuf，并携带 Basic auth 和 `x-langfuse-public-key`。
- `flush_returned` 仅表示 SDK 队列在本地完成了 flush。需要确认传输是否真正成功时，请使用状态探测方法。

## 参考文档

排查 404/401 响应、验证 OTEL 数据是否真正到达内部 APM 网关、复核补丁改动，或在 Hermes 升级覆盖了内置插件源码后做恢复时，请阅读 `references/hermes-langfuse-apm.md`。当用户需要准确的 BCM 接入流程时，请使用上文的控制台接入文档链接。

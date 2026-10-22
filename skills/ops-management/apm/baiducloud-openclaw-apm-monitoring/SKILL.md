---
name: baiducloud-openclaw-apm-monitoring
description: 通过官方 diagnostics-otel 插件，配置并验证 OpenClaw 向百度智能云 BCM APM 导出遥测数据。适用于使用接入点和完整鉴权值接入已安装的 OpenClaw Gateway、启用模型和工具内容采集，或排查原生 Trace 导出问题。
---

# OpenClaw APM 监控

## 功能介绍

通过官方 `@openclaw/diagnostics-otel` 插件，将已安装且运行正常的 OpenClaw Gateway 接入百度智能云 BCM 大模型应用监控。通过 HTTP/protobuf 导出原生 Trace、模型消息、工具调用内容和 Token 用量。默认应用名称为 `openclaw`。已验证的基准版本为 **OpenClaw 2026.9.3** 及与其版本匹配的官方插件。

## 必需输入

| 用户输入 | 配置方式 |
| --- | --- |
| `endpoint` | 如果提供的是不含路径的接入点地址，则追加 `/v1/traces`。如果地址已包含路径，则将其视为完整的上报地址。将结果写入 `diagnostics.otel.tracesEndpoint`。 |
| `auth` | 将控制台或接收端提供的 **APM Authentication 原始令牌**原样写入 `diagnostics.otel.headers.Authentication`。 |

复用用户已提供的值，只询问缺失项。应用名称默认为 `openclaw`，仅在用户要求其他名称时覆盖。不要额外要求用户提供应用名称、会话 ID、用户 ID、Langfuse 公钥/私钥、AK/SK 或 Gateway 令牌。

从 [BCM 大模型应用监控接入页面](https://console.bce.baidu.com/bcm/#/bcm/llm/apmApplication/access-doc) 获取属于同一账号和目标地域的接入点与鉴权值。只向用户指定的接收端发送遥测数据。

本技能使用 **BCM 原生 OTLP Trace 接收接口：`/v1/traces`，请求头为 `Authentication`**。原样传递 APM 令牌，不要添加 `Basic` 或 `Bearer` 前缀，也不要进行 Base64 编码。`/api/public/otel` 和 `/api/public/otel/v1/traces` 属于 Langfuse 兼容接收接口，鉴权方式不同，配置脚本会拒绝这两个路径。两类接收接口均可处理大模型 Span，但本 OpenClaw 接入使用原生 OTLP。

## 写入 OpenClaw 的配置

配置由 [scripts/configure.mjs](scripts/configure.mjs) 中的 `buildPatch()` 生成，并通过 `openclaw config patch --stdin` 合并到当前生效的 OpenClaw 配置中。配置文件通常为 `~/.openclaw/openclaw.json`，但配置档案和环境变量覆盖可能改变其位置。在 Gateway 所在主机上执行以下命令，确认实际配置文件：

```bash
openclaw config file --json
```

| 配置项 | 值 | 用途 |
| --- | --- | --- |
| `plugins.entries.diagnostics-otel.enabled` | `true` | 启用官方导出插件。 |
| `diagnostics.enabled` | `true` | 启用运行时诊断事件。 |
| `diagnostics.otel.enabled` | `true` | 启用 OpenTelemetry 导出。 |
| `diagnostics.otel.tracesEndpoint` | 规范化后的用户接入点 | 设置完整的 Trace 上报地址。 |
| `diagnostics.otel.headers.Authentication` | APM 原始令牌 | 对导出请求进行鉴权。 |
| `diagnostics.otel.protocol` | `http/protobuf` | 通过 HTTP 导出 OTLP protobuf 数据。 |
| `diagnostics.otel.serviceName` | `openclaw` | 设置 APM 应用名称。 |
| `diagnostics.otel.captureContent` | `true` | 采集受大小限制且经过脱敏的模型消息、工具参数和结果。 |
| `diagnostics.otel.traces` | `true` | 导出 Trace。 |
| `diagnostics.otel.sampleRate` | `1` | 接入验证期间采样全部根 Trace。 |
| `diagnostics.otel.metrics` / `diagnostics.otel.logs` | `false` | 关闭插件额外的指标和日志信号；Trace 中仍保留 Token 属性。 |

消息和上下文内容的采集开关为 **`diagnostics.otel.captureContent`**。该配置位于 `diagnostics.otel` 下，不在插件自身的 `config` 中。它不会开启不受限制的系统提示词或内部推理内容导出。完整的 JSON 合并示例和字段说明见[配置文件与默认设置](references/openclaw-otel.md#configuration-file-and-default-settings)。

## 操作流程

### 1. 检查实例与版本

在 **Gateway 实际运行的主机或容器**中执行，使用其运行账号、配置档案、`OPENCLAW_CONFIG_PATH` 和 `OPENCLAW_STATE_DIR`。工具沙箱中的独立配置不会作用于主机上的 Gateway。

```bash
openclaw --version
node --version
openclaw config file --json
```

- 对于 **2026.9.3 或更新的稳定版本**，官方插件版本必须与已安装的核心版本完全一致。不要安装未指定版本的 `latest` 插件。
- 对于旧版本、不兼容的 Node 运行时、声明式安装或插件安装失败的情况，阅读[版本与托管安装](references/openclaw-otel.md#versions-and-managed-installations)。不要擅自降级较新版本，也不要将新插件与旧核心搭配使用。
- 在现有安装上完成配置，不创建模型账号，也不修改模型、渠道或搜索设置。

简要告知用户：接入会启用模型和工具内容采集、创建私有配置备份，并需要重启 Gateway。用户明确要求接入 APM 即授权执行这些配置操作；除非缺少实际主机权限或凭据，否则继续完成。

### 2. 运行配置脚本

脚本使用官方支持 JSON5 的配置命令行工具校验并合并修改，具体包括：

1. 将当前生效的配置备份到权限为 `0700` 的目录中，备份文件权限为 `0600`。
2. 仅在需要时安装或更新版本匹配的官方 `diagnostics-otel` 插件。
3. 启用插件，将其追加到已有允许列表，并仅移除该插件自身的禁止项。
4. 禁用已有的 `langfuse-bridge`，避免重复导出。
5. 应用上述设置，同时保留无关配置。
6. 使用提供的 `Authentication` 令牌替换遥测请求头，避免将旧接收端的凭据发送到新接入点。

**不要将鉴权值作为命令行参数传递。** 使用已有的私有文件，或通过执行工具的标准输入将其作为数据传入。如果用户只提供鉴权文本，在 Gateway 运行账号的私有目录中创建权限为 `0600` 的临时文件，并通过文件写入工具写入该值。无需让用户额外准备第三项输入。不要将鉴权值写入技能、报告、终端输出或可分享的命令中。脚本会将其持久化到权限受限的当前配置中，因此后台服务不依赖临时的 Shell 环境变量。

使用私有鉴权文件时：

```bash
node "{baseDir}/scripts/configure.mjs" \
  --endpoint '<user-endpoint>' \
  --auth-file '<private-auth-file-path>' \
  --no-restart
```

也可以使用 `--auth-stdin`，通过执行工具的标准输入提供 APM 原始令牌。如果已设置 `OPENCLAW_APM_AUTHENTICATION`，可以省略鉴权输入选项。旧环境变量 `OPENCLAW_APM_AUTHORIZATION` 仅作为备用输入，内容仍须为同一原始令牌；生成的 HTTP 请求头始终为 `Authentication`。不要将令牌插入 Shell 命令文本。操作成功后，删除本次操作创建的临时鉴权文件；保留用户已有的凭据文件。

可选执行参数：`--dry-run` 输出脱敏后的执行计划，并在插件已安装时校验配置结构；`--service-name` 覆盖应用名称；`--cli` 指定实际的 OpenClaw 可执行文件或 `openclaw.mjs` 入口。这些是执行选项，不是要求用户额外提供的必填信息。

如果用户明确要求仅采集元数据，使用参考文档中的手动合并方式设置 `captureContent=false`，不要运行默认配置脚本。仅采集元数据时，验证不应要求存在消息输入/输出内容。

### 3. 重启并检查

在 OpenClaw 会话内，优先使用可用的 Gateway 重启工具，由 Gateway 管理自身重启。重新连接后继续检查；重启导致的会话中断本身不代表配置失败。

从主机上的外部终端执行：

```bash
openclaw gateway restart
node "{baseDir}/scripts/configure.mjs" --check
```

当配置脚本在独立的主机进程中运行时，可通过 `--restart` 同时完成重启和本地检查。对于 Docker、systemd、launchd 或前台运行的 Gateway，使用现有安装方式对应的服务管理机制。不要启动第二个 Gateway。确认服务也使用受支持的 Node 运行时。

`localConfigReady=true` 表示配置、插件加载和 Gateway 健康检查均已通过。**它不能证明 APM 已收到 Trace。**

### 4. 生成真实的原生请求

```bash
node "{baseDir}/scripts/verify.mjs"
```

脚本选择已配置的默认 Agent，通过 `gateway call chat.send` 发起带有唯一标记且 `deliver=false` 的请求，因此不会向外部渠道发送消息。脚本轮询 `chat.history` 等待完成，仅输出时间戳、标记、运行 ID 和本地用量，不输出对话内容或内部推理。

这会使用现有账号发起一次真实模型请求。不要用手工构造的 Span、空 JSON POST、Langfuse `auth_check()` 或对接入点根路径的 GET 请求替代原生请求验证。请求超时后，先检查原请求，再决定是否重新提交。

### 5. 验证上报结果并汇报

可以访问 APM 控制台或查询接口时，根据应用名称 `openclaw`、测试时间和标记查找原始 Span，并验证：

- `openclaw.model.call` 包含模型名称、原始输入/输出消息、实际耗时，以及模型提供方返回的 Token 用量。
- 每个非空父 Span ID 都能在同一条 Trace 中找到对应 Span。
- `openclaw.model.usage` 是运行级汇总，不应与各次 `model.call` 用量重复累加。

如果需要验证工具调用，另行发起带有唯一标记的无害工具请求，例如执行一次 `printf`。检查工具参数、结果，以及模型消息中的 `tool_call` / `tool_call_response` 部分。详见[上报验证与已知限制](references/openclaw-otel.md#ingestion-verification-and-known-limits)。

只有接入点和鉴权值、没有查询权限时，仍应完成配置、重启和真实请求测试。汇报本地检查已通过、原生请求已完成，但 APM 接收结果尚未验证，并附上标记和时间戳。不要将另一个云账号作为接入前提，也不要在缺少接收端证据时声称已完成端到端验证。

汇报实际核心和插件版本、应用名称、配置及备份路径、重启状态、本地检查结果和 APM 接收验证状态。始终隐藏鉴权值。不要为了绕过服务端分类或页面展示问题，反复修改已经正确的原生采集设置。

## 参考文档

- [OpenClaw OTel 配置与故障排查](references/openclaw-otel.md)：完整 JSON 设置、升级、回滚、401/404 错误、输入/输出缺失、Token 重复统计和 Gateway 重启问题。
- [RAM 权限策略](references/ram-policies.md)：接收端鉴权授予上报权限；接入无需额外的云资源管理权限。

---
name: baiducloud-opencode-apm-monitoring
description: 通过 @devtheops/opencode-plugin-otel OpenTelemetry 插件，配置并验证 OpenCode 的遥测数据上报到百度智能云 BCM APM（应用性能监控）。适用于用户需要把 opencode/OpenCode 接入 APM 监控、BCM 云监控、OTLP/OTel trace 上报、配置 OPENCODE_OTLP_* 环境变量，或排查 opencode trace 数据缺失、插件安装、接入点/鉴权头、服务名称、遥测数据未出现在 BCM 控制台等问题的场景。
---

# OpenCode APM 监控

## 概述

使用本 skill 可借助社区插件 `@devtheops/opencode-plugin-otel`，把已安装的 `opencode` CLI 接入百度智能云 BCM APM（应用性能监控）。常规接入路径是：在 `~/.config/opencode` 中安装插件，在 `opencode.json` 中启用它，填入从 BCM 控制台获取的 OTLP 环境变量，执行一次简短的 `opencode run` 请求，然后在 BCM 控制台中验证 trace 数据。

不要把真实的 APM Authentication token 或模型 API Key 存放在本 skill 或代码仓库中。请让用户通过自己的 shell、profile 文件、本地密钥存储，或打码后的截图来提供密钥。

## 工作流程

### 1. 检查现有状态

先执行只读检查：

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

如果 `opencode` 尚未安装，先完成安装：

```bash
brew install anomalyco/tap/opencode
opencode --version
```

如果环境中没有 Homebrew，请改用官方安装脚本。若因 GitHub 匿名 API 限流导致报错 `Failed to fetch version information`，可指定明确版本号重试：

```bash
curl -fsSL https://opencode.ai/install | bash
curl -fsSL https://opencode.ai/install | bash -s -- --version <known-good-version>
```

### 2. 安装 OTel 插件

在 `~/.config/opencode/opencode.json` 中启用该 npm 插件：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@devtheops/opencode-plugin-otel"]
}
```

然后把插件包安装到 opencode 配置目录下：

```bash
mkdir -p ~/.config/opencode
cd ~/.config/opencode
npm install @devtheops/opencode-plugin-otel --save
ls ~/.config/opencode/node_modules/@devtheops/opencode-plugin-otel/dist/
```

不要依赖 `opencode plugin @devtheops/opencode-plugin-otel` 命令；内部验证发现它可能提示 `Installed`，但实际并未把插件包写入 `node_modules`。

### 3. 获取 BCM 接入点与鉴权 Token

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

- 打开 `云监控BCM -> 应用性能监控 -> 应用列表 -> 新建应用` 或 `接入应用`。
  控制台直达链接：https://console.bce.baidu.com/bcm/#/bcm/apmApplication/list
- 将控制台提供的 `接入点` 复制为 OTLP endpoint。
- 将控制台提供的 `Authentication` 复制为 OTLP 请求头的值。

endpoint 和 Authentication 因地域和账号而异。不要硬编码 endpoint 值，始终使用用户自己 BCM 控制台中对应目标地域所显示的值。

在调整 endpoint/请求头格式或排查 401/404 问题之前，请先阅读 `references/bcm-opencode-otel.md`。

### 4. 配置环境变量

把运行时环境变量写入用户的 shell profile 文件（zsh 用 `~/.zshrc`，bash 用 `~/.bashrc`），或在测试阶段只针对当前会话临时导出：

```bash
export OPENCODE_ENABLE_TELEMETRY=1
export OPENCODE_OTLP_ENDPOINT="<endpoint-from-BCM>"
export OPENCODE_OTLP_PROTOCOL="http/protobuf"
export OPENCODE_OTLP_HEADERS="Authentication=<Authentication-from-BCM>"
export OPENCODE_RESOURCE_ATTRIBUTES="service.name=<service-name>,host.name=$(hostname)"
export OPENCODE_DISABLE_LOGS=1
```

请使用固定的 `service.name`。它就是 BCM 应用列表中展示的服务/应用名称；多个使用相同名称的 opencode 进程会归到同一个服务下。

调试阶段建议只在当前会话中导出变量：

```bash
OPENCODE_ENABLE_TELEMETRY=1 \
OPENCODE_OTLP_ENDPOINT="<endpoint-from-BCM>" \
OPENCODE_OTLP_PROTOCOL="http/protobuf" \
OPENCODE_OTLP_HEADERS="Authentication=<Authentication-from-BCM>" \
OPENCODE_RESOURCE_ATTRIBUTES="service.name=opencode,host.name=$(hostname)" \
OPENCODE_DISABLE_LOGS=1 \
opencode run "say ok"
```

重要提示：修改 OTEL 配置后，需要新开一个 `opencode` 会话再做测试或等待 trace 数据。已存在的会话不会追溯生效新的遥测配置。

### 5. 验证

执行一条会触发模型调用的简短 prompt：

```bash
opencode run "say ok"
```

然后到 BCM 中检查：

- `云监控BCM -> 应用性能监控 -> 应用列表` -> 点击对应应用查看详情。
- 打开应用详情页，查看应用总览，以及可用的 trace/调用链页面。
- 判定失败前请等待约 30 秒；BCM 官方文档说明产生流量后存在数据处理延迟。

## 故障排查

出现以下情况时，阅读 `references/bcm-opencode-otel.md` 获取详细诊断方法：

- `node_modules/@devtheops/opencode-plugin-otel/dist/index.js` 文件缺失。
- `opencode run` 执行成功，但 trace 数据没有出现。
- 用浏览器或普通 `curl` GET 请求 endpoint 时返回 404。
- BCM 报鉴权/token 相关错误。
- 需要将 OpenCode 插件配置与 BCM 官方的 OpenClaw 或 OpenTelemetry 示例做对比。

## 参考资料

- 百度智能云 BCM APM 总览：https://cloud.baidu.com/doc/BCM/s/qm7cyfilr
- 百度智能云 BCM OpenClaw 可观测接入指南：https://cloud.baidu.com/doc/BCM/s/3mmybwcw1
- OpenCode 插件加载说明：https://opencode.ai/docs/plugins/
- endpoint/鉴权信息获取方式、配置细节与常见失败场景，详见 `references/bcm-opencode-otel.md`。

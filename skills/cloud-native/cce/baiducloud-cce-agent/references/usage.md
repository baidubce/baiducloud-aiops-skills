# CCE Agent CLI 使用说明

命令行直连百度智能云容器引擎（CCE）智能助手：用自己账号的 AK/SK 提问，云端 Agent
调用只读云 API 帮你查询和诊断集群、节点、Pod、网络与监控指标。

二进制**纯静态编译，不依赖任何运行时环境**（无需 Node、Python、glibc）。

## 一、获取 CLI

本 Skill 包**不含二进制**，只提供说明与解析脚本。先自行获取当前平台的可执行文件：

| 平台 | 构建产物名 |
| --- | --- |
| Linux x86_64 | `cce-agent-linux-amd64` |
| Linux arm64 | `cce-agent-linux-arm64` |
| macOS Intel | `cce-agent-darwin-amd64` |
| macOS Apple Silicon | `cce-agent-darwin-arm64` |
| Windows x86_64 | `cce-agent-windows-amd64.exe` |

获取途径：向 CCE Agent 服务方索取对应平台的构建产物，或从服务方提供的制品库/下载地址
获取（`<在此填入你所在环境的下载地址>`）。

拿到后任选一种方式安装，让 Skill 能发现它：

```bash
# 方式 1：装到 PATH（推荐）
install -m 755 cce-agent-linux-amd64 ~/.local/bin/cce-agent

# 方式 2：留在原地，用环境变量指路
export CCE_AGENT_BIN=/abs/path/to/cce-agent-linux-amd64
chmod +x "$CCE_AGENT_BIN"
```

之后统一用解析脚本拿路径，它会依次查 `CCE_AGENT_BIN`、`PATH`、`$CCE_AGENT_HOME`、
`~/.local/bin`、`~/.cce-agent/bin`：

```bash
export CCE="$(bash scripts/cce-agent-env.sh)"
$CCE version
```

## 二、配置

```bash
export BCE_AK=<你的 AccessKey>          # 也接受 BAIDU_AK
export BCE_SK=<你的 SecretKey>          # 也接受 BAIDU_SK
# 服务地址已内置 https://cce.su.baidubce.com，一般不用设
# export CCE_AGENT_ENDPOINT=https://cce.su.baidubce.com
```

凭证只经环境变量传入，不要写进脚本或提交到仓库。会话归属哪个账号由签名反查得出，
不需要额外填账号 ID。AK/SK 所需的最小权限见 `ram-policies.md`。

先自检：

```bash
$CCE check
# 连通正常：endpoint=https://cce.su.baidubce.com product=cce 凭证有效（可见会话 N 个）
```

## 三、提问

```bash
$CCE chat "列出我账号下的 CCE 集群，给出名称、状态和节点数"
```

回答边生成边打到 stdout；会话 ID 与工具调用提示打到 stderr：

```
[session: sess-69945e01-01cb-4d87-9946-28129446999e]

  · 正在调用 cloud_tool_search …
  · 正在调用 cce_v2_list_clusters …
```

多轮对话必须复用同一个会话，否则上下文会丢：

```bash
$CCE send sess-69945e01-01cb-4d87-9946-28129446999e "刚才那些集群里有节点 NotReady 的吗？"
# 等价写法
$CCE chat "…" --session sess-69945e01-01cb-4d87-9946-28129446999e
```

也可以先建会话再用：

```bash
SID=$($CCE new-session --name 日常巡检)
$CCE chat "苏州地域集群健康吗？" --session "$SID"
```

## 四、对话范围：集群外与集群内

范围在**建会话时**确定，取决于是否给 `--cluster-id`，之后不可更改：

| | 集群外会话（默认） | 集群内会话 |
|---|---|---|
| 建法 | `chat "…"` / `new-session` | `new-session --cluster-id cce-xxx`（或 `chat … --cluster-id`） |
| 能力 | 全部：账号级资源 + 任意集群内部资源 | 同一套工具，但只作用于锁定的那个集群 |
| 地域 | 在提问里用自然语言说，可跨地域 | 由集群本身决定，不用再说 |
| 集群 | 要查哪个集群，在提问里说出集群 ID 或名称 | 已锁定，提问里不必重复 |
| 越界 | —— | 问其它集群会被拒绝 |

集群外是超集 —— 集群内能查的它都能查，只是**地域和集群这两个定位信息要你自己在提问里
给出**。集群内把这两件事前置到会话上，适合围绕同一个集群连续排障：不用每句都重复集群 ID，
也不会误查到别的集群。

想把已有的集群外会话改成锁定集群，只能新建会话；给已存在的会话补 `clusterId` 会返回 409。

```bash
# 集群外：一个会话里换着集群和地域问
$CCE chat "列出北京地域的集群"
$CCE send <sessionId> "cce-abc12345 这个集群里有 Pod 一直 Pending 吗？"

# 集群内：锁定后专注排障
SID=$($CCE new-session --cluster-id cce-abc12345 --name Pod诊断)
$CCE chat "default 命名空间的 Pod 为什么 Pending？" --session "$SID"
```

## 五、地域怎么给

**把目标地域写进提问文本就够了**，不需要任何地域参数：

```bash
$CCE chat "查询北京地域的集群列表"
$CCE chat "对比北京和广州的集群数量"
```

服务在苏州中心化部署，但工具出口覆盖全部九个地域，所以地域是「说出来」的，不是「授权」的。
提问里不提地域时按部署默认地域（`su`）处理，Agent 通常会先反问你要查哪个地域。

`--region` / `--regions` 是两个可选开关，日常问答都不用给：

- `--region bj`：把本次提问的**默认地域**（工具出口）换成北京。它不表达查询意图 ——
  只给 `--region bj` 而提问里不提北京，仍然会被反问要查哪个地域。
- `--regions bj,gz`：把本次**允许访问的地域收紧**成这个子集，用于限制范围。传了它就必须
  同时传 `--region`，且 `--region` 属于该集合；提问里提到集合外的地域会被答「地域不在范围内」。
- 两者都与 `--cluster-id` 互斥：集群内会话的地域由集群决定。
- 可用地域：`bd bj cd fwh gz hkg nj su yq`。

## 六、命令与参数

| 命令 | 作用 |
| --- | --- |
| `check` | 凭证与连通性自检 |
| `new-session [--name N] [--cluster-id cce-xxx]` | 建会话，打印 sessionId |
| `chat "<提问>"` | 提问并流式接收回答 |
| `send <sessionId> "<提问>"` | 在已有会话里追问 |
| `sessions [--name 子串]` | 列出本账号会话 |
| `messages <sessionId>` | 列出会话内消息 |
| `runs <sessionId>` | 列出会话内历次提问 |
| `status <runId>` | 查一次提问的状态与错误码 |
| `cancel <runId>` | 取消进行中的提问 |
| `release <sessionId>` | 释放会话占用的运行环境 |
| `version` | 打印版本 |

| 参数 | 说明 |
| --- | --- |
| `--session <sessionId>` | 复用已有会话；省略则自动新建 |
| `--cluster-id cce-xxx` | 建集群内会话，锁定到该集群；只能建会话时给定 |
| `--region bj` | 可选：把本次提问的默认地域（工具出口）换成 bj |
| `--regions bj,gz` | 可选：把本次允许访问的地域收紧成该集合，需与 `--region` 同时给出 |
| `--timeout 600` | 等一次提问出结果的上限（秒） |
| `--think` | 显示思考过程与工具明细（stderr） |
| `--raw` | 原样打印每帧事件（排障） |
| `--json` | stdout 输出结构化 JSON，便于脚本解析 |
| `--endpoint <url>` | 覆盖 `CCE_AGENT_ENDPOINT` |
| `--debug` | 打印请求 URL 与签名信息（排障） |

参数与提问文本可以混排：`chat "提问" --region bj` 与 `chat --region bj "提问"` 等价。

`--json` 的输出形状：

```json
{
  "sessionId": "sess-…",
  "runId": "run-…",
  "status": "succeeded",
  "answer": "…",
  "tools": ["cce_v2_list_clusters"],
  "events": 71
}
```

退出码：成功 0；`status` 不是 `succeeded`（`failed` / `timeout`）为非 0。

## 七、耗时与并发

- 首次提问要为会话拉起运行环境，可能等数分钟，**耐心等待，不要自己加短超时反复重试**，
  否则会留下孤儿运行环境。默认上限 600 秒，可用 `--timeout` 调整。
- 同一话题的后续提问通常几十秒内返回。
- 同一账号请串行提问；并行可能触发并发限制。
- 用完主动 `release <sessionId>`，避免运行环境被长期占用。
- `Ctrl-C` 会干净退出轮询，但云端那次提问仍在跑；确实要停用 `cancel <runId>`。

## 八、排错

| 现象 | 原因与处理 |
| --- | --- |
| `未找到 cce-agent CLI` | 还没获取二进制，或没设 `CCE_AGENT_BIN` / 没放到 PATH，见「一、获取 CLI」 |
| `需要环境变量 BCE_AK / BCE_SK` | 凭证没导出，或在新 shell 里丢了 |
| `401 InvalidAuth` / `IamSignatureInvalid` | AK/SK 不对、系统时间偏差过大，或该 AK 有 IP 白名单限制 |
| `403` + `request ip not allowed` | AK 绑定了 IP 白名单，把当前出口 IP 加进去 |
| `403` + 权限不足 | AK/SK 缺少只读权限，见 `ram-policies.md` |
| `404 NotFound` | endpoint 多写了版本前缀；写到域名即可 |
| Agent 反问「要查哪个地域」 | 提问文本里没写地域，补上地域名再问 |
| 「地域不在范围内」 | 该地域没进 `--regions` 集合，或与 `--region` 不一致 |
| `status=timeout` | 用 `status <runId>` 复查真实状态，多为还在执行；必要时加大 `--timeout` |
| 看不出卡在哪 | 加 `--think` 看工具调用，或 `--raw` 看原始事件帧；`--debug` 看请求与签名 |
| 报错要找服务方 | 一并提供 `x-bce-request-id`、`sessionId`、`runId` |

## 九、卸载

```bash
rm -f ~/.local/bin/cce-agent        # 或删掉你自己放二进制的位置
unset CCE CCE_AGENT_BIN BCE_AK BCE_SK CCE_AGENT_ENDPOINT
```

## 十、边界

- 云端 Agent **只读**，不会修改云上资源；变更操作请走控制台或 OpenAPI。
- 产品线固定为 `cce`（容器引擎），不可通过参数或环境变量更改。
- 通过本 CLI 发起的会话与控制台落在同一份数据，控制台里同样可见、可继续。




---
name: baiducloud-cce-agent
description: 用百度智能云账号的 AK/SK 调用容器引擎 CCE 的智能助手（CCE Agent），让本 agent 能查询与诊断该账号下的 CCE 集群、节点、Pod、网络与监控指标——包括列集群、看集群/节点健康、排查 Pod Pending 或 CrashLoop、查 CProm 指标、解读 K8s 事件。触发词：「用 CCE 助手查/诊断」「查一下我的 CCE 集群」「容器引擎智能助手」「call cce agent」，以及任何需要以某个百度云账号身份获取真实 CCE 云上信息的场景。产品线固定为 cce。
---

# CCE 智能助手（CCE Agent）客户端

把「查询和诊断百度智能云容器引擎（CCE）」这件事交给云端的 CCE Agent 来做：本 skill
用你提供的 AK/SK 调用它的对外 API，发起一次真实的云端会话，拿回结论。

云端 Agent 拥有 CCE 领域的排查知识和只读云 API 工具集（集群、节点、Pod、VPC、
CProm 指标等），因此**不要自己猜测或编造云上事实** —— 需要真实数据时走本 skill。
通过本 skill 发起的会话与控制台落在同一份数据，在控制台里同样可见、可继续。

产品线固定为 `cce`（容器引擎），不可通过参数或环境变量更改。

## 何时使用

- 用户要查自己账号下的 CCE 资源现状：集群列表、集群/节点健康、Pod 状态、配额等。
- 用户要排查 CCE 上的具体故障：Pod 一直 Pending、容器反复重启、节点 NotReady、
  网络不通、指标异常。
- 用户要以某个云账号身份，在命令行/脚本里复现控制台智能助手的能力。

## 何时不使用

- 纯知识性问题（「CCE 的 kube-proxy 是什么模式」）且不需要读取真实资源 —— 直接回答。
- 用户问的是本 agent 自己的能力或身份 —— 直接回答，别拉起云端会话。
- 没有拿到可用 AK/SK，或用户未授权以该账号发起真实云上查询 —— 先索要凭证或确认授权，
  不要用其他账号的凭证代替。

## 前置条件

1. **凭证**：目标账号的 `BCE_AK` / `BCE_SK`（兼容 `BAIDU_AK` / `BAIDU_SK`）。
   **只经环境变量传入**，不要写进文件、不要落进对话记录、不要提交到任何仓库。会话归属
   账号由签名反查得到，不需要显式传账号 ID。凭证需要的最小 RAM 权限见
   `references/ram-policies.md`。
2. **CLI 可执行文件**：**本 skill 不分发二进制**。先按 `references/usage.md`「获取 CLI」
   拿到当前平台的 `cce-agent`（静态编译，无 Node / Python / glibc 依赖），再用
   `scripts/cce-agent-env.sh` 解析出它的路径：脚本依次查 `CCE_AGENT_BIN`、`PATH` 上的
   `cce-agent`、`$CCE_AGENT_HOME`、`~/.local/bin`、`~/.cce-agent/bin`，找不到会打印获取指引
   并以非 0 退出。
3. **服务地址**：可选。默认已内置 `https://cce.su.baidubce.com`，开箱即用；需要改用
   其他入口时设 `CCE_AGENT_ENDPOINT`，写到网关注册的路径为止（当前公网入口无额外前缀，
   写到域名即可）。**不要自己拼版本前缀**，网关对外路径必须与后端路径逐字相同，多写一段会 404。

## 对话范围：集群外与集群内

会话有两种范围，建会话时由是否给 `--cluster-id` 决定，**之后不可更改**：

| | 集群外会话（默认） | 集群内会话（`--cluster-id cce-xxx`） |
|---|---|---|
| 能力 | 全部：账号级资源 + 任意集群内部资源 | 与集群外相同的工具集，但只作用于这一个集群 |
| 地域 | 在提问里用自然语言说明，可跨地域 | 由集群本身决定，无需也不要再给地域 |
| 集群 | **要查哪个集群，得在提问里说出集群 ID 或名称** | 已锁定，提问里不用再重复 |
| 越界行为 | —— | 问到别的集群会被拒绝 |

所以集群外是超集：集群内能做的它都能做，代价是**地域和集群这两个定位信息要由你在提问
文本里给出**；集群内把这两个信息前置到会话上，换来后续提问不必反复重复、也不会误伤
其他集群。

- 默认用集群外会话，让用户在对话里自由切换集群与地域。
- 只有"接下来一连串提问都围绕同一个集群排障"时才值得建集群内会话。
- 集群外会话里再想锁集群，只能新建一个会话；对已有会话补 `clusterId` 会返回 409。

## 用法

先解析出 CLI 路径，之后所有命令都用 `$CCE` 调用：

```bash
export BCE_AK=<ak> BCE_SK=<sk>

# 解析当前平台的 cce-agent；找不到时脚本会打印获取方式
export CCE="$(bash scripts/cce-agent-env.sh)"

# 0. 首次使用先自检凭证与连通性
$CCE check

# 1. 发起一次问答（建会话 + 提问 + 流式接收 + 打印答案）
#    自动新建的会话 ID 会以 [session: sess-xxx] 打到 stderr
$CCE chat "列出我账号下北京地域的 CCE 集群，给出名称、状态和节点数"

# 2. 同一话题的追问，用上一步的 sessionId 续话（多轮上下文由服务端维持）
$CCE send <sessionId> "刚才那些集群里有节点 NotReady 的吗？"

# 3. 锁定到某个集群做诊断（集群内会话；clusterId 只能在建会话时给定，之后不可更改）
$CCE chat "default 命名空间里有 Pod 一直 Pending，帮我定位原因" \
  --cluster-id cce-xxxxxxxx --name Pod诊断

# 4. 指定地域：**只需要在提问文本里用自然语言说出地域**，不必传任何地域参数
$CCE chat "查询北京地域的集群列表"
$CCE chat "对比北京和广州的集群数量"

# 5. 结构化输出，供本 agent 解析：answer / status / tools / sessionId / runId
$CCE chat "查询集群列表" --json

# 6. 查历史（与控制台一致）
$CCE sessions
$CCE messages <sessionId>
$CCE runs <sessionId>

# 7. 中止与清理
$CCE status <runId>     # 查执行状态与错误码
$CCE cancel <runId>
$CCE release <sessionId>
```

参数与位置参数可以混排：`chat "提问" --region bj` 和 `chat --region bj "提问"` 等价。

## 输出约定

- **回答（含流式增量）走 stdout**，会话 ID、工具调用提示、重试与错误走 stderr，
  因此 `$CCE chat "…" > answer.txt` 拿到的就是干净的答案。
- `--json` 时 stdout 只有一个 JSON 对象（`sessionId` / `runId` / `status` /
  `answer` / `tools` / `events` / `error`），stderr 保持安静。
- `--think` 额外显示思考流与工具明细（stderr），`--raw` 原样打印每帧事件，二者都用于排障。
- 退出码：执行成功为 0；`status` 不是 `succeeded`（含 `failed` / `timeout`）为非 0。

## 本 agent 的使用约定

- 一次「用 CCE 助手做某事」的请求，用 `chat` 起会，**记住 stderr 上的 `sessionId`**；同一
  话题的后续追问一律用 `send <sessionId>`，否则会丢掉多轮上下文，云端也要重新查一遍。
- **地域必须用自然语言写进提问**，例如「查询北京地域的集群列表」「北京地域有节点 NotReady 吗」。
  服务在苏州中心化部署，但能出到全部九个地域，**不需要任何地域参数**：提问里说出地域就行。
  不说地域时按部署默认地域（苏州）处理，云端 Agent 通常会先反问你要查哪个地域。
  `--region` / `--regions` 只是两个可选开关：`--region` 换掉本次提问的默认地域（工具出口），
  `--regions` 把本次允许访问的地域**收紧**成一个子集（传了它就必须同时传 `--region` 且
  取值属于该集合）。日常问答两个都不用给。
- 需要程序化判断成败时用 `--json`：`status` 取 `succeeded` / `failed` / `timeout`，
  `answer` 是最终回答，`tools` 是本轮调用过的工具名。
- 把云端 Agent 的结论**原样转达**给用户，不要改写成自己的判断，也不要声称是自己直接
  查到的。云端答案里的数字和资源名不要二次加工。
- 云端 Agent 只读、不改云上资源。用户要求变更操作时，转达为「本通道只支持查询与诊断」。
- 一次提问默认最多等 600 秒（`--timeout` 可调）。首次建会话要拉起运行环境，可能等数分钟；
  **不要自己加短超时重试**，否则会留下孤儿运行环境。诊断类问题几十秒属正常。
- 同一账号不要并行发起多个提问，可能触发并发限制；串行执行。
- 用完主动 `release <sessionId>`，把运行环境还回去。
- 报错时把 `x-bce-request-id`、`sessionId`、`runId` 一并交给用户或服务方，便于定位。

## 更多细节

- `references/usage.md`：面向人的完整说明（获取 CLI、平台矩阵、命令与参数、排错表）。
- `references/api.md`：接口清单、签名细节、事件语义、地域与作用域规则、错误码。
- `references/ram-policies.md`：AK/SK 所需的最小 RAM 权限与推荐 policy。



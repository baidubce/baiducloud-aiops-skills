# CCE Agent 对外 API 参考

本客户端（`cce-agent` CLI，获取方式见 `usage.md`）调用的是 CCE Agent 的对外 HTTP API，与容器引擎
控制台里的智能助手是**同一套接口、同一份数据**：用你自己的 AK/SK 发起的会话，在控制台
里同样可见、可继续对话。

产品线固定为 `cce`（容器引擎），由客户端以 `X-Agent-Source: cce` 写死，不可更改。

## 鉴权

每个请求都带百度智能云标准的 BCE authentication v1 签名：

```
Authorization: bce-auth-v1/<AK>/<UTC 时间戳>/<有效期秒>/host/<签名>
```

- 签名算法 HMAC-SHA256，**签名头只覆盖 `host`**。因此请求实际发出时的 `Host` 头必须与
  参与签名的 host 完全一致；中间若有代理改写 Host，签名必然失效。
- 时间戳是 UTC ISO8601（秒级），默认有效期 1800 秒；本机时钟偏差过大会导致 401。
- 会话的归属账号由签名反查得到，**不需要也不要在请求里显式传账号 ID**。
- `X-Agent-Source` 必填，本场景恒为 `cce`；缺失或取值非法返回 400。

## 地址与路径

`CCE_AGENT_ENDPOINT` 填到 API 网关为这些接口注册的路径为止。当前公网入口没有额外前缀，
写到域名即可：

```
https://cce.su.baidubce.com
```

规则是：网关对外暴露的路径必须与后端路径**逐字相同**。服务端会把收到的 path / query / host
原样送去 IAM 复验签名，任何路径改写、参数改名或 Host 改写都会让请求变成 401。因此 endpoint
里不要自己拼版本前缀 —— 网关注册的是 `/sessions`，多写一段前缀会得到 404。

## 主要接口

| 操作 | 方法与路径 | 关键入参 | 返回 |
|---|---|---|---|
| 建会话 | `POST /sessions?clientToken=` | `{name?, clusterId?}` | `{sessionId, status, …}` |
| 提问并起一次执行 | `POST /sessions/{sessionId}/runs?clientToken=` | `{input:{type:"text",content}, region?, regions?, clusterId?}` | `202 {sessionId, runId, inputMessageId, status}` |
| 读事件（可断点续传） | `GET /runs/{runId}/events?afterSequence=&maxKeys=` | 与 `marker` 互斥 | `{items[], nextAfterSequence, isTruncated}` |
| 查执行状态 | `GET /runs/{runId}` | — | 含 `status` / `errorCode` |
| 列会话 | `GET /sessions?maxKeys=&name=` | 支持 marker 分页 | `{items[], nextMarker, isTruncated}` |
| 列消息 | `GET /sessions/{sessionId}/messages` | 支持分页 | `{items[]}` |
| 列历次执行 | `GET /sessions/{sessionId}/runs` | 按创建时间倒序 | `{items[]}` |
| 取消执行 | `POST /runs/{runId}/cancel` | 幂等 | `202` |
| 释放运行环境 | `POST /sessions/{sessionId}/binding/release` | 幂等 | `204` |

`clientToken` 是幂等键，必填，取值为可打印 ASCII（客户端用 UUID）。

## 会话作用域与地域

会话分两种作用域，建会话时定，之后不可改：**集群外**（不给 `clusterId`）与**集群内**
（给 `clusterId`）。两者工具集相同，集群外是超集 —— 它能查账号级资源，也能查任意集群
的内部资源，代价是地域和集群必须由提问文本给出；集群内把集群（及其地域）钉在会话上，
后续提问不必重复，越界访问其它集群会被拒绝。

- `clusterId` 是**会话级**属性，只能在建会话时给定。换集群请新建会话；在集群外会话里
  再补 `clusterId` 会被拒（409）。集群内会话与 `region` / `regions` 互斥（集群已隐含地域），
  同时给出返回 400。
- **要查哪个地域，写在提问文本里**，例如「查询北京地域的集群列表」。服务在苏州中心化
  部署，但工具出口覆盖全部九个地域，默认允许集合就是全域，因此**跨地域查询不需要任何
  地域入参**；云端 Agent 从自然语言里识别地域。
- `region` 是**本次提问的默认地域与工具出口**：它写进可信上下文，决定模型省略地域时工具
  打到哪个地域；不传就回落到服务端部署的默认地域（苏州这套是 `su`）。它**不是提示词的
  一部分** —— 只改 `region` 而提问里不提地域，Agent 仍会追问你要查哪个地域。
- `regions` 是「本次提问允许访问的地域集合」，作用是**收紧**默认的全域集合：Agent 只能在
  集合内为单次工具调用选地域。传了它就**必须**同时传 `region` 且 `region` 属于该集合，
  否则 400。省略时集合取服务端配置的默认集合（当前部署为全部九个地域）。
- 合法地域标识只有九个：`bd`(保定) `bj`(北京) `cd`(成都) `fwh`(武汉) `gz`(广州)
  `hkg`(香港) `nj`(南京) `su`(苏州) `yq`(阳泉)。提问里提到集合外的地域，Agent 会回答
  本次会话覆盖不到该地域，不会去调用工具。

## 事件流语义

`GET /runs/{runId}/events` 返回按 `sequence`（从 1 递增）持久化的事件，用
`afterSequence` 续传，保证不丢不重。需要处理的 `eventType`：

- `runtime.session.bound`：运行环境已就绪（排队 → 执行中）。
- `assistant.delta`：回答增量，文本在 `data.text`，**逐帧拼接**。
- `assistant.completed`：本段回答收尾，全文在 `data.content.text`。
- `thinking.delta` / `thinking.completed`：思考过程流，独立累积，可以不展示。
- `tool.started` / `tool.completed` / `tool.failed`：一次工具调用，名字在 `data.toolName`。
- `usage.updated`：token 用量。
- `session.state.snapshot`：内部会话快照，客户端忽略。
- **终止帧**：`run.completed`（成功）或 `error`（失败，原因在 `data.message` / `data.code`）。
  收到任一终止帧即停止轮询。

轮询之外还有 WebSocket 推送（`GET /stream`，上行 `{"type":"subscribe","runId":…,
"source":"cce","afterSequence":…}`）。轮询同样可靠且实现简单，本客户端默认走轮询；
只有对时延极敏感的场景才需要 WS。

## 排错

| 现象 | 处理 |
|---|---|
| `401 InvalidAuth` | 核对 AK/SK；同步本机时钟；确认链路上没有代理改写 `Host` |
| `400` 提示 source 非法 | 确认请求带 `X-Agent-Source: cce`（客户端已写死，一般是被中间层剥掉了） |
| `404` | `CCE_AGENT_ENDPOINT` 多写了版本前缀，或该路径没在网关注册 |
| Agent 反问「要查哪个地域」 | 提问文本里没提地域。地域要用自然语言写进提问，`region` 参数不代表查询意图 |
| `409` | 会话作用域冲突，见上文 `clusterId` 规则 |
| `429` | 触发限流/并发上限，退避重试，避免同账号并行提问 |
| `503` | 服务或身份认证依赖暂时不可用，稍后重试 |
| 长时间无事件、状态一直排队 | `GET /runs/{runId}` 看 `status` / `errorCode`，并把 `x-bce-request-id` 提供给服务方 |
| 多轮丢上下文 | 确认用的是同一个 `sessionId` 的 `send`，而不是每次 `chat` 新建会话 |

反馈问题时请提供 `x-bce-request-id`（客户端在报错时会打印）、`sessionId` 与 `runId`。

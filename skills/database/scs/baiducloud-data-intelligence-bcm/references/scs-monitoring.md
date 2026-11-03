# SCS/Redis 监控查询指南

> 只讲**云数据库 Redis（SCS）**在 BCM 上的监控取数：视图、dimensions 与例外。
> 通用 BCM 接口见 [api-reference.md](api-reference.md)，CLI 用法见 SKILL.md；
> 各对象类型的完整指标清单见 `云产品监控列表/云产品指标列表/数据库/云数据库 Redis.md`（本文不重复收录）。

## 1. scope 与产品形态

- **scope**：见 [云产品监控列表/云产品监控对象类型列表.md](云产品监控列表/云产品监控对象类型列表.md)
  （云数据库 Redis 为 `BCE_SCS`），本文不再单独维护。
- 数据源接口：`GET /json-api/v1/metricdata/{userId}/{scope}/{metricName}`，
  即 [api-reference.md](api-reference.md) 的「查询数据接口」。`{userId}` 与 scope 两段都不能省。
- `userId` 为主账号 ID，获取与降级见 SKILL.md「userId 的获取」。

产品形态由实例详情的 `engine` + `clusterType` 判定：

| 用户说法 | `engine` | `clusterType` | 形态 | 视图家族 |
| --- | --- | --- | --- | --- |
| 标准版 / 主从 / 社区版 | `redis` | `master_slave` | standard | `S*` |
| 集群版 / 企业集群 / 企业版 | `redis` | `cluster` | cluster | `C*` |
| PegaDB / 容量型 | `PegaDB` | 任意 | pegadb | `P*` |

## 2. 监控对象类型 ↔ BCM 视图映射

官方文档按**监控对象类型**组织指标，BCM 接口按**视图（view）**取数，两套编码没有现成对照表，
下表按命名与粒度推断：

| 官方监控对象类型（码） | 粒度 | 视图 | 该视图 dimensions |
| --- | --- | --- | --- |
| Redis-社区版-实例（`RD_ST_INSTANCE`） | 实例 | `SI` | `ClusterId:{id};NodeId:{hashName}` |
| Redis-社区版-只读节点（`RD_ST_NODE_RO`） | 节点 | `SN` | `ClusterId:{id};NodeId:{redis.nodeShowId}` |
| Redis-企业版-集群（`RD_CL_CLUSTER`） | 集群 | `CC` | `ClusterId:{id}` |
| Redis-企业版-分片（`RD_CL_SHARD`） | 分片 | `CS` | `ClusterId:{id};NodeId:{hashName}` |
| Redis-企业版-代理（`RD_CL_PROXY`） | 代理 | `CP` | `ClusterId:{id};NodeId:{proxy.nodeShowId}` |
| Redis-企业版-节点（官方清单无此类型） | 节点 | `CN` | `ClusterId:{id};NodeId:{redis.nodeShowId}` |
| PegaDB-企业版-集群（`PG_CL_CLUSTER`） | 集群 | `PC` | `ClusterId:{id}` |
| PegaDB-企业版-分片（`PG_CL_SHARD`） | 分片 | `PS` | `ClusterId:{id};NodeId:{hashName}` |
| PegaDB-企业版-代理（`PG_CL_PROXY`） | 代理 | `PP` | `ClusterId:{id};NodeId:{proxy.nodeShowId}` |
| PegaDB-企业版-节点（官方清单无此类型） | 节点 | `PN` | `ClusterId:{id};NodeId:{redis.nodeShowId}` |
| Memcache-集群（`MC_CLUSTER`） | 集群 | 待确认 | 待确认 |
| Memcache-分片（`MC_SHARD`） | 分片 | 待确认 | 待确认 |
| 多活组-集群（`RD_CL_SYNC_FLOW_CLUSTER`） | 集群 | 待确认 | 待确认 |
| 多活组-分片（`RD_CL_SYNC_FLOW_SHARD`） | 分片 | 待确认 | 待确认 |

两处不对齐：

- 官方 12 类里没有「企业版-节点」对象类型，但视图侧存在 `CN`/`PN`（分别为 Redis 企业版、PegaDB 企业版的节点视图，按家族命名推断）。
- Memcache 与多活组官方有、视图侧未覆盖，其指标能否经 BCM 取到未验证。

结构事实：**同一批指标在不同粒度下复用**——`RD_ST_INSTANCE`、`RD_ST_NODE_RO`、`RD_CL_SHARD`
三类在官方文档中的指标集合完全相同（75 项），区别只在 dimensions（是否带 `NodeId`、用哪个值）。
所以「某指标在不在某视图」要查视图映射，不能按对象类型的指标清单反推。

## 3. dimensions 构造

维度值是取数成败的关键，官方指标清单只给维度键、不给取值来源：

- `ClusterId:<实例ID>`
- `NodeId:<hashName>` —— 实例视图（`SI`）、分片视图（`CS`/`PS`）
- `NodeId:<redis.nodeShowId>` —— 节点视图（`SN`/`CN`/`PN`）
- `NodeId:<proxy.nodeShowId>` —— 代理视图（`CP`/`PP`）

约束：

- **只允许**实例详情返回的 `hashName`、`nodeShowId`；数字 `nodeId` 禁用。
- 拓扑无法解析时不得回退用 `InstanceId` 充当 `NodeId`，只能报无法解析。
- 多资源 dimensions 不支持：逗号拼接只会返回第一条序列，必须拒绝。
- `NodeId` 只用于内部请求，不写进对用户的输出。

## 4. 指标清单与例外

- **完整清单**：`云产品监控列表/云产品指标列表/数据库/云数据库 Redis.md`（按 12 个对象类型分组，
  含英文名、中文名、单位、维度）。
- **必须细粒度目标的指标（19 项）**：不追加正确的 `NodeId` 就取不到数值。

  ```text
  NodeMemUsedBytes      NodeNetworkInBytes    NodeNetworkOutBytes   NodeKeysNumber
  NodeIOReadBytes       NodeIOWriteBytes      NodeQueryCountPerSecond
  ProxyQueryCountPerSecond                    CmdMgetQPS            TotalCmdProcessed
  CmdReadQPS            CmdWriteQPS           CmdOtherQPS           LatencyRead
  LatencyWrite          CmdErr                LatencyMax            LatencyOther
  NodeConnectedClients
  ```

  该清单是可用性事实，不是 dimensions 推导规则；dimensions 一律以所选视图为准。

- `SlowlogLength` 例外：控制台没有集群视图页面项，但 `ClusterId` 与 `ClusterId;NodeId` 都能返回数值。
  默认仍按所选视图取细粒度，显式集群查询只作补充；不能由此推出「没有集群视图 ⇒ 集群维度无效」。
- `QPS` 是唯一中文同名双映射：集群/代理/PegaDB 类用 `QueryCountPerSecond`，
  实例/节点/分片类用 `NodeQueryCountPerSecond`，看中文「QPS」时必须先确认视图。

## 5. 取数约定

- 时间统一 `YYYY-MM-DDTHH:mm:ssZ`（UTC）；`start`/`end` 不早于当前 40 天前、不晚于当前 +2 小时，
  单次跨度最多 40 天。
- `statistics[]` 是**数组参数，名字本身带方括号**，写成 `statistics=` 会报
  `INVALID_PARAMETER: Required statistics[] parameter String[] is not present`。
- 一个 `(target, window, metric)` 只发一次请求：多个统计方式合并进**一个**
  `statistics[]=average,maximum`（默认 `average,maximum`），不要重复 `statistics[]` 键。
- **不要重复同一个 query 键**：本仓库客户端无法给重复键签名，同一个键出现两次（两个
  `statistics[]=`，甚至两个 `periodInSecond=`）会稳定返回 `403 IamSignatureInvalid`，与取值无关；
  多值必须合并进一个参数。
- 单请求最多 1441 点；period 阶梯：`≤1h→60`、`≤6h→300`、`≤24h→1200`、`≤7d→3600`、
  `≤14d→21600`、其余 `43200`。period 与 1441 点上限是两套独立约束，窗口过大时先放大 period。
- 只对 timeout/5xx 重试一次；鉴权、签名、参数错误不重试。

## 6. 结果解读

- 数值 `0` 是**有效数据**，不是「没数据」。
- 只有 timestamp 而无统计值 ≠ 该指标没有数据——也可能只是请求参数不对。
- **「该视图不适用该指标」与「本应取到而未取到」必须分开解释**：前者是确定事实，后者才是数据缺口。
- `TotalCmdProcessed` 是累积计数器，统计前必须差分，不能直接当速率。
- `*Period` 类指标的 `average` 是单个原始采样周期（约 5 秒）内的计数，`sum` 是查询 period 桶内
  原始样本之和，**两者都不是窗口总数**。
- 指标返回为空时，先确认视图/维度/层级是否正确，再判断是否平台未采集，**不要直接当成实例异常**。
- 单位/编码未定档的指标（时延族 `Latency*`、`MasterLinkStatus`、`RedisLocalCli`、`DiskIOWaitTime`、
  `MaxSlavesOffset` 等）只做同对象相对比较，不写带单位的绝对值，也不与毫秒级 SLO 直接比较。

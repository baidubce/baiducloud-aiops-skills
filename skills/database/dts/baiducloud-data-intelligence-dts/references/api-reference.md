# baiducloud-data-intelligence-dts API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:09:04+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 全局 |  | dts.baidubce.com |

## 接口目录

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [API概览](API参考/API概览.md) |  |  | 数据传输任务相关API接口概览 |
| [目录](API参考/目录.md) |  |  | 数据传输服务API文档目录与接口列表 |
| [调用说明](API参考/调用说明.md) | POST | /v{version}/task/{dtsId} | 数据传输服务API调用与请求结构说明 |

### 数据传输任务 / Demo

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [专线迁移MongoDB分片集迁移到云数据库MongoDB分片集](API参考/数据传输任务/Demo/专线迁移MongoDB分片集迁移到云数据库MongoDB分片集.md) | POST | /v1/task | 创建MongoDB分片集专线迁移任务 |
| [专线迁移MongoDB副本集迁移到云数据库MongoDB副本集-一键反向](API参考/数据传输任务/Demo/专线迁移MongoDB副本集迁移到云数据库MongoDB副本集-一键反向.md) | POST | /v1/task | 创建MongoDB副本集一键反向迁移任务 |
| [专线迁移MongoDB副本集迁移到云数据库MongoDB副本集-数据校验](API参考/数据传输任务/Demo/专线迁移MongoDB副本集迁移到云数据库MongoDB副本集-数据校验.md) | POST | /v1/task/checksum | 创建MongoDB副本集迁移数据校验任务 |
| [专线迁移MongoDB副本集迁移到云数据库MongoDB副本集](API参考/数据传输任务/Demo/专线迁移MongoDB副本集迁移到云数据库MongoDB副本集.md) | POST | /v1/task | 创建MongoDB副本集专线迁移任务 |
| [专线迁移MySQL迁移到云数据库RDS-一键反向](API参考/数据传输任务/Demo/专线迁移MySQL迁移到云数据库RDS-一键反向.md) | POST | /v1/task | 创建MySQL迁移一键反向任务 |
| [专线迁移MySQL迁移到云数据库RDS-数据校验](API参考/数据传输任务/Demo/专线迁移MySQL迁移到云数据库RDS-数据校验.md) | POST | /v1/task/checksum | 创建MySQL迁移数据校验任务 |
| [专线迁移MySQL迁移到云数据库RDS](API参考/数据传输任务/Demo/专线迁移MySQL迁移到云数据库RDS.md) | POST | /v1/task | 创建MySQL专线迁移到RDS任务 |
| [专线迁移Redis Cluster迁移到云数据库Redis企业集群版-一键反向](API参考/数据传输任务/Demo/专线迁移Redis Cluster迁移到云数据库Redis企业集群版-一键反向.md) | POST | /v1/task | 创建Redis集群一键反向迁移任务 |
| [专线迁移Redis Cluster迁移到云数据库Redis企业集群版-数据校验](API参考/数据传输任务/Demo/专线迁移Redis Cluster迁移到云数据库Redis企业集群版-数据校验.md) | POST | /v1/task/checksum | 创建Redis集群迁移数据校验任务 |
| [专线迁移Redis Cluster迁移到云数据库Redis企业集群版](API参考/数据传输任务/Demo/专线迁移Redis Cluster迁移到云数据库Redis企业集群版.md) | POST | /v1/task | 创建Redis集群专线迁移任务 |
| [专线迁移Redis Cluster迁移到云数据库Redis标准版-数据校验](API参考/数据传输任务/Demo/专线迁移Redis Cluster迁移到云数据库Redis标准版-数据校验.md) | POST | /v1/task/checksum | 创建Redis集群迁移数据校验任务 |
| [专线迁移Redis Cluster迁移到云数据库Redis标准版](API参考/数据传输任务/Demo/专线迁移Redis Cluster迁移到云数据库Redis标准版.md) | POST | /v1/task | 创建Redis集群专线迁移任务 |
| [专线迁移Redis标准版迁移到云数据库Redis标准版-一键反向](API参考/数据传输任务/Demo/专线迁移Redis标准版迁移到云数据库Redis标准版-一键反向.md) | POST | /v1/task | 创建Redis标准版一键反向迁移任务 |
| [专线迁移Redis标准版迁移到云数据库Redis标准版](API参考/数据传输任务/Demo/专线迁移Redis标准版迁移到云数据库Redis标准版.md) | POST | /v1/task | 创建Redis标准版专线迁移任务 |
| [专线迁移的MongoDB分片集迁移到云数据库MongoDB分片集-数据校验](API参考/数据传输任务/Demo/专线迁移的MongoDB分片集迁移到云数据库MongoDB分片集-数据校验.md) | POST | /v1/task/checksum | 创建MongoDB分片集数据校验任务 |
| [专线迁移的Redis标准版迁移到云数据库Redis标准版-数据校验](API参考/数据传输任务/Demo/专线迁移的Redis标准版迁移到云数据库Redis标准版-数据校验.md) | POST | /v1/task/checksum | 创建Redis标准版数据校验任务 |
| [公网sql迁移到公网kafka](API参考/数据传输任务/Demo/公网sql迁移到公网kafka.md) | POST | /v1/task | 创建公网SQL到Kafka迁移任务 |

### 数据传输任务

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改同步对象](API参考/数据传输任务/修改同步对象.md) | PUT | /v{version}/task/{dtsId} | 修改运行中任务的同步对象映射关系 |
| [修改同步对象记录](API参考/数据传输任务/修改同步对象记录.md) | POST | /v{version}/task/schema/schemaUpdateList | 查询修改同步对象的历史记录 |
| [修改模版参数](API参考/数据传输任务/修改模版参数.md) | PUT | /v{version}/task/modifyParameters/${dtsId} | 修改运行中或其他状态任务的参数 |
| [创建任务](API参考/数据传输任务/创建任务.md) | POST | /v{version}/task | 创建数据传输任务 |
| [前置检查](API参考/数据传输任务/前置检查.md) | POST | /v{version}/task/{dtsId}/precheck | 任务配置后执行前置检查 |
| [变更链路规格](API参考/数据传输任务/变更链路规格.md) | PUT | /v{version}/task/{dtsId} | 变更数据传输任务链路规格 |
| [启动任务](API参考/数据传输任务/启动任务.md) | POST | /v{version}/task/{dtsId}/start | 前置检查通过后启动任务 |
| [强制跳过预检查](API参考/数据传输任务/强制跳过预检查.md) | PUT | /v{version}/task/{dtsId} | 强制跳过任务前置检查 |
| [暂停任务](API参考/数据传输任务/暂停任务.md) | POST | /v{version}/task/{dtsId}/pause | 暂停运行中的数据传输任务 |
| [更新任务名称](API参考/数据传输任务/更新任务名称.md) | PUT | /v{version}/task/{dtsId} | 更新指定数据传输任务的名称 |
| [查询任务信息](API参考/数据传输任务/查询任务信息.md) | GET | /v{version}/task/{dtsId} | 查看指定数据传输任务的详细信息 |
| [查询任务列表](API参考/数据传输任务/查询任务列表.md) | POST | /v{version}/task/list | 查询所有数据传输任务列表 |
| [查询前置检查结果](API参考/数据传输任务/查询前置检查结果.md) | GET | /v{version}/task/{dtsId}/precheck | 查询任务启动前的前置检查结果 |
| [结束任务](API参考/数据传输任务/结束任务.md) | POST | /v{version}/task/{dtsId}/shutdown | 结束指定数据传输任务 |
| [获取参数模版](API参考/数据传输任务/获取参数模版.md) | GET | /v{version}/task/parameters | 获取任务可修改参数模版列表 |
| [获取参数模版修改历史](API参考/数据传输任务/获取参数模版修改历史.md) | GET | /v{version}/task/parameters/history | 获取任务参数模版修改历史记录 |
| [配置任务](API参考/数据传输任务/配置任务.md) | POST | /v{version}/task/{dtsId}/config |  |
| [释放任务](API参考/数据传输任务/释放任务.md) | DELETE | /v{version}/task/{dtsId} | 释放并删除已完成或已放弃的任务 |

### 数据传输任务 / 其他

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [一键反向](API参考/数据传输任务/其他/一键反向.md) | POST | /v{version}/task/{dtsId}/rollback | 启动一键反向任务并指定同步位点 |
| [一键反向延迟检查](API参考/数据传输任务/其他/一键反向延迟检查.md) | POST | /v{version}/task/{dtsId}/newRollbackCheck | 检查一键反向任务延迟情况 |
| [一键反向查询前置检查结果](API参考/数据传输任务/其他/一键反向查询前置检查结果.md) | GET | /v{version}/task/{dtsId}/rollback/precheck | 查询一键反向前置检查结果 |
| [展示授权白名单](API参考/数据传输任务/其他/展示授权白名单.md) | POST | /v{version}/task/whitelist/{dtsId} | 展示任务的授权白名单信息 |
| [查询MySQL实例拥有的账号列表](API参考/数据传输任务/其他/查询MySQL实例拥有的账号列表.md) | POST | /v{version}/task/schema/accountInfo | 查询MySQL实例拥有的账号列表 |
| [查询vpc列表](API参考/数据传输任务/其他/查询vpc列表.md) | GET | /v{version}/task/vpc | 查询指定地域下的VPC列表 |
| [查询可用区列表](API参考/数据传输任务/其他/查询可用区列表.md) | GET | /v{version}/zone_list | 查询指定地域下的可用区列表 |
| [检查数据库连通性](API参考/数据传输任务/其他/检查数据库连通性.md) | POST | /v{version}/task/check_conn | 检查数据库连接入口是否连通 |
| [绑定&解除标签](API参考/数据传输任务/其他/绑定&解除标签.md) | PUT | /v{version}/task/tag/assign | 为资源绑定或解除标签 |
| [获取订单状态](API参考/数据传输任务/其他/获取订单状态.md) | GET | /v{version}/task/order/{orderId} | 通过订单ID获取订单状态 |
| [配置一键反向](API参考/数据传输任务/其他/配置一键反向.md) | POST | /v{version}/task/{taskId}/newRollback/config | 配置一键反向任务并触发前置检查 |

### 数据传输任务 / 数据校验

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [停止校验](API参考/数据传输任务/数据校验/停止校验.md) | POST | /v{version}/task/checksum/{dtsCheckId}/shutdown | 停止正在运行的数据校验任务 |
| [创建数据校验任务](API参考/数据传输任务/数据校验/创建数据校验任务.md) | POST | /v{version}/task/checksum | 创建新的数据校验任务 |
| [数据校验任务启动](API参考/数据传输任务/数据校验/数据校验任务启动.md) | POST | /v{version}/task/checksum/{dtsCheckId}/start | 启动已配置的数据校验任务 |
| [数据校验前置检查](API参考/数据传输任务/数据校验/数据校验前置检查.md) | POST | /v{version}/task/checksum/{dtsCheckId}/precheck | 对数据校验任务执行前置检查 |
| [查看数据校验任务信息](API参考/数据传输任务/数据校验/查看数据校验任务信息.md) | GET | /v{version}/task/checksum/{dtsCheckId}/detail | 查看指定数据校验任务的详细信息 |
| [查看数据校验比对结果](API参考/数据传输任务/数据校验/查看数据校验比对结果.md) | POST | /v{version}/task/checksum/{dtsCheckId}/result | 查看数据校验任务的比对结果 |
| [查询数据校验任务列表](API参考/数据传输任务/数据校验/查询数据校验任务列表.md) | POST | /v{version}/task/checksum/{dtsId}/list | 查询关联迁移任务的数据校验任务列表 |
| [配置数据校验任务](API参考/数据传输任务/数据校验/配置数据校验任务.md) | POST | /v{version}/task/checksum/{dtsCheckId}/config | 配置数据校验任务的连接等参数 |

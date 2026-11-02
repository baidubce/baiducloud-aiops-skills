# baiducloud-data-intelligence-mongodb API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:10:50+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 北京 | bj | mongodb.bj.baidubce.com |
| 广州 | gz | mongodb.gz.baidubce.com |
| 苏州 | su | mongodb.su.baidubce.com |
| 保定 | bd | mongodb.bd.baidubce.com |
| 武汉 | fwh | mongodb.fwh.baidubce.com |
| 成都 | cd | mongodb.cd.baidubce.com |

## 接口目录

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [API简介](API参考/API简介.md) |  |  | 介绍MongoDB API接口类型与服务域名 |
| [调用说明](API参考/调用说明.md) | POST | /v{version}/instance/{instanceId} | API认证机制与调用约定说明 |
| [附录](API参考/附录.md) |  |  | 对象定义与数据模型附录 |

### 其他接口说明

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [获取可用区列表](API参考/其他接口说明.md) | GET | /v{version}/zone | 查询云数据库MongoDB可用区列表 |
| [查询目录价](API参考/其他接口说明.md) | POST | /v1/price/queryCatalog | 查询副本集实例的目录价格 |

### 备份相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建备份](API参考/备份相关接口/创建备份.md) | POST | /v{version}/instance/{dbInstanceId}/backup | 为指定MongoDB实例创建备份 |
| [删除备份](API参考/备份相关接口/删除备份.md) | DELETE | /v{version}/instance/{dbInstanceId}/backup/{backupId} | 删除指定MongoDB实例的手动备份 |
| [更改备份备注](API参考/备份相关接口/更改备份备注.md) | PUT | /v{version}/instance/{dbInstanceId}/backup/{backupId} | 修改指定备份的备注信息 |
| [更改备份策略](API参考/备份相关接口/更改备份策略.md) | PUT | /v{version}/instance/{dbInstanceId}/backupPolicy | 修改实例自动备份策略与周期 |
| [查询备份列表](API参考/备份相关接口/查询备份列表.md) | GET | /v{version}/instance/{dbInstanceId}/backup | 查询指定实例的备份列表 |
| [查询备份策略](API参考/备份相关接口/查询备份策略.md) | GET | /v{version}/instance/{dbInstanceId}/backupPolicy | 查询指定实例的备份策略 |
| [查询备份详情](API参考/备份相关接口/查询备份详情.md) | GET | /v{version}/instance/{dbInstanceId}/backup/{backupId} | 查询指定备份的详细信息 |

### 实例相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改账号密码](API参考/实例相关接口/修改账号密码.md) | PUT | /v{version}/instance/{dbInstanceId} | 修改MongoDB实例账号密码 |
| [分片集实例组件主从切换](API参考/实例相关接口/分片集实例组件主从切换.md) | PUT | /v{version}/instance/{dbInstanceId}/node/{nodeId} | 对分片集实例组件执行主从切换 |
| [创建分片集实例](API参考/实例相关接口/创建分片集实例.md) | POST | /v{version}/instance | 创建MongoDB分片集实例 |
| [创建副本集实例](API参考/实例相关接口/创建副本集实例.md) | POST | /v{version}/instance | 创建MongoDB副本集实例 |
| [副本集实例主从切换](API参考/实例相关接口/副本集实例主从切换.md) | PUT | /v{version}/instance/{dbInstanceId} | 对副本集实例执行主从切换 |
| [副本集实例添加只读节点](API参考/实例相关接口/副本集实例添加只读节点.md) | PUT | /v{version}/instance/{dbInstanceId} | 为三节点副本集实例添加只读节点 |
| [分片集实例组件改配](API参考/实例相关接口/变更分片集实例配置.md) | PUT | /v{version}/instance/{dbInstanceId}/node/{nodeId} | 为分片集实例组件变更配置 |
| [变更副本集实例配置](API参考/实例相关接口/变更副本集实例配置.md) | PUT | /v{version}/instance/{dbInstanceId} | 变更副本集实例的CPU内存存储配置 |
| [回收站和释放实例](API参考/实例相关接口/回收站和释放实例.md) | DELETE | /v{version}/instance/{dbInstanceId} | 将实例放入回收站并释放资源 |
| [小版本升级](API参考/实例相关接口/小版本升级.md) | PUT | /v1/instance/{instanceId} | 将实例内核升级到最新小版本 |
| [新增分片集实例组件](API参考/实例相关接口/新增分片集实例组件.md) | POST | /v{version}/instance/{dbInstanceId}/node | 为分片集实例新增Mongos或Shard组件 |
| [更改分片集实例组件名称](API参考/实例相关接口/更改分片集实例组件名称.md) | PUT | /v{version}/instance/{dbInstanceId}/node/{nodeId} | 修改分片集实例组件名称 |
| [更改实例名称](API参考/实例相关接口/更改实例名称.md) | PUT | /v{version}/instance/{dbInstanceId} | 修改指定实例的名称 |
| [查询实例列表](API参考/实例相关接口/查询实例列表.md) | GET | /v{version}/instance | 查询本账号下的实例列表 |
| [查询实例详情](API参考/实例相关接口/查询实例详情.md) | GET | /v{version}/instance/{dbInstanceId} | 查询指定实例的详细信息 |
| [申请 Shard、Config Server 组件内网访问](API参考/实例相关接口/申请 Shard、Config Server 组件内网访问.md) | PUT | /v1/instance/{instanceId}/allocateNodePrivateAccess | 为分片集组件申请内网访问地址 |
| [获取只读节点列表](API参考/实例相关接口/获取只读节点列表.md) | GET | /{version}/instance/{dbInstanceId}/getReadonlyNodes | 获取副本集实例的只读节点列表 |
| [计费停服和启动服务](API参考/实例相关接口/计费停服和启动服务.md) | PUT | /{version}/instance/{dbInstanceId} | 计费停服实例或启动已停服实例 |
| [迁移可用区](API参考/实例相关接口/迁移可用区.md) | PUT | /v{version}/instance/{dbInstanceId} | 将实例迁移至其他可用区 |
| [重启分片集实例组件](API参考/实例相关接口/重启分片集实例组件.md) | PUT | /v{version}/instance/{dbInstanceId}/node/{nodeId} | 重启分片集实例的指定组件 |
| [重启实例](API参考/实例相关接口/重启实例.md) | PUT | /v{version}/instance/{dbInstanceId} | 重启数据库实例，节点轮转重启 |

### 实例相关接口 / 创建MongoDB实例前的准备

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询地域](API参考/实例相关接口/创建MongoDB实例前的准备.md) | GET | /v1/instance/flavor/availableRegionList | 查询MongoDB可用地域列表 |
| [查询AZ](API参考/实例相关接口/创建MongoDB实例前的准备.md) | POST | /v1/instance/flavor/availableZoneList | 查询指定服务类型的可用区列表 |
| [查询可购买规格](API参考/实例相关接口/创建MongoDB实例前的准备.md) | POST | /v1/instance/flavor/availableFlavorList | 查询可购买的实例规格列表 |

### 实例相关接口 / 参数模版

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询参数模板列表](API参考/实例相关接口/参数模版.md) | GET | /v{version}/instance/parameterTemplate/list | 查询参数模板列表并支持条件筛选 |
| [查询参数模板详情](API参考/实例相关接口/参数模版.md) | GET | /v{version}/instance/parameterTemplate/{templateId} | 查询指定参数模板的详细信息 |
| [创建自定义参数模板](API参考/实例相关接口/参数模版.md) | POST | /v{version}/instance/parameterTemplate | 创建自定义参数模板 |
| [更新自定义参数模板](API参考/实例相关接口/参数模版.md) | PUT | /v{version}/instance/parameterTemplate/{templateId} | 更新自定义参数模板的名称描述等 |
| [删除自定义参数模板](API参考/实例相关接口/参数模版.md) | DELETE | /v{version}/instance/parameterTemplate/{templateId} | 删除指定的自定义参数模板 |
| [查询参数模板应用记录](API参考/实例相关接口/参数模版.md) | GET | /v{version}/instance/parameterTemplate/{templateId}/applyRecord | 查询参数模板应用到实例的历史记录 |
| [应用参数模板到实例](API参考/实例相关接口/参数模版.md) | PUT | /v{version}/instance/{instanceId} | 将参数模板应用到指定实例 |

### 实例相关接口 / 标签管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [绑定/解绑标签](API参考/实例相关接口/标签管理.md) | POST | /v{version}/instance/tags | 为实例绑定或解绑标签 |
| [更新标签绑定关系](API参考/实例相关接口/标签管理.md) | PUT | /v{version}/instance/tags | 更新实例标签绑定关系，支持批量 |

### 恢复相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [库表恢复到原实例](API参考/恢复相关接口/库表恢复到原实例.md) | PUT | /v1/instance/m-OTNFIS | 将备份或时间点库表恢复到原实例 |
| [库表恢复到新实例](API参考/恢复相关接口/库表恢复到新实例.md) | POST | /v1/instance | 将源实例库表恢复到新建实例 |
| [获取可恢复的时间区间](API参考/恢复相关接口/获取可恢复的时间区间.md) | GET | /v{version}/instance/{dbInstanceId} | 获取实例可恢复的时间区间 |

### 日志管理相关接口 / 审计日志

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [开启审计日志服务](API参考/日志管理相关接口/审计日志.md) | PUT | /v1/instance/m-CH2TVe | 开启实例的审计日志服务 |
| [关闭审计日志服务](API参考/日志管理相关接口/审计日志.md) | PUT | /v1/instance/m-CH2TVe | 关闭实例的审计日志服务 |

### 日志管理相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [开通运行日志](API参考/日志管理相关接口/开通运行日志.md) | PUT | /v{version}/instance/{dbInstanceId} | 为实例开通运行日志服务 |
| [查询运行日志列表](API参考/日志管理相关接口/查询运行日志列表.md) | GET | /v{version}/instance/{dbInstanceId}/log | 查询实例指定节点的运行日志列表 |
| [查询错误日志](API参考/日志管理相关接口/查询错误日志.md) | GET | /v1/instance/{instanceId}/queryErrorLogRecords | 查询实例指定节点错误日志记录 |

### 权限管理相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建用户](API参考/权限管理相关接口/创建用户.md) | PUT | /v{version}/instance/{instanceId} | 为实例创建用户并授权数据库 |
| [创建用户数据库](API参考/权限管理相关接口/创建用户数据库.md) | PUT | /v{version}/instance/{instanceId} | 为实例创建用户数据库 |
| [删除用户](API参考/权限管理相关接口/删除用户.md) | PUT | /v{version}/instance/{instanceId} | 删除实例用户，root不可删除 |
| [删除用户数据库](API参考/权限管理相关接口/删除用户数据库.md) | PUT | /v{version}/instance/{instanceId} | 为指定MongoDB实例删除用户数据库 |
| [更新用户权限](API参考/权限管理相关接口/更新用户权限.md) | PUT | /v{version}/instance/{instanceId} | 更新MongoDB实例中用户的权限 |
| [查看用户列表](API参考/权限管理相关接口/查看用户列表.md) | GET | /v{version}/instance/{instanceId} | 查询指定MongoDB实例的所有用户信息 |
| [查看用户数据库列表](API参考/权限管理相关接口/查看用户数据库列表.md) | GET | /v{version}/instance/{instanceId} | 查询指定MongoDB实例的所有用户数据库 |

### 白名单相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [删除白名单](API参考/白名单相关接口/删除白名单.md) | PUT | /v{version}/instance/{dbInstanceId} | 为指定实例删除白名单记录 |
| [查询白名单](API参考/白名单相关接口/查询白名单.md) | GET | /v{version}/instance/{dbInstanceId} | 查询实例的白名单列表 |
| [添加白名单](API参考/白名单相关接口/添加白名单.md) | PUT | /v{version}/instance/{dbInstanceId} | 为指定实例添加白名单记录 |

### 白名单相关接口 / 安全组管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [1. 修改安全组（绑定/解绑）](API参考/白名单相关接口/安全组管理.md) | PUT | /v1/instance/{instanceId} | 修改实例安全组绑定或解绑 |
| [2. 查询白名单中的安全组列表](API参考/白名单相关接口/安全组管理.md) | GET | /v1/instance/{instanceId}/listSecurityGroupsInWhitelist | 查询实例白名单中已关联的安全组 |

### 白名单相关接口 / 白名单分组管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [1. 创建白名单分组](API参考/白名单相关接口/白名单分组管理.md) | POST | /v1/api/mongo/instance/{instanceId}/securityIpGroup | 为实例创建白名单分组 |
| [2. 更新白名单分组](API参考/白名单相关接口/白名单分组管理.md) | PUT | /v1/api/mongo/instance/{instanceId}/securityIpGroup/{uuid} | 更新实例的白名单分组 |
| [3. 删除白名单分组](API参考/白名单相关接口/白名单分组管理.md) | DELETE | /v1/api/mongo/instance/{instanceId}/securityIpGroup/{uuid} | 删除实例的白名单分组 |
| [4. 查询白名单分组列表](API参考/白名单相关接口/白名单分组管理.md) | GET | /v1/api/mongo/instance/{instanceId}/securityIpGroup | 查询实例的白名单分组列表 |

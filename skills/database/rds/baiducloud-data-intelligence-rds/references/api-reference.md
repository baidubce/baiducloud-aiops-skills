# baiducloud-data-intelligence-rds API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:11:18+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 北京 | bj | rds.bj.baidubce.com |
| 保定 | bd | rds.bd.baidubce.com |
| 广州 | gz | rds.gz.baidubce.com |
| 苏州 | su | rds.su.baidubce.com |
| 武汉 | fwh | rds.fwh.baidubce.com |
| 香港 | hkg | rds.hkg.baidubce.com |

## 接口目录

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [API概览](API参考/API概览.md) |  |  | RDS实例相关API接口导航 |
| [Sample-Code](API参考/SampleCode.md) |  |  | 查询实例列表接口示例代码 |
| [对象说明](API参考/对象说明.md) |  |  | 描述实例对象的字段含义与类型 |
| [目录](API参考/目录.md) |  |  | 云数据库RDS API目录总览 |
| [调用说明](API参考/调用说明.md) | POST | /v{version}/instance/{instanceId} | 说明API请求结构、域名与公共参数 |
| [附录](API参考/附录.md) |  |  | RDS API计费与实例套餐附录 |

### 任务管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询任务列表](API参考/任务管理/查询任务列表.md) | POST | /v1/instance/task | 查询实例任务列表 |

### 其它

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [热活实例组强切](API参考/其它/热活实例组强切.md) | PUT | /v{version}/instance/{groupId}/forceChange | 热活实例组强制切换主实例 |
| [获取可用区列表](API参考/其它/获取可用区列表.md) | GET | /v{version}/zone | 获取RDS可用区列表 |
| [获取子网列表](API参考/其它/获取子网列表.md) | GET | /v{version}/subnet | 获取VPC子网列表 |
| [获取订单状态](API参考/其它/获取订单状态.md) | GET | /v{version}/instance/order/{orderId} | 通过订单ID获取订单状态 |

### 参数管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改配置参数](API参考/参数管理/修改配置参数.md) | PUT | /v{version}/instance/{instanceId}/parameter | 修改实例参数配置 |
| [复制参数模板](API参考/参数管理/复制参数模板.md) | POST | /v{version}/instance/paraTemplate/duplicate/template | 复制参数模板 |
| [查询修改历史](API参考/参数管理/查询修改历史.md) | GET | /v{version}/instance/{instanceId}/parameter/history | 查询实例参数修改历史 |
| [查询参数列表](API参考/参数管理/查询参数列表.md) | GET | /v{version}/instance/{instanceId}/parameter | 查询实例参数列表 |
| [获取参数模板列表](API参考/参数管理/获取参数模板列表.md) | GET | /v{version}/instance/paraTemplate | 获取参数模板列表 |
| [获取参数模板详情](API参考/参数管理/获取参数模板详情.md) | GET | /v{version}/instance/paraTemplate/template/detail/{templateId} | 获取参数模板详情 |

### 只读组管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改连接信息](API参考/只读组管理/修改连接信息.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/updateEndpoint | 修改只读组连接地址端口等信息 |
| [创建只读组](API参考/只读组管理/创建只读组.md) | POST | /v{version}/rds/{sourceAppId}/rogroup | 创建只读组 |
| [删除只读组](API参考/只读组管理/删除只读组.md) | DELETE | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId} | 删除只读组 |
| [只读实例加入只读组](API参考/只读组管理/只读实例加入只读组.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/join | 只读实例加入只读组 |
| [只读实例离开只读组](API参考/只读组管理/只读实例离开只读组.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/leave | 只读实例离开只读组 |
| [只读组重新负载均衡](API参考/只读组管理/只读组重新负载均衡.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/reload | 只读组重新负载均衡 |
| [展示主实例关联的只读组列表](API参考/只读组管理/展示主实例关联的只读组列表.md) | GET | /v{version}/rds/{sourceAppId}/rogroup/list | 展示主实例关联的只读组列表 |
| [开启或关闭公网](API参考/只读组管理/开启或关闭公网.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/updatePubliclyAccessible | 开启或关闭只读组公网访问 |
| [批量修改只读组名称、延迟剔除开关、延迟阈值、重新负载均衡开关、组内只读实例权重](API参考/只读组管理/批量修改只读组名称、延迟剔除开关、延迟阈值、重新负载均衡开关、组内只读实例权重.md) | PUT | /v{version}/rds/{sourceAppId}/rogroup/{roGroupId}/updateRoGroupProperty | 批量修改只读组属性及权重 |
| [查询只读组详情](API参考/只读组管理/查询只读组详情.md) | GET | /v{version}/rds/{sourceAppId}/rogroup/detail/{roGroupId} | 查询只读组详情 |

### 回收站管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [删除单个实例](API参考/回收站管理/删除单个实例.md) | DELETE | /v{version}/instance/recycler/{instanceId} | 从回收站删除单个实例 |
| [实例开机](API参考/回收站管理/实例开机.md) | PUT | /v{version}/instance/recycler/recover | 恢复回收站中的实例 |
| [查询回收站实例列表](API参考/回收站管理/查询回收站实例列表.md) | GET | /v{version}/instance/recycler/list | 查询回收站实例列表 |

### 备份管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改备份策略](API参考/备份管理/修改备份策略.md) | PUT | /v{version}/instance/{instanceId} | 修改实例备份策略 |
| [删除指定的备份集](API参考/备份管理/删除指定的备份集.md) | DELETE | /v{version}/instance/{instanceId}/backup/{snapshotId} | 删除指定的备份集 |
| [手动发起全量的物理备份](API参考/备份管理/手动发起全量的物理备份.md) | POST | /v{version}/instance/{instanceId}/backup | 手动发起全量物理备份 |
| [按备份集进行库表恢复](API参考/备份管理/按备份集进行库表恢复.md) | PUT | /v{version}/instance/{instanceId}/recoveryToSourceInstanceBySnapshot | 按备份集恢复库表到原实例 |
| [按时间点进行库表恢复](API参考/备份管理/按时间点进行库表恢复.md) | PUT | /v{version}/instance/{instanceId}/recoveryToSourceInstanceByDatetime | 按时间点恢复库表到实例 |
| [查询备份列表](API参考/备份管理/查询备份列表.md) | GET | /v{version}/instance/{instanceId}/backup | 分页查询指定实例的备份列表 |
| [查询备份详情](API参考/备份管理/查询备份详情.md) | GET | /v{version}/instance/{instanceId}/backup/{backupId} | 查询指定备份详情及下载链接 |
| [目标地域映射列表API](API参考/备份管理/目标地域映射列表API.md) | GET | /v1/instance/{instanceId}/backup/target/region | 查询备份副本可选目标地域列表 |
| [获取binlog信息](API参考/备份管理/获取binlog信息.md) | GET | /v{version}/instance/{instanceId}/binlogs/{logId}/{downloadValidTimeInSec} | 获取指定binlog日志的详细信息 |
| [获取binlog列表](API参考/备份管理/获取binlog列表.md) | GET | /v{version}/instance/{instanceId}/binlogs/{datetime} | 查询指定时间点的binlog日志列表 |
| [设置加密策略API](API参考/备份管理/设置加密策略API.md) | PUT | /v1/instance/{instanceId} | 修改指定实例的加密策略配置 |

### 安全管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [更新白名单](API参考/安全管理/更新白名单.md) | PUT | /v{version}/instance/{instanceId}/securityIp | 全量更新实例的IP白名单列表 |
| [查询白名单](API参考/安全管理/查询白名单.md) | GET | /v{version}/instance/{instanceId}/securityIp | 查询实例的白名单分组信息 |
| [获取SSL加密信息](API参考/安全管理/获取SSL加密信息.md) | GET | /v{version}/instance/ssl/{instanceId} | 查询实例的SSL加密状态信息 |
| [获取SSL加密证书](API参考/安全管理/获取SSL加密证书.md) | GET | /v{version}/instance/ssl/static/ca | 获取SSL加密的CA证书内容 |

### 实例管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建主实例](API参考/实例管理/创建主实例.md) | POST | /v{version}/instance | 创建一个或多个相同配置的RDS实例 |
| [创建代理实例](API参考/实例管理/创建代理实例.md) | POST | /v{version}/instance | 创建RDS代理实例 |
| [创建只读实例](API参考/实例管理/创建只读实例.md) | POST | /v{version}/instance | 创建RDS只读实例 |
| [变配实例](API参考/实例管理/变配实例.md) | PUT | /v{version}/instance/{instanceId} | 变更实例的CPU、内存和存储配置 |
| [可用区迁移](API参考/实例管理/可用区迁移.md) | PUT | /v{version}/instance/{instanceId}/azoneMigration | 将实例迁移到其他可用区 |
| [实例开启自动续费](API参考/实例管理/实例开启自动续费.md) | PUT | /v{version}/instance/ | 为实例开启自动续费功能 |
| [实例批量变配](API参考/实例管理/实例批量变配.md) | PUT | /v{version}/instance/{instanceId} | 批量变配主实例与只读实例 |
| [实例是否支持启用自动扩容](API参考/实例管理/实例是否支持启用自动扩容.md) | GET | /v{version}/instance/{instanceId}/autoExpansion | 查询实例是否支持启用存储自动扩容 |
| [更新存储自动扩容配置](API参考/实例管理/更新存储自动扩容配置.md) | PUT | /v{version}/instance/{instanceId}/diskAutoResize/config/{action} | 开启关闭或修改存储自动扩容配置 |
| [更新实例公网访问状态](API参考/实例管理/更新实例公网访问状态.md) | PUT | /v{version}/instance/{instanceId} | 开启或关闭实例公网访问 |
| [更新实例同步模式](API参考/实例管理/更新实例同步模式.md) | PUT | /v{version}/instance/{instanceId} | 修改实例复制同步模式 |
| [更新实例名称](API参考/实例管理/更新实例名称.md) | PUT | /v{version}/instance/{instanceId} | 修改实例名称 |
| [更新实例连接信息](API参考/实例管理/更新实例连接信息.md) | PUT | /v{version}/instance/{instanceId} | 修改实例连接域名前缀 |
| [更新时间窗口](API参考/实例管理/更新时间窗口.md) | PUT | /v{version}/instance/{instanceId}/maintaintime | 修改实例维护时间窗口 |
| [查询可用区列表](API参考/实例管理/查询可用区列表.md) | GET | /v{version}/zone | 获取可用区列表 |
| [查询子网列表](API参考/实例管理/查询子网列表.md) | GET | /v{version}/subnet | 查询子网列表 |
| [查询实例列表](API参考/实例管理/查询实例列表.md) | GET | /v{version}/instance | 查询实例列表 |
| [查询指定实例详情](API参考/实例管理/查询指定实例详情.md) | GET | /v{version}/instance/{instanceId} | 查询指定实例详细信息 |
| [检查实例是否支持热变配](API参考/实例管理/检查实例是否支持热变配.md) | POST | /v{version}/instance/{instanceId}/checkHotUpgrade | 检查实例是否支持热变配 |
| [绑定标签](API参考/实例管理/绑定标签.md) | POST | /v{version}/instance/tags | 为实例绑定标签 |
| [续费实例](API参考/实例管理/续费实例.md) | POST | /v1/instance/renew | 续费预付费实例 |
| [获取指定实例的自动扩容配置信息](API参考/实例管理/获取指定实例的自动扩容配置信息.md) | GET | /v{version}/instance/{instanceId}/autoResizeConfig | 获取实例自动扩容配置 |
| [获取新购价格](API参考/实例管理/获取新购价格.md) | POST | /v{version}/instance/price | 查询新购实例价格 |
| [获取预付费的变配差价](API参考/实例管理/获取预付费的变配差价.md) | POST | /v{version}/instance/price/diff | 获取预付费变配差价 |
| [释放实例](API参考/实例管理/释放实例.md) | DELETE | /v{version}/instance | 释放云数据库实例 |
| [重启实例](API参考/实例管理/重启实例.md) | PUT | /v{version}/instance/{instanceId} | 重启指定实例，支持立即或时间窗口执行 |
| [集群状态检查](API参考/实例管理/集群状态检查.md) | GET | /v{version}/instance/{instanceId}/status | 检查实例所在集群的运行状态 |

### 数据库管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改描述信息](API参考/数据库管理/修改描述信息.md) | PUT | /v{version}/instance/{instanceId}/databases/{dbName}/remark | 修改指定数据库的描述备注信息 |
| [修改数据库端口](API参考/数据库管理/修改数据库端口.md) | PUT | /v{version}/instance/{instanceId}/port | 修改指定实例的数据库连接端口 |
| [创建数据库](API参考/数据库管理/创建数据库.md) | POST | /v{version}/instance/{instanceId}/databases | 在指定实例中创建数据库 |
| [删除数据库](API参考/数据库管理/删除数据库.md) | DELETE | /v{version}/instance/{instanceId}/databases/{dbName} | 删除指定实例中的指定数据库 |
| [获取数据库列表](API参考/数据库管理/获取数据库列表.md) | GET | /v{version}/instance/{instanceId}/databases | 查询指定实例下的数据库列表 |

### 日志管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [慢日志下载详情](API参考/日志管理/慢日志下载详情.md) | GET | /v{version}/instance/{instanceId}/slowlogs/download_url/{logId}/{downloadValidTimeInSec} | 获取慢日志下载链接及有效期 |
| [慢日志列表](API参考/日志管理/慢日志列表.md) | GET | /v{version}/instance/{instanceId}/slowlogs/logList/{datetime} | 按时间查询实例的慢日志列表 |
| [获取pg日志列表](API参考/日志管理/获取pg日志列表.md) | GET | /v{version}/instance/{instanceId}/pg/list | 获取PostgreSQL数据库日志列表 |
| [获取pg日志详情](API参考/日志管理/获取pg日志详情.md) | GET | /v{version}/instance/{instanceId}/pg/download | 获取pg日志下载详情链接 |
| [获取慢日志详情](API参考/日志管理/获取慢日志详情.md) | POST | /v{version}/instance/{instanceId}/slowlogs/details | 查询慢日志的详细内容 |
| [获取错误日志详情](API参考/日志管理/获取错误日志详情.md) | POST | /v{version}/instance/{instanceId}/errorlogs/details | 查询错误日志的详细内容 |
| [错误日志下载详情](API参考/日志管理/错误日志下载详情.md) | GET | /v{version}/instance/{instanceId}/errorlogs/download_url/{logId}/{downloadValidTimeInSec} | 获取错误日志下载链接及有效期 |
| [错误日志列表](API参考/日志管理/错误日志列表.md) | GET | /v{version}/instance/{instanceId}/errorlogs/logList/{datetime} | 按时间查询实例的错误日志列表 |

### 热活实例组

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [主角色变更](API参考/热活实例组/主角色变更.md) | PUT | /v{version}/instance/group/{groupId}/instance | 变更热活实例组的主角色实例 |
| [修改热活实例组的名称](API参考/热活实例组/修改热活实例组的名称.md) | POST | /v{version}/instance/group/{groupId}/name | 修改热活实例组的名称 |
| [创建实例组](API参考/热活实例组/创建实例组.md) | POST | /v{version}/instance/group | 创建实例组并指定名称和主实例 |
| [删除热活实例组](API参考/热活实例组/删除热活实例组.md) | DELETE | /v{version}/instance/group/{groupId} | 删除指定热活实例组 |
| [加入某个实例组](API参考/热活实例组/加入某个实例组.md) | POST | /v{version}/instance/group/{groupId}/instance | 将指定实例加入目标实例组 |
| [实例组列表](API参考/热活实例组/实例组列表.md) | GET | /v{version}/instance/group | 分页查询实例组列表 |
| [实例组前置检查（GTID检查）](API参考/热活实例组/实例组前置检查（GTID检查）.md) | POST | /v{version}/instance/group/checkGtid | 加入实例组前检查GTID是否开启 |
| [实例组前置检查（实例连通性检查）](API参考/热活实例组/实例组前置检查（实例连通性检查）.md) | POST | /v{version}/instance/group/checkPing | 加入实例组前检查实例间连通性 |
| [实例组前置检查（数据检查）](API参考/热活实例组/实例组前置检查（数据检查）.md) | POST | /v{version}/instance/group/checkData | 加入实例组前检查实例数据条件 |
| [实例组详情](API参考/热活实例组/实例组详情.md) | GET | /v{version}/instance/group/{groupId} | 查询指定实例组详细信息 |
| [小版本前置检查](API参考/热活实例组/小版本前置检查.md) | POST | /v{version}/instance/group/checkVersion | 实例加入热活组前进行小版本检查 |
| [强制切换热活实例组](API参考/热活实例组/强制切换热活实例组.md) | PUT | /v{version}/instance/group/{groupId}/forceChange | 强制切换热活实例组主实例 |
| [批量加入热活实例组](API参考/热活实例组/批量加入热活实例组.md) | POST | /v1/instance/group/batchjoin | 批量将实例加入热活实例组 |
| [退出热活实例组](API参考/热活实例组/退出热活实例组.md) | DELETE | /v{version}/instance/group/{groupId}/instance/{instanceId} | 将实例退出指定热活实例组 |

### 版本管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [发起大版本升级API](API参考/版本管理/发起大版本升级API.md) | PUT | /v{version}/rds/instance/{instanceId} | 对指定实例发起大版本升级 |
| [大版本升级前置检查API](API参考/版本管理/大版本升级前置检查API.md) | GET | /v{version}/rds/instance/{instanceId}/majorVersion/preCheck | 检查实例是否满足大版本升级条件 |
| [实例升级小版本](API参考/版本管理/实例升级小版本.md) | PUT | /v{version}/rds/instance/{instanceId} | 对实例发起小版本升级 |
| [查看实例允许升级的小版本列表](API参考/版本管理/查看实例允许升级的小版本列表.md) | GET | /v{version}/rds/instance/{instanceId}/upgradeMinorVersionList | 查询实例可升级的小版本列表 |
| [版本升级迁移评估API](API参考/版本管理/版本升级迁移评估API.md) | GET | /v{version}/rds/instance/{instanceId}/dtsSourceCheck | 升级前检查实例迁移评估是否通过 |
| [获取实例大版本列表API](API参考/版本管理/获取实例大版本列表API.md) | GET | /v{version}/rds/instance/{instanceId}/majorVersionList | 查询实例可升级的大版本列表 |

### 表粒度账号管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询账户详情](API参考/表粒度账号管理/查询账户详情.md) | POST | /v{version}/instance/account/tableLevel/detail | 查询指定实例表粒度账户详情 |

### 账号管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改账号备注](API参考/账号管理/修改账号备注.md) | PUT | /v{version}/instance/{instanceId}/account/{accountName}/desc | 修改指定实例账号的备注信息 |
| [修改账号密码](API参考/账号管理/修改账号密码.md) | PUT | /v{version}/instance/{instanceId}/account/{accountName}/password | 修改指定实例账号的密码 |
| [修改账号权限](API参考/账号管理/修改账号权限.md) | PUT | /v{version}/instance/{instanceId}/account/{accountName}/privileges | 修改指定实例账号的数据库权限 |
| [创建账号](API参考/账号管理/创建账号.md) | POST | /v{version}/instance/{instanceId}/account | 在指定主实例下创建新账号 |
| [删除账号](API参考/账号管理/删除账号.md) | DELETE | /v{version}/instance/{instanceId}/account/{accountName} | 删除指定实例下的指定账号 |
| [查询账号列表](API参考/账号管理/查询账号列表.md) | GET | /v{version}/instance/{instanceId}/account | 查询指定实例的账号列表 |
| [查询账号详情](API参考/账号管理/查询账号详情.md) | GET | /v{version}/instance/{instanceId}/account/{accountName} | 查询指定实例账号详情（v1） |
| [表粒度新增账号API](API参考/账号管理/表粒度新增账号API.md) | POST | /v2/instance/{instanceId}/account/tableLevel/create | 新增表粒度账号并设置三级权限 |
| [表粒度更新用户描述API](API参考/账号管理/表粒度更新用户描述API.md) | PUT | /v2/instance/account/tableLevel/update_desc | 更新表粒度账号的备注描述 |
| [表粒度查询用户列表API](API参考/账号管理/表粒度查询用户列表API.md) | GET | /v2/instance/{instanceId}/account/tableLevel/list | 查询实例下全部表粒度账号列表 |
| [表粒度查询用户详情API](API参考/账号管理/表粒度查询用户详情API.md) | POST | /v2/instance/account/tableLevel/detail | 查询表粒度账号详情及完整权限 |

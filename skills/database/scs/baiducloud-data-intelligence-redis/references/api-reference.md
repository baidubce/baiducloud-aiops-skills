# baiducloud-data-intelligence-redis API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-15T17:08:57+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 北京 | bj | redis.bj.baidubce.com |
| 保定 | bd | redis.bd.baidubce.com |
| 广州 | gz | redis.gz.baidubce.com |
| 苏州 | su | redis.su.baidubce.com |
| 武汉 | fwh | redis.fwh.baidubce.com |
| 香港 | hkg | redis.hkg.baidubce.com |

## 接口目录

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [API简介](API参考/API简介.md) |  |  | 介绍Redis API设计规范及认证追踪机制 |
| [API规格](API参考/API规格.md) |  |  | 说明Redis API公共请求头与响应头格式 |
| [使用须知](API参考/使用须知.md) |  |  | 说明API认证机制、排版约定及时间日期规范 |
| [通用说明](API参考/通用说明.md) | POST | /v{version}/instance/{instanceId} | 说明API域名协议和通用参数。 |
| [错误返回](API参考/错误返回.md) |  |  | 说明错误响应格式与公共错误码 |
| [附录](API参考/附录.md) |  |  | 定义实例模型等附录数据结构 |

### 参数模版

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改参数模版名称](API参考/参数模版/修改参数模版名称.md) | PUT | /v2/template/rename/{templateShowId} | 修改指定参数模版的名称 |
| [创建参数模版](API参考/参数模版/创建参数模版.md) | POST | /v2/template/create | 创建不区分地域的参数模版 |
| [删除参数模版](API参考/参数模版/删除参数模版.md) | DELETE | /v2/template/delete/{templateShowId} | 删除指定参数模版 |
| [参数模版修改参数](API参考/参数模版/参数模版修改参数.md) | PUT | /v2/template/modifyParams/{templateShowId} | 修改参数模版中的指定参数配置 |
| [参数模版删除参数](API参考/参数模版/参数模版删除参数.md) | POST | /v2/template/deleteParams/{templateShowId} | 从参数模版中删除指定参数 |
| [参数模版添加参数](API参考/参数模版/参数模版添加参数.md) | POST | /v2/template/addParams/{templateShowId} | 向参数模版中添加指定参数 |
| [参数模版详情](API参考/参数模版/参数模版详情.md) | GET | /v2/template/{templateShowId} | 查看指定参数模版的详细信息 |
| [应用参数模版](API参考/参数模版/应用参数模版.md) | POST | /v2/template/apply/{templateShowId} | 将参数模版应用到指定实例 |
| [获取参数模版列表](API参考/参数模版/获取参数模版列表.md) | GET | /v2/template/list | 分页获取当前账号参数模版列表 |
| [获取应用参数模版记录](API参考/参数模版/获取应用参数模版记录.md) | GET | /v2/template/record/{templateShowId} | 分页获取参数模版应用历史记录 |
| [获取系统参数列表](API参考/参数模版/获取系统参数列表.md) | GET | /v2/template/system | 获取全量系统参数供创建模版选择 |

### 参数管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改参数](API参考/参数管理/修改参数.md) | PUT | /v1/instance/{instanceId}/parameter | 修改Redis实例的指定参数值 |
| [获取参数列表](API参考/参数管理/获取参数列表.md) | GET | /v1/instance/{instanceId}/parameter | 查询Redis实例配置与运行参数 |

### 备份恢复

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改备份备注API](API参考/备份恢复/修改备份备注API.md) | PUT | /v1/instance/{instanceId}/backup/{batchId}/comment | 修改指定备份的备注信息 |
| [删除手动备份API](API参考/备份恢复/删除手动备份API.md) | DELETE | /v1/instance/{instanceId}/backup/{batchId} | 删除指定实例的手动备份 |
| [手动备份API](API参考/备份恢复/手动备份API.md) | POST | /v1/instance/{instanceId}/backup | 手动触发实例备份 |
| [查看备份列表API](API参考/备份恢复/查看备份列表API.md) | GET | /v1/instance/{instanceId}/backup | 查询实例的备份列表 |
| [获取备份的URL API](API参考/备份恢复/获取备份的URL API.md) | GET | /v1/instance/{instanceId}/backup/{backupId}/url | 获取备份文件的下载链接 |
| [获取备份策略API](API参考/备份恢复/获取备份策略API.md) | GET | /v1/instance/{instanceId}/backup/policy | 查询实例的自动备份策略 |
| [设置备份策略API](API参考/备份恢复/设置备份策略API.md) | PUT | /v1/instance/{instanceId}/backup/modifyPolicy | 设置实例的自动备份策略 |

### 多活实例组

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改多活实例组名称](API参考/多活实例组/修改多活实例组名称.md) | PUT | /v{version}/syncGroup/{syncGroupShowId} | 修改多活实例组名称 |
| [创建多活实例组](API参考/多活实例组/创建多活实例组.md) | POST | /v{version}/syncGroup/create | 创建多活实例组 |
| [前置检查](API参考/多活实例组/前置检查.md) | POST | /v{version}/syncGroup/check | 热活实例组创建前置检查 |
| [多活实例组列表](API参考/多活实例组/多活实例组列表.md) | GET | /v{version}/syncGroup/list | 查询多活实例组列表 |
| [多活实例组删除](API参考/多活实例组/多活实例组删除.md) | DELETE | /v{version}/syncGroup/{syncGroupShowId} | 删除指定的多活实例组 |
| [多活实例组详情](API参考/多活实例组/多活实例组详情.md) | GET | /v{version}/syncGroup/{syncGroupShowId} | 查询多活实例组详情 |
| [获取同步状态](API参考/多活实例组/获取同步状态.md) | GET | /v{version}/syncGroup/{syncGroupShowId}/syncStatus | 获取实例组同步状态 |

### 安全管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [TDE加密](API参考/安全管理/TDE加密.md) | POST | /v{version}/instance/{instanceId}/tde | 开启实例的TDE加密 |
| [开启或关闭TLS加密API](API参考/安全管理/开启或关闭TLS加密API.md) | POST | /v1/instance/{instanceId}/tls | 开启或关闭TLS加密 |
| [更新安全组API](API参考/安全管理/更新安全组API.md) | POST | /v1/instance/{instanceId}/securityGroup/update | 更新实例绑定的安全组 |
| [查看安全组API](API参考/安全管理/查看安全组API.md) | GET | /v1/instance/{instanceId}/securityGroup | 查看实例绑定的安全组 |
| [绑定安全组API](API参考/安全管理/绑定安全组API.md) | POST | /v1/instance/{instanceId}/securityGroup/bind | 为实例绑定安全组 |
| [获取TLS证书API](API参考/安全管理/获取TLS证书API.md) | GET | /v1/instance/{instanceId}/tls | 获取实例的TLS证书 |
| [解绑安全组API](API参考/安全管理/解绑安全组API.md) | POST | /v1/instance/{instanceId}/securityGroup/unbind | 解绑Redis实例已绑定的安全组。 |

### 实例服务

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [IP变更API](API参考/实例服务/IP变更API.md) | POST | /v1/instance/{instanceId}/azoneMigration/modifyEntrance | 变更Redis实例内网IP地址。 |
| [主从切换API](API参考/实例服务/主从切换API.md) | PUT | /v1/instance/{instanceId}/switchMasterSlave | 切换实例分片的主从节点关系。 |
| [从回收站中批量恢复实例](API参考/实例服务/从回收站中批量恢复实例.md) | POST | /v2/recycler/recover | 批量恢复回收站中的后付费实例。 |
| [代理节点替换API](API参考/实例服务/代理节点替换API.md) | PUT | /v1/instance/{instanceId}/proxyNode | 替换Redis实例中的代理节点。 |
| [修改实例名称](API参考/实例服务/修改实例名称.md) | PUT | /v1/instance/{instanceId}/rename | 修改指定Redis实例的名称。 |
| [修改实例域名](API参考/实例服务/修改实例域名.md) | PUT | /v1/instance/{instanceId}/renameDomain | 修改指定Redis实例的访问域名。 |
| [修改维护时间窗口API](API参考/实例服务/修改维护时间窗口API.md) | PUT | /v1/instance/{instanceId}/timeWindow | 修改实例的日常维护时间窗口。 |
| [创建统一读入口](API参考/实例服务/创建统一读入口.md) | POST | /v{version}/entrance/create/{instanceId} | 为集群创建统一读入口地址。 |
| [拨测接口](API参考/实例服务/拨测接口.md) | GET | /v{version}/instance/{instanceId}/blbStatus | 检测实例BLB的存活状态。 |
| [标准版升级集群版API](API参考/实例服务/标准版升级集群版API.md) | PUT | /v1/instance/{instanceId}/clusterTypeChange | 将标准版实例升级为集群版。 |
| [清空实例API](API参考/实例服务/清空实例API.md) | PUT | /v1/instance/{instanceId}/flush | 清空指定Redis实例的全部数据。 |
| [绑定标签](API参考/实例服务/绑定标签.md) | PUT | /v1/instance/{instanceId}/bindTag | 为指定Redis实例绑定标签。 |
| [统一读入口负载均衡](API参考/实例服务/统一读入口负载均衡.md) | POST | /v{version}/entrance/disconnect/{instanceId} | 对统一读入口重新负载均衡。 |
| [获取可用区列表](API参考/实例服务/获取可用区列表.md) | GET | /v1/zone | 查询Redis可用区列表。 |
| [获取回收站内的实例列表](API参考/实例服务/获取回收站内的实例列表.md) | GET | /v2/recycler/list | 查询回收站内的实例列表。 |
| [获取子网列表](API参考/实例服务/获取子网列表.md) | GET | /v1/subnet | 查询指定VPC下的子网列表。 |
| [获取实例列表](API参考/实例服务/获取实例列表.md) | GET | /v2/instance | 查询账号下Redis实例列表。 |
| [获取实例规格列表](API参考/实例服务/获取实例规格列表.md) | GET | /v2/nodetypes | 查询Redis实例规格列表 |
| [获取实例详情](API参考/实例服务/获取实例详情.md) | GET | /v2/instance/{instanceId} | 查询指定实例详细信息 |
| [解绑标签](API参考/实例服务/解绑标签.md) | PUT | /v1/instance/{instanceId}/unBindTag | 解绑实例上的指定标签 |
| [迁移可用区API](API参考/实例服务/迁移可用区API.md) | POST | /v1/instance/{instanceId}/azoneMigration | 将实例迁移至其他可用区 |
| [释放回收站中的实例](API参考/实例服务/释放回收站中的实例.md) | POST | /v2/recycler/delete | 从回收站批量释放实例 |
| [重启实例API](API参考/实例服务/重启实例API.md) | PUT | /v1/instance/{instanceId}/restart | 重启指定Redis实例 |
| [集群状态检查](API参考/实例服务/集群状态检查.md) | GET | /v{version}/instance/{instanceId}/status | 检查实例所在集群状态 |

### 弹性扩缩

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [删除 内存弹性扩缩API](API参考/弹性扩缩/删除 内存弹性扩缩API.md) | POST | /v1/instance/{instanceId}/deleteAutoScalingConfig | 删除实例内存弹性扩缩配置 |
| [查询内存弹性扩缩配置API](API参考/弹性扩缩/查询内存弹性扩缩配置API.md) | GET | /v1/instance/{instanceId}/autoScalingConfig | 查询实例内存弹性扩缩配置 |
| [设置内存弹性扩缩配置API](API参考/弹性扩缩/设置内存弹性扩缩配置API.md) | POST | /v1/instance/{instanceId}/autoScalingConfig | 设置实例内存弹性扩缩配置 |

### 日志管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [审计日志开关API](API参考/日志管理/审计日志开关API.md) | PUT | /v1/instance/{instanceId}/log/audit/switch | 开启或关闭实例审计日志 |
| [日志列表API](API参考/日志管理/日志列表API.md) | GET | /v1/instance/{instanceId}/log/list | 查询实例日志列表 |
| [日志明细API](API参考/日志管理/日志明细API.md) | GET | /v1/instance/{instanceId}/log/{logId} | 查询指定日志明细和下载链接 |

### 热活实例组

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改热活实例组名称](API参考/热活实例组/修改热活实例组名称.md) | PUT | /v2/group/{groupId} | 修改热活实例组名称 |
| [创建热活实例组](API参考/热活实例组/创建热活实例组.md) | POST | /v2/group/create | 创建热活实例组 |
| [删除IP白名单](API参考/热活实例组/删除IP白名单.md) | PUT | /v2/group/{groupId}/white_list/delete | 删除实例IP白名单 |
| [前置检查](API参考/热活实例组/前置检查.md) | POST | /v2/group/check | 热活实例组创建前置检查 |
| [变更主角色](API参考/热活实例组/变更主角色.md) | POST | /v2/group/{groupId}/setAsLeader/{instanceId} | 变更热活实例组主角色 |
| [实例组禁写](API参考/热活实例组/实例组禁写.md) | PUT | /v2/group/{groupId}/forbidWrite | 设置热活实例组是否禁写 |
| [添加IP白名单](API参考/热活实例组/添加IP白名单.md) | PUT | /v2/group/{groupId}/white_list/add | 为热活实例组添加IP白名单 |
| [添加从集群](API参考/热活实例组/添加从集群.md) | POST | /v2/group/{groupId}/join | 向热活实例组添加从角色集群 |
| [热活实例组详情](API参考/热活实例组/热活实例组详情.md) | GET | /v2/group/{groupId} | 查询热活实例组详细信息 |
| [移除从集群](API参考/热活实例组/移除从集群.md) | POST | /v2/group/{groupId}/quit/{instanceId} | 从热活实例组移除从角色集群 |
| [获取IP白名单列表](API参考/热活实例组/获取IP白名单列表.md) | GET | /v2/group/{groupId}/white_list | 获取热活实例组IP白名单列表 |
| [获取从角色同步状态](API参考/热活实例组/获取从角色同步状态.md) | GET | /v2/group/{groupId}/syncStatus | 查询热活实例组从角色同步状态 |
| [获取热活实例组列表](API参考/热活实例组/获取热活实例组列表.md) | POST | /v2/group/list | 分页查询热活实例组列表 |
| [设置从角色脏读](API参考/热活实例组/设置从角色脏读.md) | PUT | /v2/group/{groupId}/stale_readable | 设置热活实例组从角色脏读 |
| [设置流控规则](API参考/热活实例组/设置流控规则.md) | PUT | /v2/group/{groupId}/qps | 设置热活实例组流控规则 |
| [释放热活实例组](API参考/热活实例组/释放热活实例组.md) | DELETE | /v2/group/{groupId}/release | 释放指定热活实例组 |

### 版本升级

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [代理版本升级or重启 API](API参考/版本升级/代理版本升级or重启 API.md) | PUT | /v1/instance/{instanceId}/upgradeProxy | 升级或重启实例代理 |
| [大版本升级API](API参考/版本升级/大版本升级API.md) | POST | /v1/instance/{instanceId}/upgradeVersion | 升级实例内核大版本 |

### 网络安全

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改访问密码](API参考/网络安全/修改访问密码.md) | PUT | /v1/instance/{instanceId}/modifyPassword | 修改实例的访问密码 |
| [删除IP白名单](API参考/网络安全/删除IP白名单.md) | DELETE | /v1/instance/{instanceId}/securityIp | 删除实例IP白名单 |
| [域名交换](API参考/网络安全/域名交换.md) | POST | /v2/instance/swapDomain | 交换源和目标实例域名 |
| [增加IP白名单](API参考/网络安全/增加IP白名单.md) | PUT | /v1/instance/{instanceId}/securityIp | 为实例增加IP白名单 |
| [查询IP白名单](API参考/网络安全/查询IP白名单.md) | GET | /v1/instance/{instanceId}/securityIp | 查询实例IP白名单 |

### 订单服务

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建实例](API参考/订单服务/创建实例.md) | POST | /v2/instance | 创建一个或多个Redis实例。 |
| [取消预付费转后付费API](API参考/订单服务/取消预付费转后付费API.md) | POST | /v1/instance/cancelToPostpay | 取消未生效的预付费转后付费变更。 |
| [变更配置](API参考/订单服务/变更配置.md) | PUT | /v1/instance/{instanceId}/change | 变更Redis实例规格配置。 |
| [后付费转预付费API](API参考/订单服务/后付费转预付费API.md) | POST | /v1/instance/toPrepay | 将后付费实例转为预付费。 |
| [手动修改带宽API](API参考/订单服务/手动修改带宽API.md) | POST | /v1/instance/{instanceId}/modifyBandwidth | 手动修改Redis实例带宽值。 |
| [续费API](API参考/订单服务/续费API.md) | POST | /v1/instance/renew | 对预付费实例执行续费操作。 |
| [获取创建实例价格](API参考/订单服务/获取创建实例价格.md) | POST | /v1/price | 查询创建指定规格实例的价格。 |
| [获取实例变更配置价格](API参考/订单服务/获取实例变更配置价格.md) | POST | /v1/instance/{instanceId}/price | 查询实例变更为指定配置价格。 |
| [释放实例](API参考/订单服务/释放实例.md) | DELETE | /v1/instance/{instanceId} | 释放实例并移入回收站。 |
| [预付费转后付费API](API参考/订单服务/预付费转后付费API.md) | POST | /v1/instance/toPostpay | 将预付费实例转为后付费。 |

### 账号管理

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改账号密码](API参考/账号管理/修改账号密码.md) | POST | /v{version}/instance/{instanceId}/aclUserActions/modifyPasswd | 修改非default账号的密码。 |
| [创建账号](API参考/账号管理/创建账号.md) | POST | /v{version}/instance/{instanceId}/aclUserActions | 为集群创建访问账号。 |
| [删除账号](API参考/账号管理/删除账号.md) | POST | /v{version}/instance/{instanceId}/aclUserActions/delete | 删除指定集群账号。 |
| [设置权限](API参考/账号管理/设置权限.md) | POST | /v{version}/instance/{instanceId}/aclUserActions/authority | 设置指定账号读写权限。 |
| [账号列表](API参考/账号管理/账号列表.md) | GET | /v{version}/instance/{instanceId}/aclUserActions | 查询集群账号列表。 |

### 部署集

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [修改部署集API](API参考/部署集/修改部署集API.md) | PUT | /v1/deploySet/{deploySetId} | 修改指定部署集信息。 |
| [创建部署集API](API参考/部署集/创建部署集API.md) | POST | /v1/deploySet | 创建Redis部署集。 |
| [删除部署集API](API参考/部署集/删除部署集API.md) | DELETE | /v1/deploySet/{deploySetId} | 删除指定部署集，有绑定实例则不可删除 |
| [获取部署集列表API](API参考/部署集/获取部署集列表API.md) | GET | /v1/deploySet | 分页查询部署集列表 |

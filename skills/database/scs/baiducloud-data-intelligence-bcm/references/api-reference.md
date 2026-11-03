# baiducloud-data-intelligence-bcm API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:07:59+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 华北-北京 | bj | bcm.bj.baidubce.com |
| 华北-保定 | bd | bcm.bd.baidubce.com |
| 华北-阳泉 | yq | bcm.yq.baidubce.com |
| 西南-成都 | cd | bcm.cd.baidubce.com |
| 华南-广州 | gz | bcm.gz.baidubce.com |
| 华东-苏州 | su | bcm.su.baidubce.com |
| 华东-南京 | nj | bcm.nj.baidubce.com |
| 华中-武汉 | fwh | bcm.fwh.baidubce.com |
| 香港 | hkg | bcm.hkg.baidubce.com |
| 华北-度小满金融专区 | hb-fsg | bcm.hb-fsg.baidubce.com |

## 接口目录

### v1 版本 / 事件总线

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [1. 事件集](API参考/v1 版本/事件总线.md) | POST | /v1/event-bus | 创建事件集 |
| [2. 事件源](API参考/v1 版本/事件总线.md) | GET | /v1/event-bus/source/list | 获取指定事件集下事件源列表 |
| [3. 事件](API参考/v1 版本/事件总线.md) | GET | /v1/event-bus/event/list | 获取指定事件源下事件列表 |
| [4. 事件接收](API参考/v1 版本/事件总线.md) | POST | /v1/event-bus/recv | 接收用户自定义事件并批量发送 |
| [5. 事件规则](API参考/v1 版本/事件总线.md) | POST | /v1/event-bus/rule | 创建事件规则及投递目标配置 |
| [6. 事件历史查询](API参考/v1 版本/事件总线.md) | GET | /v1/event-bus/historic | 查询事件推送历史记录 |

### v1 版本

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [事件总线推送](API参考/v1 版本/事件总线推送.md) | POST | /v1/event-bus/recv | 向事件总线推送具体事件 |
| [事件报警历史](API参考/v1 版本/事件报警历史.md) | GET | /event-api/v1/accounts/{userId}/services/BCE_ALL/alarm-histories | 获取云产品事件报警历史列表 |
| [云产品事件列表查询](API参考/v1 版本/云产品事件列表查询.md) | POST | /event-api/v1/event/metaList | 查询云产品下事件列表 |
| [云产品监控项列表查询](API参考/v1 版本/云产品监控项列表查询.md) | POST | /csm/api/v1/meta/metric/list | 查询云产品下监控项列表 |
| [仪表盘接口](API参考/v1 版本/仪表盘接口.md) | POST | /csm/api/v1/dashboard/products/{userId}/dashboards | 创建仪表盘 |
| [批量查询监控数据接口V2](API参考/v1 版本/批量查询监控数据接口V2.md) | POST | /csm/api/v2/data/metricAllData | 批量查询云产品多维度多指标监控数据 |
| [查询数据接口](API参考/v1 版本/查询数据接口.md) | GET | /json-api/v1/metricdata/{userId}/BCE_BCC/CpuIdlePercent | 查询指标统计数据时间序列 |
| [维度值TopN和监控数据查询接口](API参考/v1 版本/维度值TopN和监控数据查询接口.md) | POST | /csm/api/v2/dimensions/top | 获取维度值TopN及对应监控数据 |
| [维度值TopN查询接口](API参考/v1 版本/维度值TopN查询接口.md) | POST | /csm/api/v2/dimensions/top | 获取指定指标下维度值TopN |
| [部分维度查询最新指标数据](API参考/v1 版本/部分维度查询最新指标数据.md) | POST | /csm/api/v2/userId/{userId}/services/BCE_BLB/data/metricData/latest/batch | 按多维度查询最新指标数据 |
| [部分维度查询监控数据](API参考/v1 版本/部分维度查询监控数据.md) | POST | /csm/api/v2/userId/{userId}/services/BCE_BLB/data/metricData/PartialDimension | 按多维度查询监控数据 |

### v1 版本 / 事件监控

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询云产品事件](API参考/v1 版本/事件监控.md) | GET | /event-api/v1/bce-event/list | 获取云产品事件信息列表 |
| [查询平台类事件](API参考/v1 版本/事件监控.md) | GET | /event-api/v1/platform-event/list | 获取平台类事件信息列表 |
| [报警策略](API参考/v1 版本/事件监控.md) | POST | /event-api/v1/accounts/{accountId}/services/{serviceName}/alarm-policies | 创建事件报警策略 |

### v1 版本 / 即时拨测

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建探测任务](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/HTTP/taskCreate | 创建网络探测任务 |
| [探测历史记录](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/taskList | 查询探测任务历史记录 |
| [删除探测记录](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/taskDelete | 删除指定探测记录 |
| [探测任务结果](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/loadData | 查询探测任务结果数据 |
| [探测详情](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/groupTask | 分页查询探测任务结果详情 |
| [重新探测](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/createFromTask | 基于原任务创建重新探测任务 |
| [历史探测列表](API参考/v1 版本/即时拨测.md) | POST | /csm/api/v1/site/once/groupTaskList | 查询某任务或组的历史探测列表 |
| [获取当前探测点](API参考/v1 版本/即时拨测.md) | GET | /csm/api/v1/site/once/siteAgent | 获取当前可用探测点及IP类型 |

### v1 版本 / 站点监控

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [站点监控任务配置相关接口](API参考/v1 版本/定时探测（原站点监控）.md) | POST | /csm/api/v1/userId/{userId}/site/http/create | 创建和配置站点监控任务 |
| [站点报警配置相关接口](API参考/v1 版本/定时探测（原站点监控）.md) | POST | /csm/api/v1/userId/{userId}/site/alarm/config/create | 创建站点监控报警策略配置 |
| [整体概览相关接口](API参考/v1 版本/定时探测（原站点监控）.md) | GET | /csm/api/v1/userId/{userId}/site/metricSiteData | 获取站点监控整体趋势概览数据 |
| [探测点相关接口](API参考/v1 版本/定时探测（原站点监控）.md) | GET | /csm/api/v1/userId/{userId}/site/agent/list | 列出可用探测点省份与运营商 |

### v1 版本 / 实例组接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建实例组](API参考/v1 版本/实例组接口.md) | POST | /csm/api/v1/userId/{userId}/instance-group | 创建新的实例组 |
| [更新实例组名称](API参考/v1 版本/实例组接口.md) | PATCH | /csm/api/v1/userId/{userId}/instance-group | 修改指定实例组名称 |
| [删除实例组](API参考/v1 版本/实例组接口.md) | DELETE | /csm/api/v1/userId/{userId}/instance-group/7900 | 删除指定实例组 |
| [获取实例组详情](API参考/v1 版本/实例组接口.md) | GET | /csm/api/v1/userId/{userId}/instance-group/7900 | 查询指定实例组详细信息 |
| [查询实例组列表](API参考/v1 版本/实例组接口.md) | GET | /csm/api/v1/userId/{userId}/instance-group/list | 分页查询实例组列表 |
| [实例组添加实例成员](API参考/v1 版本/实例组接口.md) | POST | /csm/api/v1/userId/{userId}/instance-group/7900/instance/add | 向实例组批量添加实例成员 |
| [获取实例组实例成员列表](API参考/v1 版本/实例组接口.md) | GET | /csm/api/v1/userId/{userId}/instance-group/instance/list？ | 查询实例组内实例成员列表 |
| [实例组移除实例成员](API参考/v1 版本/实例组接口.md) | POST | /csm/api/v1/userId/{userId}/instance-group/7900/instance/remove | 从实例组移除实例成员 |
| [查看实例列表接口（创建实例组时用）](API参考/v1 版本/实例组接口.md) | GET | /csm/api/v1/userId/{userId}/instance/list | 查询可加入实例组的实例列表 |
| [查看实例列表（用于对已经创建的实例组进行添加实例操作—过滤掉已经添加的实例）](API参考/v1 版本/实例组接口.md) | GET | /csm/api/v1/userId/{userId}/instance/filteredList | 查询可添加且未入组的实例列表 |

### v1 版本 / 报警历史

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [报警历史列表](API参考/v1 版本/报警历史.md) | POST | /ah-api/v1/alarmhouse/alarm/list | 分页查询各类报警历史记录列表 |
| [报警历史详情](API参考/v1 版本/报警历史.md) | GET | /ah-api/v1/alarmhouse/alarm | 按报警ID查询报警历史详情 |

### v1 版本 / 报警管理接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建报警策略](API参考/v1 版本/报警管理接口.md) | POST | /csm/api/v1/services/alarm/config/create | 创建V2版报警策略配置 |
| [删除报警策略](API参考/v1 版本/报警管理接口.md) | POST | /csm/api/v1/services/alarm/config/delete | 删除指定云产品的报警策略 |
| [更新报警策略](API参考/v1 版本/报警管理接口.md) | POST | /csm/api/v1/services/alarm/config/update | 全量更新V2版报警策略配置 |
| [屏蔽报警策略](API参考/v1 版本/报警管理接口.md) | POST | /csm/api/v1/services/alarm/config/block | 屏蔽指定报警策略通知 |
| [开启报警配置](API参考/v1 版本/报警管理接口.md) | POST | /csm/api/v1/services/alarm/config/unblock | 开启指定报警策略通知 |
| [查看报警策略](API参考/v1 版本/报警管理接口.md) | GET | /csm/api/v1/services/alarm/config | 查看指定报警策略详情 |
| [查看单一实例报列表接口](API参考/v1 版本/报警管理接口.md) | GET | /csm/api/v1/services/alarm/config/list | 查看单一实例的报警策略列表 |
| [获取指标列表](API参考/v1 版本/报警管理接口.md) | GET | /csm/api/v1/services/alarm/config/metrics | 获取指定云产品指标项列表 |

### v1 版本 / 报警管理接口V2

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建报警策略](API参考/v1 版本/报警管理接口V2.md) | POST | /csm/api/v2/userId/{userId}/services/{service}/alarm/config/create | 创建V2版报警策略配置 |
| [更新报警策略](API参考/v1 版本/报警管理接口V2.md) | PUT | /csm/api/v2/userId/{userId}/services/{service}/alarm/config/update | 全量更新V2版报警策略配置 |
| [屏蔽报警策略](API参考/v1 版本/报警管理接口V2.md) | POST | /csm/api/v2/userId/{userId}/services/BCE_BCC/alarm/config/block | 屏蔽指定报警策略通知 |
| [开启报警策略](API参考/v1 版本/报警管理接口V2.md) | POST | /csm/api/v2/userId/{userId}/services/BCE_BCC/alarm/config/unblock | 开启指定报警策略通知 |
| [查看报警策略](API参考/v1 版本/报警管理接口V2.md) | GET | /csm/api/v2/userId/{userId}/services/BCE_BCC/alarm/config | 查看指定报警策略详情 |
| [查看报警策略列表](API参考/v1 版本/报警管理接口V2.md) | GET | /csm/api/v2/userId/{userId}/services/BCE_BCC/alarm/config/list | 分页查看报警策略列表 |

### v1 版本 / 通知模版

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [查询用户组列表](API参考/v1 版本/通知模版.md) | POST | /json-api/v1/alarm/notify/group/list | 分页查询用户组列表 |
| [查询用户列表](API参考/v1 版本/通知模版.md) | POST | /json-api/v1/alarm/notify/party/list | 分页查询用户列表 |
| [新建通知模版](API参考/v1 版本/通知模版.md) | POST | /csm/api/v1/userId/{userId}/action/create | 创建报警通知模版 |
| [删除通知模版](API参考/v1 版本/通知模版.md) | DELETE | /csm/api/v1/userId/{userId}/action/delete | 删除指定通知模版 |
| [查询通知模版列表](API参考/v1 版本/通知模版.md) | POST | /csm/api/v1/userId/{userId}/action/actionList | 分页查询通知模版列表 |
| [编辑通知模版](API参考/v1 版本/通知模版.md) | POST | /csm/api/v1/userId/{userId}/action/update | 编辑指定通知模版 |

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [公共请求与响应头](API参考/公共请求与响应头.md) |  |  | 说明公共请求与响应头 |
| [服务域名](API参考/服务域名.md) |  |  | 列出各区域服务域名 |
| [概述](API参考/概述.md) |  |  | 云监控API概述 |
| [通用说明](API参考/通用说明.md) | POST | /v{version}/instance/{instanceId} | API通用说明与认证 |
| [错误返回](API参考/错误返回.md) |  |  | 错误返回格式与错误码 |

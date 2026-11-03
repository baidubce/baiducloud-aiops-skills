# baiducloud-data-intelligence-iam API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:10:29+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 北京 | bj | iam.bj.baidubce.com |

## 接口目录

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [公共请求头与公共响应头](API参考/公共请求头与公共响应头.md) |  |  | 描述公共请求头与响应头字段。 |
| [数据类型](API参考/数据类型.md) |  |  | 定义用户、登录配置等数据模型。 |
| [服务域名](API参考/服务域名.md) |  |  | 提供身份服务的访问域名与协议。 |
| [简介](API参考/简介.md) |  |  | 介绍IAM概述与API接口概览 |
| [通用说明](API参考/通用说明.md) | PUT | /v1/user/{userName} | 介绍API认证签名等通用约定。 |
| [错误码](API参考/错误码.md) |  |  | 说明错误返回格式与公共错误码。 |

### 用户管理接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建用户](API参考/用户管理接口.md) | POST | /v1/user | 创建新的IAM子用户。 |
| [查询用户](API参考/用户管理接口.md) | GET | /v1/user/{userName} | 查询指定用户的详细信息。 |
| [更新用户](API参考/用户管理接口.md) | PUT | /v1/user/{userName} | 更新用户名称、描述或状态。 |
| [删除用户](API参考/用户管理接口.md) | DELETE | /v1/user/{userName} | 删除指定用户及其关联资源。 |
| [列举用户](API参考/用户管理接口.md) | GET | /v1/user | 列出所有IAM用户。 |
| [配置用户的控制台登录](API参考/用户管理接口.md) | PUT | /v1/user/{userName}/loginProfile | 设置用户控制台登录密码与MFA。 |
| [查询控制台登录配置](API参考/用户管理接口.md) | GET | /v1/user/{userName}/loginProfile | 查询用户控制台登录配置。 |
| [关闭控制台登录配置](API参考/用户管理接口.md) | DELETE | /v1/user/{userName}/loginProfile | 关闭用户控制台登录功能。 |
| [修改子用户操作保护](API参考/用户管理接口.md) | POST | /v1/user/operation/mfa/switch | 开启或关闭子用户操作保护。 |
| [修改子用户密码](API参考/用户管理接口.md) | PUT | /v1/subUser/{userName}/update | 修改子用户登录密码。 |
| [创建用户的AccessKey](API参考/用户管理接口.md) | POST | /v1/user/{userName}/accesskey | 为用户创建AccessKey密钥。 |
| [禁用用户的AccessKey](API参考/用户管理接口.md) | PUT | /user/{userName}/accesskey/{accessKeyId} | 禁用指定用户的AccessKey。 |
| [启用用户的AccessKey](API参考/用户管理接口.md) | PUT | /user/{userName}/accesskey/{accessKeyId} | 启用指定用户的AccessKey。 |
| [删除用户的AccessKey](API参考/用户管理接口.md) | DELETE | /user/{userName}/accesskey/{accessKeyId} | 删除指定用户的AccessKey。 |
| [列举用户的AccessKey](API参考/用户管理接口.md) | GET | /v1/user/{userName}/accesskey | 列出用户所有AccessKey。 |
| [查询用户的AccessKey上次使用时间](API参考/用户管理接口.md) | GET | /v1/accesskey/{accessKeyId}/lastusedtime | 查询访问密钥上次使用时间 |
| [解绑子用户虚拟 MFA](API参考/用户管理接口.md) | DELETE | /v1/user/{userName}/mfaType/{mfaType} | 解绑子用户虚拟MFA认证 |
| [查询IAM用户联合信息](API参考/用户管理接口.md) | GET | /v1/subUser/idp/query | 查询IAM用户联合配置信息 |
| [更新IAM用户联合功能状态](API参考/用户管理接口.md) | POST | /v1/subUser/idp/updateStatus | 启用或关闭IAM用户联合功能 |
| [更新IAM用户联合功能配置](API参考/用户管理接口.md) | POST | /v1/subUser/idp/update | 更新IAM用户联合功能配置 |
| [删除IAM用户联合配置](API参考/用户管理接口.md) | POST | /v1/subUser/idp/delete | 删除IAM用户联合功能配置 |
| [查询主账号概览信息](API参考/用户管理接口.md) | GET | /v1/account/summary | 查询主账号配额与计数概览 |

### 策略管理接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建策略](API参考/策略管理接口.md) | POST | /v1/policy | 创建新的权限策略 |
| [更新策略](API参考/策略管理接口.md) | POST | /v1/policy/{policyName} | 更新自定义权限策略内容 |
| [查询策略](API参考/策略管理接口.md) | GET | /v1/policy/{policyName} | 查询指定权限策略详情 |
| [删除策略](API参考/策略管理接口.md) | DELETE | /v1/policy/{policyName} | 删除指定权限策略 |
| [列举策略](API参考/策略管理接口.md) | GET | /v1/policy | 列举系统或自定义策略 |
| [关联用户权限](API参考/策略管理接口.md) | PUT | /v1/user/{userName}/policy/{policyName} | 为用户关联权限策略 |
| [解除用户权限](API参考/策略管理接口.md) | DELETE | /v1/user/{userName}/policy/{policyName}policyType={policyType} | 解除用户关联的权限策略 |
| [列举用户的权限](API参考/策略管理接口.md) | GET | /v1/user/{userName}/policy | 列举用户关联的权限策略 |
| [关联组权限](API参考/策略管理接口.md) | PUT | /v1/group/{groupName}/policy/{policyName} | 为用户组关联权限策略 |
| [解除组权限](API参考/策略管理接口.md) | DELETE | /v1/group/{groupName}/policy/{policyName}policyType={policyType} | 解除用户组关联权限策略 |
| [列举组的权限](API参考/策略管理接口.md) | GET | /v1/group/{groupName}/policy | 列举用户组关联权限策略 |
| [关联角色权限](API参考/策略管理接口.md) | PUT | /v1/role/{roleName}/policy/{policyName} | 为指定角色关联权限策略 |
| [解除角色权限](API参考/策略管理接口.md) | DELETE | /v1/role/{roleName}/policy/{policyName} | 解除指定角色关联的权限策略 |
| [列举角色的权限](API参考/策略管理接口.md) | GET | /v1/role/{roleName}/policy | 列举指定角色关联的权限策略 |
| [列举权限授予的主体](API参考/策略管理接口.md) | GET | /v1/policy/{policyId}/grant/{grantType} | 按授予类型列举策略被授予主体 |
| [列举权限授予的所有主体](API参考/策略管理接口.md) | GET | /v1/policy/{policyId}/entity | 列举策略被授予的所有主体 |

### 组管理接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建组](API参考/组管理接口.md) | POST | /v1/group | 创建用户组 |
| [查询组](API参考/组管理接口.md) | GET | /v1/group/{groupName} | 查询指定用户组信息 |
| [更新组](API参考/组管理接口.md) | PUT | /v1/group/{groupName} | 更新指定用户组信息 |
| [删除组](API参考/组管理接口.md) | DELETE | /v1/group/{groupName} | 删除指定用户组 |
| [列举组](API参考/组管理接口.md) | GET | /v1/group | 列举所有用户组 |
| [添加用户到组](API参考/组管理接口.md) | PUT | /v1/group/{groupName}/user/{userName} | 将指定用户添加到组 |
| [从组内移除用户](API参考/组管理接口.md) | DELETE | /v1/group/{groupName}/user/{userName} | 从指定组移除用户 |
| [列举用户的组](API参考/组管理接口.md) | GET | /v1/user/{userName}/group | 列举用户所在的所有组 |
| [列举组内用户](API参考/组管理接口.md) | GET | /v1/group/{groupName}/user | 列举指定组内的用户 |

### 角色管理接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建角色](API参考/角色管理接口.md) | POST | /v1/role | 创建角色 |
| [查询角色](API参考/角色管理接口.md) | GET | /v1/role/{roleName} | 查询指定角色信息 |
| [更新角色](API参考/角色管理接口.md) | PUT | /v1/role/{roleName} | 更新指定角色信息 |
| [删除角色](API参考/角色管理接口.md) | DELETE | /v1/role/{roleName} | 根据角色名删除指定角色。 |
| [列举角色](API参考/角色管理接口.md) | GET | /v1/role | 获取当前账号下的全部角色列表。 |

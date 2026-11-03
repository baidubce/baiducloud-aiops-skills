# baiducloud-data-intelligence-billing API 摘要（自动生成，请勿手改）

> 来源: references/API参考/ ；生成时间: 2026-10-13T20:08:30+08:00
> 由 apidoc-summarizer 生成。

## 地域 Endpoint

| 地域 | 标识 | Endpoint |
| --- | --- | --- |
| 全局 |  | billing.baidubce.com |

## 接口目录

### 代金券

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [代金券、现金券查询接口](API参考/代金券/代金券、现金券查询接口.md) | POST | /v{version}/coupons/list | 分页查询客户名下代金券及现金券详情。 |

### 余额查询相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [信用额度查询](API参考/余额查询相关接口/信用额度查询.md) |  |  | 查询账户的信用额度信息。 |
| [账户余额查询](API参考/余额查询相关接口/账户余额查询.md) | POST | /v{version}/finance/cash/balance | 查询账号的余额。 |

### （未分组）

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [功能更新记录](API参考/功能更新记录.md) |  |  | 记录财务系统接口功能更新历史。 |
| [接口规范](API参考/接口规范.md) |  |  | 财务系统API请求响应格式标准与公共头。 |
| [简介](API参考/简介.md) |  |  | 介绍财务系统OPEN API服务及接口类型。 |
| [访问控制](API参考/访问控制.md) |  |  | 说明签名申请、鉴权及多用户访问控制。 |
| [通用说明](API参考/通用说明.md) | PUT | /v1/cluster/{clusterUuid} | 说明接口域名、协议、版本及实名认证要求 |
| [错误返回](API参考/错误返回.md) |  |  | 说明API错误码格式与公共错误码 |

### 成本相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [成本分摊](API参考/成本相关接口/成本分摊.md) | GET | /v{version}/bill/share/bill | 分页获取分摊账单，主账户可查子账户。 |
| [成本拆分](API参考/成本相关接口/成本拆分.md) | GET | /v{version}/bill/cost/split/bill/list | 分页获取按天或按月聚合的成本拆分账单。 |

### 订单

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [创建续费订单API](API参考/订单/创建续费订单API.md) | POST | /v1/order/renew | 创建指定产品资源的续费订单。 |
| [续费至统一到期日接口](API参考/订单/续费至统一到期日接口.md) |  |  | 更新资源统一到期日设置。 |
| [订单取消](API参考/订单/订单取消.md) | POST | /v{version}/order/cancel | 批量取消订单。 |
| [订单支付API](API参考/订单/订单支付API.md) | POST | /v{version}/order/pay | 支付单个订单。 |

### 订单 / 自动续费API

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [自动续费资源列表查询接口getRenewResourceList](API参考/订单/自动续费API.md) | POST | /v{version}/renew/resource/list | 分页获取预付费资源自动续费详情。 |
| [为预付费资源配置自动续费接口createRenewResourceRule](API参考/订单/自动续费API.md) | POST | /v{version}/renew/resource/rule/create | 为预付费资源配置自动续费规则。 |

### 订单 / 订单查询API

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [GetOrderList接口](API参考/订单/订单查询API.md) | POST | / | 分页获取订单详情。 |
| [GetOrdersByUuid接口](API参考/订单/订单查询API.md) | POST | / | 查询指定uuid的订单详情。 |

### 账单相关接口

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| [Python请求示例](API参考/账单相关接口/Python请求示例.md) |  |  | 资源月账单查询的Python代码示例。 |
| [产品月度账单](API参考/账单相关接口/产品月度账单.md) | GET | /v{version}/bill/month/summary | 查询产品月度账单详情，支持按月或同月按天区间 |
| [计费项账单](API参考/账单相关接口/计费项账单.md) | POST | /v{version}/bill/resource/chargeitem | 分页获取后付费资源计费项账单详情 |
| [资源月账单](API参考/账单相关接口/资源月账单.md) | GET | /v{version}/bill/resource/month | 分页获取资源月账单详情 |
| [附录](API参考/账单相关接口/附录.md) |  |  | 提供账单接口相关数据模型定义 |

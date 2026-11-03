# 订单查询API

## GetOrderList接口

### 接口描述

分页获取订单详情。

### 请求结构

Plain Text

```
POST / HTTP/1.1
Host: billing.baidubce.com
Date: Wed, 06 Apr 2019 06:34:40 GMT
Authorization: AuthorizationString
{
  // request body(json)
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 名称 | 类型 | 参数位置 | 描述 | 是否必须 |
| --- | --- | --- | --- | --- |
| uuid | String | RequestBody参数 | 订单ID，为订单系统的唯一键 | 可选 |
| queryAccountId | String | RequestBody参数 | 查询订单账户，若为空则表示当前登陆账户。只有主账户可以代查其财务圈子账户的订单 | 可选 |
| orderType | String | RequestBody参数 | 订单类型，NEW(新购)、RENEW(续费)、SHIFT\_CHARGE(后付费计费方案变更)、DILATATION(升级)、SHRINKAGE(降级)、RESIZE(后付费变配)、COMPENSATE\_TIME(赔付时长)、REFUND(退款)、TRANSFER\_IN(转入)、TO\_PREPAY(后付费转预付费)、TO\_POSTPAY(预付费转后付费)、TIME\_EXPAND(续时订单)，注括号内为解释，参数赋值英文字符 | 可选 |
| status | String | RequestBody参数 | 订单状态， NEED\_PURCHASE（等待支付）,NEED\_CONFIRM（待确认）,CONFIRMED（已确认）,CANCELLED（已取消）, DEFERRED\_CREATE（延迟创建）,READY\_FOR\_CREATE（待创建）,CREATING（创建中）,CREATED（创建完成）,CREATE\_FAILED（创建失败）,EXPIRED（超期）,REFUND\_SUCC（退款成功）,REFUND\_FAILED（退款失败） | 可选 |
| serviceType | String | RequestBody参数 | 产品类型，例：BCC，BOS等 | 可选 |
| productType | String | RequestBody参数 | 计费类型：prepay/ postpay，分别表示预付费/后付费 | 可选 |
| startTime | String | RequestBody参数 | 订单创建时间作为查询条件，时间区间的开始时间，UTC时间，格式yyyy-MM-ddTHH:mm:ssZ | 可选 |
| endTime | String | RequestBody参数 | 订单创建时间作为查询条件，时间区间的结束时间，UTC时间，格式yyyy-MM-ddTHH:mm:ssZ | 可选 |
| pageNo | Integer | RequestBody参数 | 分页查询的页数，从1开始计数，缺省值为1 | 可选 |
| pageSize | Integer | RequestBody参数 | 每页包含的最大数量，最大数量通常不超过1000，缺省值为100。 | 可选 |

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| pageNo |  | Integer |
| pageSize | Integer | 分页查询分页大小 |
| totalCount | Integer | 当前查询条件总条目 |
| orders | List< Order > | 订单详情列表 |

### 请求示例

说明：一次请求最多返回1000个订单的信息。

Plain Text

```
POST /v{version}/order/list HTTP/1.1 
Host: billing.baidubce.com 
ContentType: application/json; charset=utf-8
Content-Length: <Content_Length>
Authorization: authorization string
{
  "uuid":"the uuid of the order",
  "queryAccountId":"your account id",
  "orderType":"REFUND",
  "status":"CREATED",
  "serviceType":"BCC",
  "productType":"prepay",
  "startTime":"2018-01-01T00:00:00Z",
  "endTime":"2019-11-01T00:00:00Z",
  "pageNo":1,
  "pageSize":100
}
  

```

响应示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: d4591fcf-025b-46bc-81eb-91ddda4e27bc
Server: BWS
Date: Tue, 09 Apr 2019 11:01:10 GMT
Content-Type: application/json;charset=UTF-8 
{
    "pageNo": 1,
    "pageSize": 100,
    "totalCount": 60,
    "orders": [
     {
        "uuid": "id",
        "type": "NEW",
        "accountId": "aaaa",
        "serviceType": "SCS",
        "productType": "prepay",
        "subProductType": "",
        "orderItems": [
        {
            "serviceType": "SCS",
            "productType": "prepay",
            "subProductType": "",
            "region": "bj",
            "key": "scs",
             "configurations": [
                 "缓存节点：cache.n1.medium，2个",
                 "类型：Redis",
                 "容量：0G",
                 "代理节点：0"
               ],
               "flavors": [
                    {
                        "name": "cacheNode",
                        "value": "cache.n1.medium",
                        "scale": 1
                    },
                    {
                        "name": "engine",
                        "value": "2",
                        "scale": 1
                    },
                    {
                        "name": "capacity",
                        "value": "0G",
                        "scale": 1
                    },
                    {
                        "name": "proxyNode",
                        "value": "0",
                        "scale": 1
                    }
               ],
              "count": 1,
              "time": 1,
              "timeUnit": "MONTH",
              "pricingDetail": {
                  "cpt2Price": {
                        "price": 340,
                        "catalogPrice": 340
                  },
                  "cpt1Price": null,
                  "policy": null,
                  "customPrice": false,
                   "alterPriceList": null,
                   "bidPrice":null
               },
               "paymentMethod": {
                   "discountRate": 100,
                   "coupons": [],
                   "discountCoupons": []
               },
               "releaseTime": null,
               "resourceActiveTime": null,
               "combinedServiceType": null,
               "resourceIds": null,
               "shortIds":null,
               "resourceIdAndFees": [],
               "catalogPrice": 340,
               "status": null,
               "resourceMappings": null
               }
           ],
           "price": 340,
           "status": "EXPIRED",
           "createTime": "2019-07-18T09:02:44Z",
           "purchaseTime": null,
           "updateTime": "2019-07-25T09:03:12Z",
           "activeTime": null,
           "resourceIds": null,
           "SHOortIds":null,
           "payChannel": "CASH"
       }
    ]
}
```

## GetOrdersByUuid接口

### 接口描述

查询指定 uuid 的订单详情

### 请求结构

Plain Text

```
POST / HTTP/1.1
Host: billing.baidubce.com
Date: Wed, 06 Apr 2019 06:34:40 GMT
Authorization: AuthorizationString
{
  // request body(json)
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 名称 | 类型 | 参数位置 | 描述 | 是否必须 |
| --- | --- | --- | --- | --- |
| uuids | List< String > | RequestBody参数 | 订单ID列表，为订单系统的唯一键。不得为空，最多接受500个 uuid | 必填 |
| queryAccountId | String | RequestBody参数 | 查询订单账户，若为空则表示当前登陆账户。只有主账户可以代查其财务圈子账户的订单 | 可选 |

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| pageNo | Integer | 分页查询编号，从1开始计数 |
| pageSize | Integer | 分页查询分页大小 |
| totalCount | Integer | 当前查询条件总条目 |
| orders | List< Order > | 订单详情列表 |

### 请求示例

Plain Text

```
POST /v{version}/order/getByUuid HTTP/1.1 
Host: billing.baidubce.com 
ContentType: application/json; charset=utf-8
Content-Length: <Content_Length>
Authorization: authorization string
{
  "uuids": [
      "uuid of order A",
      "uuid of order B"
      ],
  "queryAccountId":"your account id"
}
```

### 响应示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: d4591fcf-025b-46bc-81eb-91ddda4e27bc
Server: BWS
Date: Tue, 09 Apr 2019 11:01:10 GMT
Content-Type: application/json;charset=UTF-8 
{
    "pageNo": 1,
    "pageSize": 100,
    "totalCount": 100,
    "orders": [
     {
        "uuid": "id",
        "type": "NEW",
        "accountId": "aaaa",
        "serviceType": "SCS",
        "productType": "prepay",
        "subProductType": "",
        "orderItems": [
        {
            "serviceType": "SCS",
            "productType": "prepay",
            "subProductType": "",
            "region": "bj",
            "key": "scs",
             "configurations": [
                 "缓存节点：cache.n1.medium，2个",
                 "类型：Redis",
                 "容量：0G",
                 "代理节点：0"
               ],
               "flavors": [
                    {
                        "name": "cacheNode",
                        "value": "cache.n1.medium",
                        "scale": 1
                    },
                    {
                        "name": "engine",
                        "value": "2",
                        "scale": 1
                    },
                    {
                        "name": "capacity",
                        "value": "0G",
                        "scale": 1
                    },
                    {
                        "name": "proxyNode",
                        "value": "0",
                        "scale": 1
                    }
               ],
              "count": 1,
              "time": 1,
              "timeUnit": "MONTH",
              "pricingDetail": {
                  "cpt2Price": {
                        "price": 340,
                        "catalogPrice": 340
                  },
                  "cpt1Price": null,
                  "policy": null,
                  "customPrice": false,
                   "alterPriceList": null,
                   "bidPrice":null
               },
               "paymentMethod": {
                   "discountRate": 100,
                   "coupons": [],
                   "discountCoupons": []
               },
               "releaseTime": null,
               "resourceActiveTime": null,
               "combinedServiceType": null,
               "resourceIds": null,
               "shortIds":null,
               "resourceIdAndFees": [],
               "catalogPrice": 340,
               "status": null,
               "resourceMappings": null
               }
           ],
           "price": 340,
           "status": "EXPIRED",
           "createTime": "2019-07-18T09:02:44Z",
           "purchaseTime": null,
           "updateTime": "2019-07-25T09:03:12Z",
           "activeTime": null,
           "resourceIds": null,
           "SHOortIds":null,
           "payChannel": "CASH"
       sh }
    ]
}
```

## 数据类型

### Model对象定义

#### Order 订单

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| uuid | String | 订单的业务主键，按id获取订单使用该主键 |

|type|String|订单类型
|accountId|String|订单所有者账户ID
|serviceType|String|产品类型，例：BCC，BOS等
|productType|String|计费类型：prepay/ postpay / postpay\_\_prepay，分别表示预付费/后付费/预付费和后付费组合类型
|subProductType|String|付费类型(后付费计费方式)，比如bandwidth, network
|orderItems|List< OrderItem >|订单项列表, 一个订单项对应一组同配置的产品
|orderFee|Fee|订单金额明细
|price|BigDecimal|订单总金额，单位：元
|status|String|订单主状态
|createTime|String|订单创建时间，utc时间
|purchaseTime|String|订单的扣费成功时间，utc时间
|updateTime|String|订单更新时间，utc时间
|activeTime|String|订单生效时间，utc时间
|resourceIds|List< String >|订单创建/更新的资源uuid列表
|shortIds|List< String >|订单创建/更新的资源短列表，与resourceIds列表元素一一对应，若无短ID，则用「「’/’标志。
|payChannel|String|财务支付方式
|isAutoPayed|Boolean|是否是API支付的订单
|autoRenewOrder|Boolean|是否是自动续费来源的订单

#### Fee 计费明细

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| price | BigDecimal | 总目录价 |
| cash | BigDecimal | 实付现金 |
| coupon | BigDecimal | 实付代金券额度 |
| discountCoupon | BigDecimal | 实付折扣券额度 |
| cashEquivalentCoupon | BigDecimal | 实付现金券额度 |
| discountAmount | BigDecimal | 折扣额度 |
| agentCash | BigDecimal | 代理商代付现金 |
| agentRebateIn | BigDecimal | 代理商代付返点 |
| cashEquivalents | BigDecimal | 现金等价物 |
| refundCash | BigDecimal | 实际退现金额 |
| refundCoupon | BigDecimal | 实际退代金券额 |
| catalogPrice | BigDecimal | 目录价 |
| alterPrice | BigDecimal | 订单改价的优惠金额 |

#### OrderItem 订单项

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| serviceType | String | 产品类型，例：BCC，BOS等 |
| productType | String | 计费类型：prepay/ postpay，分别表示预付费/后付费 |
| subProductType | String | 计费子类型，例如按流量或按带宽计费 |
| region | String | 区域 |
| key | String | 用于区分不同订单项的标识 |
| configurations | List< String > | 配置列表 |
| flavors | List | 英文配置 |
| count | int | 购买资源的份数（如，BCC的台数) |
| time | BigDecimal | 预付费订单中表示购买的资源时长，默认单位：月；后付费订单中无购买时长 |
| timeUnit | String | 购买时长的时间单位 |
| pricingDetail | PricingDetail | 价格明细 |
| paymentMethod | PaymentMethod | 支付方式 |
| releaseTime | String | 资源定时释放时间 |
| resourceActiveTime | String | 非空则指定资源激活开始时间 |
| combinedServiceType | String | 合并购买中的组合订单 |
| itemFee | Fee | 订单项费用明细 |
| resourceIds | List | 订单关联的资源(创建后的资源)uuid列表 |
| shortIds | List< String > | 订单关联的资源(创建后的资源)短ID列表，与resourceIds列表元素一一对应，若无短ID，则用’/’标志。 |
| resourceIdAndFees | List< ResourceIdAndFee > | 订单关联的各资源fee |
| resourceStartTime | String | 订单影响的资源的开始时间 |
| resourceEndTime | String | 订单影响的资源的结束时间 |
| catalogPrice | BigDecimal | 目录价 |
| realCatalogPrice | BigDecimal | 订单的原始价格，如果有多年多折，取多年多折原价，有活动价，取的是目录价 |
| status | String | 活动组合订单的订单项状态 |
| resourceMappings | List< ResourceMapping > | 活动组合订单的订单项相关绑定资源 |

#### PricingDetail 价格明细

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| cpt2Price | Cpt2Price | 包年包月计费 |
| cpt1Price | BigDecimal | 固定配置，按分钟计费 |
| policy | String | 定价策略 |
| alterPriceList | AlterPriceList | 改价列表 |
| bidPrice | BidPrice | 出价信息 |

#### Cpt2Price 包年包月计费

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| price | BigDecimal | 实际价格 |
| catalogPrice | BigDecimal | 目录价 |

#### BidPrice 竞价详情

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| bidModel | String | 出价模型 |
| bidPrice | BigDecimal | 出价金额 |

#### PaymentMethod 支付方式

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| discountRate | Integer | 折扣率，90表示90% |
| coupons | List< CouponInfo > | 代金券信息 |
| discountCoupons | List< CouponInfo > | 折扣券信息 |

#### CouponInfo 代金券详情

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| couponId | String | 代金券号 |
| amount | BigDecimal | 代金券金额，单位：元，精确到小数点后两位 |

#### ResourceIdAndFee 资源价格详情

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| resourceId | String | 资源ID |
| resourceFee | Fee | 资源计费价格详情 |

#### ResourceMapping 资源详情

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| key | String | 资源ID |
| id | String | 资源ID |
| shortId | String | 资源短ID |
| status | String | 资源状态 |
| expiredTime | String | 过期时间 |

#### 订单状态枚举说明

| 枚举 | 状态 | 控制台展示名称 | 终态 | 说明 |
| --- | --- | --- | --- | --- |
| NEED\_PURCHASE | 待支付 | 未支付 | 否 | 用户下单之后，如需支付，则立即进入此状态 |
| CANCELLED | 取消 | 已取消 | 是 | 用户从控制台发起取消，则进入此状态 |
| DEFERRED\_CREATE | 延迟生效 | 已支付 / 已生效（账期）/ 抢占中（竞价实例） | 否 | 改变资源的计费方式后，但尚未到订单的生效时间，此时订单处于延迟创建状态，等到了订单的生效时间，订单进入待创建状态 |
| READY\_FOR\_CREATE | 待创建 | 已支付 / 已生效（账期） | 否 | 用户支付完成后，进入该状态 |
| CREATING | 创建中 | 已支付 / 已生效（账期） | 否 | 表示产品方正在创建资源 |
| CREATED | 已创建 | 已支付 / 已生效（账期） | 是 | 表示产品方已创建资源完成。注意：此状态是订单的终态，不允许改变。 |
| CREATE\_FAILED | 创建失败 | 已作废 | 是 | 表示产品方创建资源失败。 |
| EXPIRED | 已过期 | 已作废 | 是 | 订单超期，导致被取消。注意：活动订单超期时间是 12 小时；普通订单的超期时间是 7 天。 |
| REFUND\_SUCC | 退款成功 | 已作废 | 是 | 如果订单需要退款，且退款完成，则会进入该状态。 注意：这个状态仅针对有支付且创建失败的订单；对于退款订单，进入 CREATED 状态后自动进入退款逻辑，退款完成后状态仍处于 CREATED。 |
| REFUND\_FAILED | 退款失败 | 已支付 | 是 | 如果订单需要退款，且退款失败，则会进入该状态。 |

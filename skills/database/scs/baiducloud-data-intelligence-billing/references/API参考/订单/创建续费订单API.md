# 创建续费订单API

## 创建续费订单接口

## renew接口

### 接口描述

创建特定产品下，指定资源及其关联资源的续费订单。

### 权限说明

请求发起人需要具有合法的AccessKeyID和SecretAccessKey才能发起请求，请参考[鉴权认证](/doc/Reference/s/Njwvz1wot)。

### 注意事项

如果请求中没有用户验证信息（即匿名访问），返回403 Forbidden，错误信息：AccessDenied。
下单请求 QPS 在100以内。

### 请求结构与示例

Plain Text

```
POST /v1/order/renew HTTP/1.1 
Host: billing.baidubce.com 
ContentType: application/json
Authorization: authorization string
```

### 请求示例

Plain Text

```
{
  "accountId": "your account id",
  "serviceType": "BCC",
  "region": "bj",
  "renewItems": [
    {
      "instanceId": "instance ShortId",
      "time": 1,
      "timeUnit": "YEAR"
    }
  ],

}
```

### 请求参数

| 名称 | 类型 | 参数位置 | 描述 | 是否必须 |
| --- | --- | --- | --- | --- |
| accountId | String | body参数 | 账户 id，可以查询自己及下级账号的续费资源。不传则查当前账户的续费资。账户 id 需要和待续费资源的 id 一致 | 是 |
| serviceType | String | body参数 | 产品名称 | 是 |
| region | String | body参数 | 区域英文名 | 是 |
| renewItems | List | body参数 | 续费资源项。最多支持100个资源同时续费 | 是 |
| RenewItem→instanceId | String | body参数 | 资源实例的长ID，或者是短ID | 是 |
| RenewItem→time | Int | body参数 | 续费时长，正整数。 | 是 |
| RenewItem→timeUnit | String | body参数 | 续费单位。见附录TimeUnit可选值 | 是 |

### 返回参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| success | Boolean | 续费是否成功 |
| orderId | String | 创建成功的续费订单ID |
| busyResourceInfo | List | 因重复下单导致的续费失败时，返回重复下单的订单和资源信息。续费成功时，此字段为空 |
| BusyResourceInfo→orderId | String | 冲突资源对应的订单 id |
| BusyResourceInfo→orderId | String | 冲突资源长 id |

### 返回示例一

Plain Text

```
{
  "success": true,
  "orderId": "createdOrderId"
}
```

### 返回示例二

Plain Text

```
{
  "success":  false,
  "busyResourceInfo":  [
    {
      "orderId": "busyOrderId",
      "resourceName": "busyResourceName"
    }
  ]
}
```

### 附录

**TimeUnit代码**

| TimeUnit | 说明 |
| --- | --- |
| YEAR | 年 |
| MONTH | 月 |

**region代码**

| 地区 | region |
| --- | --- |
| 华北 - 北京 | bj |
| 华北 - 保定 | bd |
| 华南 - 广州 | gz |
| 华东 - 苏州 | su |
| 香港 | hkg |
| 全局产品 | global |

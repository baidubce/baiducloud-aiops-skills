# 预付费转后付费API

## 请求说明

通过调用API接口来执行预付费转后付费。

* 预付费转后付费延迟生效。仅在预付费实例到期后自动变更为后付费，生成转换任务的实例不支持进行其他订单相关操作（比如变配、续费等）。
* 仅预付费实例支持变更
* 处于待变更状态的实例不支持重复变更
* 开通自动续费的实例不支持计费变更
* 已到期的实例不支持计费变更

## 请求结构

Plain Text

```
POST /v1/instance/toPostpay HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{    
    "instanceIds": [
        "scs-bj-woxuukeunrju",
        "scs-bj-rfdlbypsafhi"
    ]
}
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceIds | List<String> | Body | 是 | 集群ID列表。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| orderId | String | 订单ID。多个集群同时变更会产生多个订单，订单以英文逗号分隔。 |

## 请求示例

Plain Text

```
POST /v1/instance/toPostpay  HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{    
    "instanceIds": [
        "scs-bj-woxuukeunrju",
        "scs-bj-rfdlbypsafhi"
    ]
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "orderId": "xxx"
}
```

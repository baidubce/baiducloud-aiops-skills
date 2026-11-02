# 续费API

## 请求说明

对于预付费实例，通过调用API接口来执行续费操作。

* 本接口用于对已有的预付费实例进行续费。
* 如果预付费实例在回收站中,续费后会从回收站中恢复。
* 续费接口为异步变更，可通过查询指定实例详情接口查询实例状态。
* 当前版本为v1。

## 请求结构

Plain Text

```
POST /v1/instance/renew HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{    
    "duration":1,
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
| duration | Integer | Body | 是 | 转预付费的时长，单位月。最小值1。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| orderId | String | 订单ID。 |

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ozgdsbsqqnxi/clusterTypeChange HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{    
    "duration":1,
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

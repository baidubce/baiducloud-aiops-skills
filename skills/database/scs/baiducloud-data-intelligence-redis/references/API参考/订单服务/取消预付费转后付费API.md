# 取消预付费转后付费API

## 请求说明

通过调用API接口来取消计费变更。

* 只有计费变更没有生效之前可以取消。

## 请求结构

Plain Text

```
POST /v1/instance/cancelToPostpay HTTP/1.1
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

无。

## 请求示例

Plain Text

```
POST /v1/instance/cancelToPostpay HTTP/1.1
HOST: redis.{region}.baidubce.com
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
```

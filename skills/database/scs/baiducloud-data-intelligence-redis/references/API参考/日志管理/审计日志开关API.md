# 审计日志开关API

## 请求说明

* 该 API 对应的控制台操作为开启或关闭**审计日志**。
* 审计日志仅**Redis内存型4.0 6.0 7.0**版本支持。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/log/audit/switch HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| action | String | Body | 是 | 开关动作。open（开启）、close（关闭） |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无特殊返回参数。

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-oqdgnbjfogjw/log/audit/switch  HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{
    "action": "close"
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
```

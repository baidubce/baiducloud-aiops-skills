# 删除 内存弹性扩缩API

### 请求说明

* 删除实例的内存弹性扩缩配置。
* 目前仅标准版实例支持。

### 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/deleteAutoScalingConfig
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | 实例ID |

### 返回头域

除公共头域，无其它特殊头域。

### 返回参数

无。

### 请求示例

Plain Text

```
POST /v1/instance/{instanceId}/deleteAutoScalingConfig
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 返回示例

Plain Text

```
 HTTP/1.1 200 OK
 x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
 Content-Type: application/json
```

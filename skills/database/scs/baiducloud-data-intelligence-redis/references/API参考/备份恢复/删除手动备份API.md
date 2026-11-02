# 删除手动备份API

### 请求说明

* 通过调用API来删除手动备份。

### 请求结构

Plain Text

```
DELETE /v1/instance/{instanceId}/backup/{batchId} HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| batchId | String | Path | 是 | 备份ID。 |

  

### 返回头域

除公共头部，无其它特殊头部。

### 返回参数

无。

### 请求示例

Plain Text

```
DELETE /v1/instance/{instanceId}/backup/{batchId} HTTP/1.1
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

# 获取备份的URL API

### 请求说明

* 通过调用API来获取备份的URL。

### 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/backup/{backupId}/url  HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| backupId | Integer | Path | 是 | 备份ID。 |

  

### 返回头域

除公共头部，无其它特殊头部。

### 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| url | String | 下载地址。 |
| urlExpiration | Integer | 过期时间，单位秒。 |

### 请求示例

Plain Text

```
GET /v1/instance/{instanceId}/backup/{backupId}/url  HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
  "url": "http://bos-sandbox-bj.baidu-int.com/scs-backup-rdb-bucket/expiration7/2680_11029_4f2082af-052d-4446-b517-787e259b26b0?authorization=bce-auth-v1%2Fce16d1f34a4e4b5481769e19322ff0d7%2F2019-08-29T11%3A42%3A33Z%2F1800%2Fhost%2Fbfec628b70b4e5f93b74903d6be86f47259849bfa8206afcf07a23a0e688b4d6",
  "urlExpiration": 1800
}
```

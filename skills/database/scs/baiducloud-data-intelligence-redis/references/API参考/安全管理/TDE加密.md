# TDE加密

## TDE加密

### 接口描述

本接口用于开启TDE加密。

本接口为v1接口。

**注意事项**

* 支持Redis标准版6.0集群
* 热活组中的实例不支持此操作，并且开启后的实例不支持加入热活组中
* 开启TDE加密后不支持关闭
* 开启TDE加密后历史备份不支持恢复
* 开启TDE加密后不支持大key分析功能

### 请求结构

Plain Text

```
POST /v{version}/instance/{instanceId}/tde HTTP/1.1
Host: redis.bj.baidubce.com
Authorization: authorization string
{
  "action": "open"
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| version | String | 是 | PATH参数 | API版本号。此处值为1。 |
| instanceId | String | 是 | PATH参数 | 集群ID。 |
| action | String | 是 | RequestBody参数 | 开启TDE加密。参数可选值：open |

  

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| operateStatus | String | 操作状态。仅成功时返回success |
| errorMessage | String | 操作失败原因。该值为空，无实际意义。 |

  

### 请求示例

Plain Text

```
POST http://redis.bj.baidubce.com/v1/instance/scs-bj-bmacccxilppn/tde
Host: redis.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
  "action": "open"
}
```

### 响应示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Date: Wed, 08 Jul 2015 03:28:11 GMT
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
Server: BWS
{
    "operateStatus": "success",
    "errorMessage": ""
}
```

Plain Text

```
HTTP/1.1 400 Bad Request
Content-Type: application/json;charset=UTF-8
Date: Wed, 08 Jul 2015 03:28:11 GMT
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
Server: BWS
{
    "requestId": "a43bf34f-0c20-4a63-8ec7-d14a369d0f64",
    "code": "ClusterStatusForbidden",
    "message": "The cluster status forbidden operation."
}
```

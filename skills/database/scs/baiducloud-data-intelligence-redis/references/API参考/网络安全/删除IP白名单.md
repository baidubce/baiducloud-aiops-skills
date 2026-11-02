# 删除IP白名单

### 请求说明

* 设置可以访问实例的IP白名单。

### 请求结构

Plain Text

```
DELETE /v1/instance/{instanceId}/securityIp?clientToken={clientToken} HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
{
  "securityIps": ["securityIps0"，"securityIps1"]
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| clientToken | String | 是 | URL参数 | 幂等性Token，是一个长度不超过64位的ASCII字符串 |
| instanceId | String | 是 | URL参数 | 实例Id |
| securityIps | List<String> | 是 | RequestBody参数 | IP白名单分组下的IP列表。包括常规地址: 如192.168.0.1，CIDR地址: 如192.168.1.0/24，0.0.0.0/0代表允许所有地址 |

### 返回头域

除公共头部，无其它特殊头部。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
DELETE /v1/instance/scs-bj-ykfiztgpxjny/securityIp HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
  "securityIps": ["192.0.0.1"]
}
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
```

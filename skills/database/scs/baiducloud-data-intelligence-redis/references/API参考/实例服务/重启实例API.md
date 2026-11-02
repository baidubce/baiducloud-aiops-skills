# 重启实例API

### 请求说明

* 重启单个redis实例,不支持重启memcache。
* 重启后Redis实例状态变更为重启中，重启成功后变更为运行中。
* 重启过程中可能会有分片数\*5秒内的闪断，请选择业务低峰期进行，并确保应用具有自动重连机制。
* 注：对于单副本实例，实例重启将导致数据丢失，请谨慎操作。

### 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/restart HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求参数

| 参数 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | Path | 实例ID |
| isDefer | Boolean | 否 | Body | 执行时机。- false：立即执行 - true：维护时间内执行 |

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ykfiztgpxjny/restart HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

### 返回示例

Plain Text

```
 HTTP/1.1 200 OK
 x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
 Content-Type: application/json
```

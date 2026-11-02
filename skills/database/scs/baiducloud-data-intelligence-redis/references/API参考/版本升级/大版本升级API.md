# 大版本升级API

### 请求说明

* 通过调用API升级实例的内核版本。

### 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/upgradeVersion HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无特殊其他头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| kernelVersion | String | Body | 否 | 升级大版本时的版本号。非大版本升级时为空。- 升级版本要高于现在的版本。 - 3系标准版可以升级到6系、7系 - 4系可以升级到6系、7系 - 5系可以升级到6系、7系 - 6系可以升到7系 |
| isDefer | Boolean | Body | 否 | 执行时间。- false：立即执行 - true：维护时间内执行 |

  

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
POST  /v1/instance/scs-bj-ykfiztgpxjny/upgradeVersion HTTP/1.1
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

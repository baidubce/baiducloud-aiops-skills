# 代理版本升级or重启 API

### 请求说明

* 通过调用API升级实例的代理版本。

### 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/upgradeProxy HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无特殊其他头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | URI | 是 | 集群ID |
| proxyList | List<String> | RequestBody参数 | 否 | 升级任务为空 重启任务不为空。- 填写批量重启的proxy的showId |
| upgradeType | String | RequestBody参数 | 是 | 任务类型。- relaunch：重启proxy； - latest：升级proxy版本 |
| isDefer | Boolean | RequestBody参数 | 否 | 是否延迟执行，默认false：- false 立即执行 - true 延迟执行(维护时间窗口执行) |

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ykfiztgpxjny/upgradeProxy HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json  
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
    "proxyList": [],
    "upgradeType":"latest",
    "isDefer": true
}
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
ContentType: application/json
```

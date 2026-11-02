# 清空实例API

### 请求说明

* 清空单个Redis实例的数据。
* 对Redis实例，清空后表现为数据占用内存下降，数据被清空。

### 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/flush HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{
 "password":"password",
 "dbIndex": 0
}
```

### 请求头域

除公共头域外，无特殊其他头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| password | String | Body | 是 | 实例密码，如果没有设置密码，传递空字符串，密码需要加密传输，禁止明文传输，详情请参考[密码加密传输规范定义](https://cloud.baidu.com/doc/SCS/s/fjwvxtrd9#%E5%AF%86%E7%A0%81%E5%8A%A0%E5%AF%86%E4%BC%A0%E8%BE%93%E8%A7%84%E8%8C%83%E5%AE%9A%E4%B9%89) |
| dbIndex | Integer | Body | 否 | 数据库索引，取值为：[0,255] |
| isFlushExpired | Boolean | Body | 否 | true=只清理过期数据, false=清理所有数据 |
| isDefer | Boolean | Body | 否 | 维护时间窗口执行, 仅isFlushExpired=true时可用。- true：维护时间执行，false：立即执行。 |

  

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ykfiztgpxjny/flush HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
 "password":"password",
 "dbIndex": 0
}
```

### 返回示例

Plain Text

```
 HTTP/1.1 200 OK
 x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
 Content-Type: application/json
```

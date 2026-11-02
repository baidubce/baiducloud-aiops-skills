# 设置备份策略API

### 请求说明

* 通过调用API来设置redis实例自动备份策略。

### 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/backup/modifyPolicy  HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
{
   "backupDays": "Sun,Mon,Tue,Wed,Thu,Fri,Sta",
   "backupTime": "01:05:00",
   "expireDay": 7,
   "isEncrypt": "yes"
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| backupTime | String | Body | 否 | 备份时间。- 未填写该参数时，备份时间默认修改为1:05:00。 |
| backupDays | String | Body | 是 | 备份周期。 |
| expireDay | Integer | Body | 是 | 备份文件保留时长，可选范围： 1-15天 |
| isEncrypt | String | Body | 是 | 是否开启加密 no 不开启 yes 开启 |

### 返回头域

除公共头部，无其它特殊头部。

### 返回参数

无。

### 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ykfiztgpxjny/backup/modifyPolicy HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
   "backupDays": "Sun,Mon,Tue,Wed,Thu,Fri,Sta",
   "backupTime": "01:05:00",
   "expireDay": 7,
   "isEncrypt": "yes"
}
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
```

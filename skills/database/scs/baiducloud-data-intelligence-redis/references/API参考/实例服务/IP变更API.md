# IP变更API

## 请求说明

**云数据库Redis**支持通过调用API进行**内网IP变更**。

* VPC默认不变，可用区、子网默认选择与主节点一致。
* 修改网络地址生效后，会断开旧地址上的所有网络连接（旧地址不可用）。请确保业务使用连接地址（域名）连接实例。并确保迁移后DNS缓存及时刷新，且应用程序具备断线重连机制。
* **Redis社区版、集群版、容量版**均支持IP变更功能。
* **变更IP**不支持热活实例组、多活实例组，只读节点。
* **变更IP**不支持开通外网ip。
* BLB专属集群的实例不支持变更内网ip。

## 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/azoneMigration/modifyEntrance
Host: redis.bj.baidubce.com
Authorization: authorization string
{
    "isDefer":"true"
}
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID。 |
| isDefer | Boolean | Body | 是 | 是否维护时间内执行。- true：维护时间内执行 - false：立即执行 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无。

## 请求示例

Plain Text

```
POST /v1/instance/{instanceId}/azoneMigration/modifyEntrance
Host: redis.bj.baidubce.com
Authorization: authorization string
{
    "isDefer":"true"  
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

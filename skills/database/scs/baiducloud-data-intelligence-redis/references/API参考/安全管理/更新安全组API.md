# 更新安全组API

## 请求说明

通过调用API来更新Redis的安全组。 更新后会替换之前所有已经绑定的安全组为新的安全组。

## 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/securityGroup/update HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{
        "securityGroupIds": [
            "g-0qdtc2bzp0gd"
        ]
    }
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| securityGroupIds | List<String> | Body | 是 | 绑定的安全组ID列表。 |

## 返回头域

除公共头域外，无其它特殊头域。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| success | Boolean | 是否成功。 |

## 请求示例

Plain Text

```
 POST /v1/instance/scs-bdbl-ynqvbwopdesj/securityGroup/bind HTTP/1.1
 Host: redis.bj.baidubce.com
 Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
    {
        "securityGroupIds": [
            "g-0qdtc2bzp0gd"
        ]
    }
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Date: Wed, 08 Jul 2015 03:28:11 GMT
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
Server: BWS
{
        "success": true
 }
```

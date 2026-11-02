# 开启或关闭TLS加密API

## 请求说明

通过调用API来开启Redis的TLS访问。开启TLS访问，将会重启实例，请在低峰期操作。

## 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/tls HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
{
    "action": "open"
}
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| action | String | Body | 是 | open：开启；close：关闭；update：更新证书有效期。开启加密之后才能进行更新。 |

## 返回头域

除公共头域外，无其它特殊头域。

## 返回参数

无。

## 请求示例

Plain Text

```
POST /v1/instance/scs-bj-elahimuhxjia/tls HTTP/1.1
HOST: redis.bj.baidubce.com
ContentType: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
    "action": "open"
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
```

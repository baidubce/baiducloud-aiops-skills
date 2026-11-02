# 创建部署集API

## 请求说明

通过调用API来创建部署集。

## 请求结构

Plain Text

```
POST /v1/deploySet HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
{
    "name": "clltest11",
    "strategy": "HOST_HA",
    "concurrency": 2
}
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| name | String | Body | 是 | 部署集名称。 |
| desc | String | Body | 否 | 备注。 |
| strategy | String | Body | 是 | 策略。默认值：HOST\_HA。 |
| concurrency | Integer | Body | 是 | 并发度。取值范围：1-127。默认值：20。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| deploySetId | String | 部署集ID。 |

## 请求示例

Plain Text

```
POST /v1/deploySet HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
    "name": "clltest11",
    "desc": "clltest11",
    "strategy": "HOST_HA",
    "concurrency": 2
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
     "deploySetId": "dset-72f5618f-f976-4d35-8fe4-1618ab6fec03"
 }
```

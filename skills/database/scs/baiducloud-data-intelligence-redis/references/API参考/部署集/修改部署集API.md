# 修改部署集API

## 请求说明

通过调用API修改部署集。

## 请求结构

Plain Text

```
PUT /v1/deploySet/{deploySetId} HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| deploySetId | String | Path | 是 | 部署集ID。 |
| desc | String | Body | 否 | 备注。 |
| name | String | Body | 是 | 部署集名称。 |
| concurrency | Integer | Body | 是 | 并发度。取值范围：1-127。默认值：20。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无特殊返回参数。

## 请求示例

Plain Text

```
PUT /v1/deploySet/dset-cb0ce309-aee1-4309-b041-85532fe36738 HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json   
Authorization: bce-auth-v1/0255cb4f78f140728045b551d6a317ec/2018-11-13T05:46:05Z/1800/host/70268ec1d0491c86e67f345ad3aee4cf7f8924dade9b7f3e2f1a95814a00c129
{
    "name": "clltest9",
    "concurrency": 20,
    "desc": "clltest91"
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 1214cca7-4ad5-451d-9215-71cb844c0a50
Content-Type: application/json;charset=UTF-8
```

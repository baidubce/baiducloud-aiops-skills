# 获取部署集列表API

## 请求说明

通过调用API来获取部署集列表。

## 请求结构

Plain Text

```
GET /v1/deploySet?maxKeys=1&marker=-1 HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| marker | String | Query | 否 | 批量获取列表的查询的起始位置，是一个由系统生成的字符串。默认-1。 |
| maxKeys | Integer | Query | 否 | 每页包含的最大数量(主实例)，最大数量通常不超过1000，缺省值为1000。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| result | List<Deploy> | 部署集列表。 |
| marker | String | 批量获取列表的查询的起始位置，是一个由系统生成的字符串,起始值可传入-1。 |
| isTruncated | Boolean | true表示后面还有数据，false表示已经是最后一页 |
| nextMarker | String | 获取下一页所需要传递的marker值。当isTruncated为false时，该域不出现。 |
| maxKeys | Integer | 每页包含的最大数量，最大数量通常不超过1000，缺省值为1000。 |

### Deploy

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| scsInstanceCount | Integer | 部署集绑定的实例数量。 |
| scsInstancelds | List<String> | 部署集绑定的SCS集群ID列表。 |
| name | String | 部署集名称。 |
| strategy | String | 策略。默认值：HOST\_HA。 |
| concurrency | Integer | 并发度。 |
| deploySetId | String | 部署集ID。 |
| desc | String | 备注。 |

## 请求示例

Plain Text

```
GET /v1/deploySet?maxKeys=1&marker=-1 HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json   
Authorization: bce-auth-v1/0255cb4f78f140728045b551d6a317ec/2018-11-13T05:46:05Z/1800/host/70268ec1d0491c86e67f345ad3aee4cf7f8924dade9b7f3e2f1a95814a00c129
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "result": [
        {
            "scsInstanceCount": 0,
            "name": "ceshi",
            "strategy": "HOST_HA",
            "concurrency": 1,
            "deploySetId": "dset-52aaf380-dd37-47a2-b999-70af061a5118",
            "desc": "for_test"
        }
    ],
    "marker": "-1",
    "isTruncated": true,
    "nextMarker": "dset-3978b624-a9b7-45b8-8a40-3fc107686c35",
    "maxKeys": 1
}
```

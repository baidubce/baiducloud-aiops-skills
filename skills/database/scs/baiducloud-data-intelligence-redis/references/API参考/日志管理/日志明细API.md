# 日志明细API

## 请求说明

* 查询实例的某一个日志的明细信息。
* **日志详情**仅**Redis内存型**支持。

## 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/log/{logId} HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| logId | String | Path | 是 | 日志ID |
| validSeconds | String | Query | 否 | 下载有效时间，单位s。默认值1800。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| logId | String | 日志ID |
| downloadUrl | String | 日志下载链接 |
| downloadExpire | String | 下载链接到期时间 |

## 请求示例

Plain Text

```
GET /v1/instance/scs-bj-oqdgnbjfogjw/log/scs-bj-oqdgnbjfogjw_67140_runlog_202410111430
HOST: redis.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "logId": "scs-bj-oqdgnbjfogjw_67140_runlog_202410111430",
    "downloadUrl": "https://bj.bcebos.com/scs-log-download-bj/scs-bj-oqdgnbjfogjw_67140_runlog_202410111430?authorization=bce-auth-v1%2F91884b9e79a442f29f8b41106d060e72%2F2024-10-12T10%3A58%3A56Z%2F1800%2Fhost%2F6689fc40ebad827fe774d47e510df6c461ae2bf649598f49de89ea83d398e1ea",
    "downloadExpires": "2024-10-12 19:28:56"
}
```

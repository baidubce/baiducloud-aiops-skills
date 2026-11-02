# 日志列表API

## 请求说明

* 该 API 对应的控制台操作为日志列表。 您可以查看7天内的运行日志、慢日志、审计日志，寻找解决运维问题的线索。
* 审计日志仅**Redis 4.0 6.0 7.0**版本支持。
* **日志列表**仅**Redis内存型**支持。

## 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/log/list?fileType={fileType}&startTime={startTime} HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| fileType | String | Query | 是 | 日志类型，取值范围：- slowlog（慢日志下载列表） - runlog（运行日志下载列表） - auditlog（审计列表） |
| startTime | String | Query | 是 | 开始时间，格式 "yyyy-MM-dd hh:mm:ss" |
| endTime | String | Query | 否 | 结束时间，格式 "yyyy-MM-dd hh:mm:ss"- 未填写该参数，将默认返回开始时间+24小时内的日志。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| logList | List<ShardLog> | 日志列表 |

## ShardLog 分片日志信息

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| shardShowId | String | 分片ID |
| totalNum | Integer | 总数 |
| logItem | List<LogItem> | 分片日志列表 |
| shardId | Integer | 分片数字ID |

## LogItem 单个日志记录

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| logId | String | 日志记录ID |
| logSizeInBytes | Integer | 日志文件大小(单位为字节) |
| logStartTime | String | 日志起始时间点 |
| logEndTime | String | 日志结束时间点 |
| downloadUrl | String | 日志下载链接 |
| downloadExpires | String | 下载链接到期时间 |

## 请求示例

Plain Text

```
GET /v1/instance/scs-bj-oqdgnbjfogjw/log/list?fileType=runlog&startTime=2024-10-11 00:00:00 HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json
 Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{

    "logList": [
        {
            "shardId": 67140,
            "shardShowId": "scs-bj-oqdgnbjfogjw-0",
            "totalNum": 4,
            "logItem": [
                {
                    "logId": "scs-bj-oqdgnbjfogjw_67140_runlog_202410111430",
                    "logSizeInBytes": 35746,
                    "logStartTime": "2024-10-11 14:00:00",
                    "logEndTime": "2024-10-11 14:30:00",
                    "downloadUrl": "https://bj.bcebos.com/scs-log-download-bj/scs-bj-oqdgnbjfogjw_67140_runlog_202410111430?authorization=bce-auth-v1%2F91884b9e79a442f29f8b41106d060e72%2F2024-10-12T10%3A52%3A25Z%2F1800%2Fhost%2Fad748418009dbce23bb73e7adc8a3f5e09d830eb1a6a69f5047cc14cf26dfcd5",
                    "downloadExpires": "2024-10-12 19:22:25"
                }
            ]
        }
    ]
}
```

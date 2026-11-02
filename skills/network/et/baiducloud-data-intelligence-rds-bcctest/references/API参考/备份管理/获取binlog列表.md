# 获取binlog列表

**接口说明**

获取binlog日志列表，该日志列表记录RDS对应数据库引擎日志事务版本链

**请求结构**

Plain Text

```
GET /v{version}/instance/{instanceId}/binlogs/{datetime} HTTP 1.1
HOST: rds.bj.baidubce.com
Authorization: authorization string
```

**请求头域**

除公共头域外，无其它特殊头域

**请求参数**

| 参数名称 | 参数类型 | 是否必须 | 参数位置 | 描述 | 示例值 |
| --- | --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | API版本号 | 1 |
| instanceId | String | 是 | URL参数 | 实例 ID | rds-XWBihCgR |
| datetime | String | 是 | URL参数 | 日志列表备份开始时间,UTC时间 | 2023-09-21T23:00:00Z |

**返回头域**

除公共头域外，无其它特殊头域

**返回参数**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| binlogs | List<Binlogs> | binlog 列表结果 |

**Binlogs字段数据结构说明**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| binlogId | String | binlogId |
| binlogSizeInBytes | Integer | 文件大小，单位mb |
| binlogEndTime | String | binlog文件记录的开始时间 |
| binlogStartTime | String | binlog文件记录的结束时间 |
| binlogStatus | String | binlog日志状态 available |
| binlogRealId | String | 文件名 |

**请求示例**

Plain Text

```
GET /v1/instance/rds-XWBihCgR/binlogs/2023-09-19T12:00:00Z HTTP 1.1
HOST: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475 
Content-Type: application/json
{
 "binlogs": [
    {
     "binlogId": "1695225915328623302",
     "binlogSizeInBytes": 28556,
     "binlogStatus": "available",
     "binlogStartTime": "2023-09-19T16:05:15Z",
     "binlogEndTime": "2023-09-20T16:05:15Z",
     "binlogRealId": "mysql-bin.000002"
    }
 ]
}
```

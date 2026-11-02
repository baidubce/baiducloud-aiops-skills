# 获取pg日志列表

## 获取pg日志列表

### 接口描述

本接口用于获取postgresql数据库日志列表，日志内容默认保留7天。

本接口为v1接口。

### 请求结构

Plain Text

```
GET /v{version}/instance/{instanceId}/pg/list?date={date} HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| version | String | 是 | Path参数 | API版本号 |
| instanceId | String | 是 | Path参数 | 实例ID |
| date | String | 是 | Query参数 | 日期，格式如：2023-06-14 |

  

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| pgLogs | List < PgLogResponse > | pg 日志列表响应结构。 |

**PgLogResponse**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| pglogId | String | 日志id。 |
| pglogSizeInBytes | long | 日志大小。 |
| pglogStartTime | String | 日志开始时间。 |
| pglogEndTime | String | 日志结束时间。 |

  

### 请求示例

Plain Text

```
GET http://rds.bj.baidubce.com/v1/instance/rds-p8tkuOKY/pg/list?date=2024-06-05
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

### 响应示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
Date: Wed, 08 Jul 2015 03:28:11 GMT
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
Server: BWS
{
  "pgLogs": [
    {
      "pglogId": "postgresql-2024-06-06_142752.log",
      "pglogSizeInBytes": 292,
      "pglogStartTime": "2024-06-06T06:27:52Z",
      "pglogEndTime": "2024-06-06T06:28:00Z"
    }
  ]
}
```

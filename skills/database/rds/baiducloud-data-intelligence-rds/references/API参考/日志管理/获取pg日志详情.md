# 获取pg日志详情

## 获取pg日志详情

### 接口描述

本接口用于pg日志详情，供下载使用

本接口为v1接口

### 请求结构

Plain Text

```
GET /v{version}/instance/{instanceId}/pg/download?pglogId={pglogId}&downloadValidTimeInSec={downloadValidTimeInSec} HTTP/1.1
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
| pglogId | String | 是 | Query参数 | pg 日志ID |
| downloadValidTimeInSec | Integer | 否 | Query参数 | 下载链接有效期，单位是秒。默认值3600 |

  

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| pglogId | String | 日志ID。 |
| pglogSizeInBytes | long | 日志大小。 |
| pglogStartTime | String | 日志开始时间。 |
| pglogEndTime | String | 日志结束时间。 |
| downloadUrl | String | 日志下载链接。 |
| downloadExpires | String | 日志下载链接有效期。 |

  

### 请求示例

Plain Text

```
GET http://rds.bj.baidubce.com/v1/instance/rds-pYhTQCEj/pg/download?pglogId=postgresql-2024-06-06_142752.log&downloadValidTimeInSec=172800
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
  "pglogId": "postgresql-2024-06-06_142752.log",
  "pglogSizeInBytes": 292,
  "pglogStartTime": "2024-06-06T06:27:52Z",
  "pglogEndTime": "2024-06-06T07:27:52Z",
  "downloadUrl": "https://backups-bj.bos.bj.baidubce.com/rds/pgsql/pglog/rdsgwqlv98g87wg/852393f6-1fa2-4b13-b891-a7d7bdc46bf6/postgresql-2024-06-06_142752.log?authorization=bce-auth-v1%2F685f75238392421bffc98aa73%2F2024-06-06T09%3A43%3A14Z%2F172800%2Fhost%2F409cfb0222417e3b4a79e556a65e2af29f2a6243807ef82257124e48446c718d",
  "downloadExpires": "2024-06-08T09:43:14Z"
}
```

# 获取binlog信息

**接口说明**

* 获取binlog的日志详细信息，获取本次binlogID的数据事务版本。

**请求结构**

Plain Text

```
GET /v{version}/instance/{instanceId}/binlogs/{logId}/{downloadValidTimeInSec} HTTP 1.1
HOST: rds.bj.baidubce.com
Authorization: authorization string
```

**请求头域**

除公共头域外，无其它特殊头域。

**请求参数**

| 参数名称 | 参数类型 | 是否必须 | 参数位置 | 描述 | 示例值 |
| --- | --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | API版本号 | 1 |
| instanceId | String | 是 | URL参数 | 实例ID | rds-ZuKoVGUf |
| logId | String | 是 | URL参数 | binlogId | 1689091568329757972 |
| downloadValidTimeInSec | String | 是 | URL参数 | 下载有效时间（S） | 1800 |

**返回头域**

除公共头域外，无其它特殊头域。

**返回参数**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| binlog | Binlog | binlog 结果 |

**Binlog字段数据结构说明**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| downloadUrl | String | 下载链接 |
| downloadExpires | String | 过期时间 |

**请求示例**

Plain Text

```
GET /v1/instance/rds-ZuKoVGUf/binlogs/1689091568329757972/1800
HOST: rds.bj.baidubce.com HTTP 1.1
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2023-09-21T05:11:31Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
{
    "binlog": {
    "downloadUrl": "https://bj-rds-mysql-binlog-0000.bj.bcebos.com/binlog/rdsmbyabusl2955/rdsmbyabusl2955_0000/1695225915328623302/mysql-bin.000002?authorization=bce-auth-v1%2F075920b4dc6e46d9b752a848715035af%2F2023-09-22T02%3A41%3A31Z%2F1800%2Fhost%2Fd2751a8c21ee9eb0dd8445a035c2a20c0a7a3d6aa401d6c5398b0c08d948f34c",
    "downloadExpires": "2023-09-22T03:11:31Z"
 }
}
```

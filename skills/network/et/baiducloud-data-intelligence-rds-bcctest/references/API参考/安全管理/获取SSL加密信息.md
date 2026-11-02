# 获取SSL加密信息

**接口说明**

获取SSL加密信息

**请求结构**

Plain Text

```
GET /v{version}/instance/ssl/{instanceId} HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

**请求头域**

除公共头域外，无其他特殊头域。

**请求参数**

| 参数名称 | 参数类型 | 是否必须 | 参数位置 | 示例值 | 描述 |
| --- | --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | 1 | API 版本号 |
| instanceId | String | 是 | URL参数 | rdsm23pnpsz2hqz | 实例 ID (长实例ID，短实例ID不可用） |

**返回头域**

除公共头域外，无其他特殊头域。

**返回参数**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| sslState | SslState | SslState对象 |

**SslState对象**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| instanceId | String | 实例 ID |
| sslStatus | String | ssl状态, open: 开启，close: 关闭， 默认为close |
| sslAddress | String | 加密ssl地址 如:"www.baidu.com" |
| startTime | String | 开始日期 |
| endTime | String | 结束日期 |

**请求示例**

Plain Text

```
GET   /v1/instance/ssl/rdsm23pnpsz2hqz HTTP/1.1
HOST: rds.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2018-09-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "sslState": {
    "instanceId": "rdsm23pnpsz2hqz",
    "sslStatus": "close",
    "sslAddress": "mysql57.rdsm23pnpsz2hqz.rds.bj.baidubce.com",
    "startTime": "0002-11-30T00:00:00Z",
    "endTime": "0002-11-30T00:00:00Z"
    }
}
```

# 获取实例大版本列表API

## **接口描述**

查询指定实例可升级的大版本列表信息。

mysql引擎不支持跨版本升级，每次只能升级一个大版本，接口返回为空，版本顺序直接参考 [MySQL版本](https://cloud.baidu.com/doc/RDS/s/9jwvz0wd3#mysql%E7%89%88%E6%9C%AC)

SQL Server引擎不支持

## **请求结构**

```
GET /v{version}/rds/instance/{instanceId}/majorVersionList HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | API版本号。此接口值为1 |
| instanceId | String | 是 | URL参数 | 实例ID |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| rdsMajorVersionList | List<MajorVersion> | 实例可升级的大版本列表信息 |

**MajorVersion**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| dbVersion | String | 数据库版本 |
| dbType | String | 数据库类型 |
| minorVersion | String | 数据库小版本 |
| rdsMinorVersion | String | 小版本名称 |
| featureDescription | String | 功能描述 |

## **请求示例**

```
GET http://rds.bj.baidubce.com/v1/rds/instance/rds-RX7mPB1o/majorVersionList
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## **返回示例**

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
{
    "metadata": {
        "bceRequestId": "855abcae-cd9f-4d1f-b526-ab3bca0c3db7",
        "transferEncoding": "chunked",
        "contentLength": -1,
        "contentType": "application/json;charset=UTF-8",
        "date": 1776685708000,
        "server": "BWS"
    },
    "rdsMajorVersionList": [
        {
            "dbVersion": "12",
            "minorVersion": "12.22-20250703",
            "rdsMinorVersion": "rds_pg_12.22_20250703",
            "orderId": "2",
            "instanceVersion": "12.22-20250703",
            "runtimeVersion": "12.22-20250703",
            "dbType": "postgresql"
        },
        {
            "dbVersion": "13",
            "minorVersion": "13.18-20250703",
            "rdsMinorVersion": "rds_pg_13.18_20250703",
            "orderId": "2",
            "instanceVersion": "13.18-20250703",
            "runtimeVersion": "13.18-20250703",
            "dbType": "postgresql"
        }
    ]
}
```

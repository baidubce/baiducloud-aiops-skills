# 查询MySQL实例拥有的账号列表

## 接口说明

查询MySQL实例拥有的账号列表

## 请求结构

```
POST /v{version}/task/schema/accountInfo
Host: dts.baidubce.com    
Authorization: authorization string   
{
    "srcConnection": {
        "instanceType": "instanceType",
        "dbType": "dbType",
        "region": "region",
        "dbPort": dbPort,
        "dbUser": "dbUser",
        "dbPass": "dbPass",
        "dbHost": "dbHost"
    },
    "dstConnection": {
        "instanceType": "instanceType",
        "dbType": "dbType",
        "region": "region",
        "dbPort": dbPort,
        "dbUser": "dbUser",
        "dbPass": "dbPass",
        "dbHost": "dbHost"
    }
}
```

## 请求参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| version | String | 是 | API版本号 | "1" | URL参数 |
| **srcConnection** | **Connection** | 是 | 源端 | srcConnection | Request Body 参数 |
| **dstConnection** | **Connection** | 是 | 目标端 | dstConnection | Request Body 参数 |

### Connection字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **instanceType** | **String** | 否 | 实例类型 | bcerds |
| **region** | **String** | 否 | 地域 | bj |
| **dbType** | **String** | 否 | 数据库类型 | mysql |
| **dbUser** | **String** | 否 | 数据库访问账号 | *dts\_trans* |
| **dbPass** | **String** | 否 | 数据库访问密码 | dbPass |
| **dbPort** | **Integer** | 否 | 数据库访问端口 | 3306 |
| **dbHost** | **String** | 否 | 数据库ip或主机名 | 192.168.1.1 |
| **instanceId** | **String** | 否 | 实例ID | rdsmfgdti3d53f5 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Bool** | 是 | 是否成功 | true |
| **status** | **Int** | 是 | 状态码 | 200 |
| **result** | **Result** | 是 | 返回结果 | result |

### Result字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **validAccountInfo** | **ValidAccount[]** | 是 | 指定实例中允许迁移的账号信息 | validAccountInfo |
| **invalidAccountInfo** | **InvalidAccountInfo[]** | 是 | 指定实例中不允许迁移的账号信息 | invalidAccountInfo |
| **validCount** | **Int** | 是 | 返回的允许迁移的账号数量 | 1 |
| **invalidCount** | **Int** | 是 | 返回的不允许迁移的账号数量 | 1 |

## 请求示例

```
POST /v1/task/schema/accountInfo
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization:  authorization string   

{
    "srcConnection": {
        "instanceType": "public",
        "dbType": "mysql",
        "region": "bj",
        "dbPort": 3308,
        "dbUser": "admin",
        "dbPass": "admin",
        "dbHost": "10.156.64.44"
    },
    "dstConnection": {
        "instanceType": "public",
        "dbType": "mysql",
        "region": "bj",
        "dbPort": 3308,
        "dbUser": "admin",
        "dbPass": "admin",
        "dbHost": "10.156.64.44"
    }
}
```

## 响应示例

```
HTTP/1.1 200 OK

{
    "success": true,
    "status": 200,
    "result": {
        {
            "validAccountInfo" : {
                "user_name1" : ["host1", "host2", ..., "hostN"],
                "user_name2" : ["host1", "host2", ..., "hostN"],
            },
            "invalidAccountInfo" {
                "user_name3" : {~~~~
                    "host1" : "error_message1",
                     "host2" : "error_message2"
                },
                "user_name3" : {
                    "127.0.0.1" : "不支持迁移host为localhost或回环地址的账号"
                }
             },
             "validCount" : 10,
             "invalidCount" : 5
         }
}
```

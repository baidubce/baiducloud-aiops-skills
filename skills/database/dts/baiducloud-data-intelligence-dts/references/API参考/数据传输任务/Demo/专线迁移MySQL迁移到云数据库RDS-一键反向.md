# 专线迁移MySQL迁移到云数据库RDS-一键反向

# 创建任务

## 接口说明

创建任务。

## 请求结构

```
POST /v1/task
Host: dts.baidubce.com    
Authorization: authorization string  
{
   "crossRegionTag": 0,
   "directionType": "single",
   "standard": "large",
   "productType": "postpay",
   "sourceInstanceType": "public",
   "targetInstanceType": "bcerds",
   "type": "migration",
   "rollback": 1,
   "orderInfo": {
      "src": {
         "instanceType": "bcegateway",
         "dbType": "mysql",
         "region": "bd",
         "vpcShortId": "vpc-2a0giawvdben",
         "subnetShortId": "sbn-ka9xp8yuj81n",
         "zone": "cn-bd-c"
      },
      "dst": {
         "instanceType": "bcerds",
         "dbType": "mysql",
         "region": "bd"
      }
   }
}
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **type** | **String** | 是 | 任务类型（数据传输任务：migration），目前仅支持数据传输任务 | migration | Request Body 参数 |
| **productType** | **String** | 是 | 付费类型（后付费：postpay），目前仅支持后付费 | postpay | Request Body 参数 |
| **standard** | **String** | 是 | 实例规格（small；medium；large；xlarge） | large | Request Body 参数 |
| **sourceInstanceType** | **String** | 是 | 源端类型（百度智能云数据库：bcerds；自建数据存储：public） | bcerds | Request Body 参数 |
| **targetInstanceType** | **String** | 是 | 目标端类型（百度智能云数据库：bcerds；自建数据存储：public） | bcerds | Request Body 参数 |
| **crossRegionTag** | **Integer** | 是 | 跨地域标识（当源端、目标端类型均为百度智能云数据库且跨地域时：1；其他情况：0） | 0 | Request Body 参数 |
| **directionType** | **String** | 是 | 同步方向（单向同步：single；双向同步：bidirect），目前仅支持单向同步 | single | Request Body 参数 |
| **orderInfo** | **OrderInfo** | 是 | 购买类型 | orderInfo | Request Body 参数 |
| **rollback** | **String** | 否 | 一键反向，1为创建一键反向任务，其余时候不传该参数 | 1 | Request Body 参数 |

### OrderInfo字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **src** | **Src** | 是 | 源端 | src |
| **dst** | **Src** | 是 | 目标端 | src |

### Src字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **instanceType** | **String** | 是 | 源端接入类型（云数据库RDS：bcerds；云数据库 DocDB for MongoDB：bcedocdb；云数据库 SCS for Redis：bcescs；云数据库专属集群DDC：bceddc；云原生数据库 GaiaDB-S：bcegaiadb；公网：public；专线接入：bceet；云服务器BCC：bcebcc；物理服务器BBC：bcebbc；专属服务器DCC：bcedcc；专线迁移：bcegateway（src或dst只支持一端类型为bcegateway）） | public |
| **dbType** | **String** | 是 | 源端数据类型（mysql；pg；SQL Server：mssql；oracle；MongoDB副本集：mongodb；MongoDB分片集：mongodbCluster；社区集群版：openRedisCluster；企业集群版：redisCluster；标准版：redis；kafka；elasticsearch；palo） | mysql |
| **sliceNum** | **String** | 否 | 分片数量 | 1 |
| **region** | **String** | 否 | 地域 | bj |
| **zone** | **String** | 否 | 接入类型为bcegateway时，需要指定可用区 | cn-bj-a |
| **vpcShortId** | **String** | 否 | 接入类型为bcegateway时，需要指定VPC短ID | vpc-46k27rb9wppz |
| **subnetShortId** | **String** | 否 | 接入类型为bcegateway时，需要指定子网短ID | sbn-qtm3d4eituqc |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsTasks** | **List<DtsTask>** | 是 | 任务ID列表 | dtsmxxyy1234 |

### DtsTask字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | dtsmxxyy1234 |

## 请求示例

```
POST /v1/task
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943 
{
  "crossRegionTag": 0,
  "directionType": "single",
  "standard": "large",
  "productType": "postpay",
  "sourceInstanceType": "public",
  "targetInstanceType": "bcerds",
  "type": "migration",
  "rollback": 1,
  "orderInfo": {
     "src": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bd",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c"
      },
      "dst": {
            "instanceType": "bcerds",
            "dbType": "mysql",
            "region": "bd"
     }
  }
}
```

## 响应示例

```
HTTP/1.1 200 OK

{
    "dtsTasks": [
        {
            "dtsId": "dtsr5g818m9dclz0gvf6"
        }
    ]
}
```

# 配置任务

## 接口说明

配置任务。

## 请求结构

```
POST /v1/task/{taskId}/newRollback/config
Host: dts.baidubce.com    
Authorization: authorization string  
{
    "taskName": "dtsr5g818m9dclz0gvf6",
    "openRollbackConfig": "true",
    "dtsTaskPos": {
        "type": "migration",
        "dataType": [
            "increment",
            "schema",
            "base"
        ],
        "taskName": "正向",
        "srcConnection": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bj",
            "dbHost": "172.16.1.37",
            "dbPort": 3306,
            "dbUser": "db1",
            "dbPass": "db12345#",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "dstConnection": {
            "instanceType": "bcerds",
            "dbType": "mysql",
            "region": "bd",
            "instanceId": "rds-U9MLckFU",
            "sqlType": ""
        },
        "schemaMapping": [
            {
                "src": "lws.t",
                "dst": "test1.t",
                "type": "table"
            }
        ],
        "granularity": "dbtb",
        "incrIgnoreType":""
    },
    "dtsTaskNeg": {
        "type": "migration",
        "dataType": [
            "increment"
        ],
        "taskName": "反向",
        "srcConnection": {
            "instanceType": "bcerds",
            "dbType": "mysql",
            "region": "bd",
            "instanceId": "rds-U9MLckFU",
            "sqlType": ""
        },
        "dstConnection": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bj",
            "dbHost": "172.16.1.37",
            "dbPort": 3306,
            "dbUser": "db1",
            "dbPass": "db12345#",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "schemaMapping": [
            {
                "src": "lws.t",
                "dst": "test1.t",
                "type": "table"
            }
        ],
        "granularity": "dbtb",
        "incrIgnoreType":""
    }
}
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **taskId** | **String** | 是 | 任务ID | "dtsmxxxyyy" | URL参数 |
| **taskName** | **String** | 是 | 任务名称 | taskName | Request Body 参数 |
| **openRollbackConfig** | **String** | 是 | 是否打开反向任务配置 | true | Request Body 参数 |
| **dtsTaskPos** | **String** | 是 | 正向数据流 | dtsTaskPos | Request Body 参数 |
| **dtsTaskNeg** | **String** | 是 | 反向数据流 | dtsTaskNeg | Request Body 参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必选 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | dtsxxxyyyzzz |

## 请求示例

```
POST /v1/task/{taskId}/newRollback/config
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943 

{
    "taskName": "dtsr5g818m9dclz0gvf6",
    "openRollbackConfig": "true",
    "dtsTaskPos": {
        "type": "migration",
        "dataType": [
            "increment",
            "schema",
            "base"
        ],
        "taskName": "正向",
        "srcConnection": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bj",
            "dbHost": "172.16.1.37",
            "dbPort": 3306,
            "dbUser": "db1",
            "dbPass": "db12345#",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "dstConnection": {
            "instanceType": "bcerds",
            "dbType": "mysql",
            "region": "bd",
            "instanceId": "rds-U9MLckFU",
            "sqlType": ""
        },
        "schemaMapping": [
            {
                "src": "lws.t",
                "dst": "test1.t",
                "type": "table"
            }
        ],
        "granularity": "dbtb",
        "incrIgnoreType":""
    },
    "dtsTaskNeg": {
        "type": "migration",
        "dataType": [
            "increment"
        ],
        "taskName": "反向",
        "srcConnection": {
            "instanceType": "bcerds",
            "dbType": "mysql",
            "region": "bd",
            "instanceId": "rds-U9MLckFU",
            "sqlType": ""
        },
        "dstConnection": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bj",
            "dbHost": "172.16.1.37",
            "dbPort": 3306,
            "dbUser": "db1",
            "dbPass": "db12345#",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "schemaMapping": [
            {
                "src": "lws.t",
                "dst": "test1.t",
                "type": "table"
            }
        ],
        "granularity": "dbtb",
        "incrIgnoreType":""
    }
}
```

## 响应示例

```
HTTP/1.1 200 OK

{
  "dtsId" : "dtsxxxyyyzzz"
}
```

# 前置检查

## 接口说明

当配置完任务，开始前置检查。

## 请求结构

```
POST /v1/task/{dtsId}/precheck
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
POST /v1/task/{dtsId}/precheck
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK

{
  "result" : { },
  "success" : true
}
```

# 查询前置检查结果

## 接口说明

任务启动前的前置检查，包括连通性，对象存在性，binlog格式等。

## 请求结构

```
GET /v1/task/{dtsId}/rollback/precheck
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 是 | 前置检查结果集合 |  |

## 请求示例

```
GET /v1/task/{dtsId}/rollback/precheck
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK

{
    "success": true,
    "result": {
        "posCheckResults": [//正向数据流
            {
                "name": "srcConnect",
                "status": "ready",
                "message": "源库无法连接, 请确认配置信息和源库状态是否正常",
                "subscription": "检查数据传输服务是否能连通源数据源"
            }
        ],
        "negCheckResults": [//反向数据流
            {
                "name": "dstConnect",
                "status": "ready",
                "message": "目标库无法连接, 请确认配置信息和目标库状态是否正常",
                "subscription": "检查数据传输服务器是否能连通目的数据库"
            }
        ]
    }
}
```

# 强制跳过前置检查

## 接口说明

强制跳过前置检查。

## 请求结构

```
PUT /v1/task/{dtsId}?skipPrecheck
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 单任务ID | dtsmxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
PUT /v1/task/{dtsId}?skipPrecheck
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK

{
  "result" : { },
  "success" : true
}
```

# 启动任务

## 接口说明

当配置完任务，前置检查通过后，可以启动任务。

## 请求结构

```
POST /v1/task/{dtsId}/start
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
POST /v1/task/{dtsId}/start
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "result" : { },
  "success" : true
}
```

# 暂停任务

## 接口说明

运行中的任务可以暂停。

## 请求结构

```
POST /v1/task/{dtsId}/pause
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
POST /v1/task/{dtsId}/pause
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "result" : { },
  "success" : true
}
```

# 结束任务

## 接口说明

结束任务。

## 请求结构

```
POST /v1/task/{dtsId}/shutdown
Host: dts.baidubce.com 
Authorization: string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
POST /v1/task/{dtsId}/shutdown
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "result" : { },
  "success" : true
}
```

# 释放任务

## 接口说明

释放并删除任务。

## 请求结构

```
DELETE /v1/task/{dtsId}
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsxxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
DELETE /v1/task/{dtsId}
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "result" : { },
  "success" : true
}
```

# 一键反向延迟检查

## 接口说明

一键反向延迟检查。

## 请求结构

```
POST /v1/task/{dtsId}/newRollbackCheck
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | dtsxxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 |  | null |

## 请求示例

```
POST /v1/task/{dtsId}/newRollbackCheck
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
    "success": true,
    "status": 200,
    "result": {
        "data": [
            {
                "dtsId": "dtsm5ktdl7vu9twkx7oq",
                "delay": "2"
            }
        ]
    }
}
```

# 启动一键反向

## 接口说明

启动一键反向，当一键反向的正反向任务处于增量运行中时(subStatus中“I”:"running")，调用此接口。

## 请求结构

```
POST /v1/task/{dtsId}/rollback
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | dtsxxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 |  | null |

## 请求示例

```
POST /v1/task/{dtsId}/rollback
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK

{
  "result" : { },
  "success" : true
}
```

# 查询任务信息

## 接口说明

查看指定ID的数据传输任务信息。

## 请求结构

```
GET /v1/task/{dtsId}
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | "dtsmxxxyyy" | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 任务ID | dtsmxxyy1234 |
| **taskName** | **String** | 是 | 任务名称 | dtsmxxyy1234 |
| **status** | **String** | 是 | 任务状态： unConfig：未配置，当用户创建完任务后，就进入未配置状态, 该状态只有dtsId信息 ready：未启动，当配置完后任务后就进入未启动状态，这时就包含任务的所有信息 checking：前置检查中，当用户点击启动后，先会进行前置检查； checkPass：前置检查通过，只有前置检查通过后，才可以进行启动任务 checkFailed：前置检查失败，任务启动时，会进行前置检查，若检查失败，就进入该状态，这时可以进行修改任务或直接结束任务 running：运行中，前置检测通过后，就进入该状态，包括数据迁移中或数据同步中 stopping：暂停中，处于该状态的任务不能进行任何操作 stopped：已暂停，从该状态启动，会进行断点续传，比如：暂停后修改数据同步对象 stopCheckFailed：已暂停(新增同步对象前置检查失败)，当新增同步对象时，会进行前置检查，如果检查失败，回到已暂停状态，但是可以查看检查失败原因 runFailed：运行失败，当运行过程中出现异常就进入该状态，如果是可恢复错误，修复后可继续启动，如果是不可恢复错误，只能结束任务 finished：任务结束，包括手工进行结束，或任务完成后自动结束，或出现不可恢复的错误 | finished |
| **dataType** | **DataType** | 是 |  |  |
| **region** | **String** | 是 | 地域 | bj |
| **createTime** | **String** | 是 | 创建时间 | 2020-12-10T13: 24: 10Z |
| **srcConnection** | **Connection** | 是 | 源端 | srcConnection |
| **dstConnection** | **Connection** | 是 | 目标端 | dstConnection |
| **schemaMapping** | **SchemaMapping** | 是 | schemaMapping | schemaMapping |
| **runningTime** | **Integer** | 是 | 任务已运行时长 | 20 |
| **subStatus** | **List<SubStatus>** | 是 | 子任务状态 |  |
| **dynamicInfo** | **DynamicInfo** | 是 | dynamicInfo | dynamicInfo |
| **errmsg** | **String** | 是 | 执行失败时返回的错误信息，执行成功时为空字符串 |  |
| **sdkRealtimeProgress** | **String** | 是 | （只限数据订阅）任务实时进度，UTC格式 | sdkRealtimeProgress |
| **granularity** | **String** | 是 | 传输任务的粒度，目前只区分实例级和库表级两种 | dbtb |
| **subDataScope** | **SubDataScope** | 是 | （只限数据订阅）订阅通道数据范围 | subDataScope |
| **payInfo** | **PayInfo** | 是 | 付费信息 | payInfo |
| **lockStatus** | **String** | 是 | 任务是否被锁定，取值有：unlock，lockExpiration | unlock |
| **initPosition** | **InitPosition** | 是 | 自定义同步点 | initPosition |
| **accountMapping** | **AccountMapping[]** | 是 | 账号迁移 | accountMapping |
| **incrIgnoreType** | **String** | 是 | 特殊DDL过滤 | drop,truncate |
| **statistic** | **Statistic** | 是 | DTS任务性能统计数据。包含：readSpeed（读取速率，行/s）、writeSpeed（写入速率，行/s） | writeSpeed |
| **checksumResult** | **ChecksumResult** | 是 | 校验结果，可能值：CONSISTENT（一致），INCONSISTENT（不一致），NONE（未知，校验任务运行未结束） | CONSISTENT |
| **dtsIdPos** | **String** | 是 | 双向同步任务时，正向任务ID | dtsmxxyy1234 |
| **dtsIdNeg** | **String** | 是 | 双向同步任务时，反向任务ID | dtsmxxyy1234 |
| **dtsTaskPos** | **DtsTaskPos** | 是 | 双向同步任务时，正向任务信息 | dtsTaskPos |
| **dtsTaskNeg** | **DtsTaskNeg** | 是 | 双向同步任务时，反向任务信息 | dtsTaskNeg |
| **dtsTasks** | **DtsTasks[]** | 是 | 任务组任务时，子任务信息 | dtsTasks |

## 请求示例

```
GET /v1/task/{dtsId}
Host: dts.baidubce.com 
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
    "taskName": "dtsr5g818m9dclz0gvf6",
    "status": "running",
    "region": "bd->bd",
    "dtsIdPos": "dtsmub011wnqq29iwnso",
    "dtsIdNeg": "dtsmh1890duax9ri923u",
    "dtsTaskPos": {
        "dtsId": "dtsmub011wnqq29iwnso",
        "taskName": "正向",
        "status": "running",
        "dataType": [
          "schema",
          "base",
          "increment"
        ],
        "region": "bd->bd",
        "createTime": "2022-12-01T07:45:14Z",
        "srcConnection": {
            "instanceType": "bcegateway",
            "dbType": "mysql",
            "region": "bj",
            "dbHost": "172.16.1.37",
            "dbPort": 3306,
            "dbUser": "db1",
            "dbPass": "",
            "vpcShortId": "vpc-2a0giawvdben",
            "subnetShortId": "sbn-ka9xp8yuj81n",
            "zone": "cn-bd-c",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "dstConnection": {
           "instanceType": "bcerds",
           "dbType": "mysql",
           "region": "bd",
           "instanceId": "rds-U9MLckFU",
           "sqlType": ""
        },
        "schemaMapping": [
            {
               "type": "table",
               "src": "lws.t",
               "dst": "lws.t"
            }
        ],
        "granularity": "dbtb",
        "initPosition": {
           "type": "gtidset",
           "position": "54638621-1505-11eb-bfa0-6c92bf3bcc61:1-29122194"
        },
        "subStatus": [
            {
               "s": "closed",
               "b": "closed",
               "i": "running"
            }
        ],
        "dynamicInfo": {
            "schema": [
                {
                   "current": "1",
                   "count": "1",
                   "speed": "0.100000",
                   "expectFinishTime": "0"
                }
            ],
            "base": [
                {
                    "current": "2",
                    "count": "2",
                    "speed": "0.200000",
                    "expectFinishTime": "0"
                }
            ],
            "increment": {
                "delay": 0, // 延迟为0时表示增量同步追平
                "position": "54638621-1505-11eb-bfa0-6c92bf3bcc61:1-29122194"// 增量同步位点与源端一致时表示增量同步追平
            }
        },
        "statistic": {
           "readSpeed": "",
           "writeSpeed": ""
        },
        "errmsg": "",
        "subDataScope": {
           "startTime": "",
           "endTime": ""
        }
    },
    "dtsTaskNeg": {
        "dtsId": "dtsmh1890duax9ri923u",
        "taskName": "dtsmh1890duax9ri923u",
        "status": "paused",
        "dataType": [
           "increment"
        ],
        "region": "bd->bd",
        "createTime": "2022-12-01T07:45:14Z",
        "srcConnection": {
            "dbServer": "",
            "instanceType": "bcerds",
            "region": "bd",
            "dbType": "mysql",
            "dbUser": "_dts_trans_",
            "dbPass": "",
            "dbPort": 3306,
            "dbHost": "100.80.205.40",
            "instanceId": "rdsmizrhd984cx8",
            "instanceShortId": "rds-U9MLckFU",
            "maxRetryTime": "720",
            "field_whitelist": "",
            "field_blacklist": ""
        },
        "dstConnection": {
            "dbServer": "",
            "instanceType": "public",
            "region": "bd",
            "dbType": "mysql",
            "dbUser": "admin",
            "dbPass": "",
            "dbPort": 3308,
            "dbHost": "10.156.64.44",
            "instanceId": "",
            "sqlType": "",
            "maxRetryTime": "720",
            "supportOnlineDDL": "false"
        },
        "schemaMapping": [
            {
                "type": "table",
                "src": "lws.t",
                "dst": "lws.t",
                "where": "",
                "sqlType": null,
                "fieldBlacklist": null,
                "fieldWhitelist": null,
                "field": null
            }
        ],
        "initPosition": {
            "type": null,
            "position": ""
        },   
        "subStatus": [],
        "statistic": {
            "readSpeed": "",
            "writeSpeed": ""
        },
        "errmsg": "",
        "granularity": "dbtb",
        "subDataScope": {
            "startTime": "",
            "endTime": ""
        }
    },
    "createTime": "2022-12-01T07:45:14Z"
    "payInfo": {
        "productType": "postpay",
        "sourceInstanceType": "OffBce",
        "targetInstanceType": "OnBce",
        "crossRegionTag": 1,
        "createTime": 1669880714000,
        "standard": "Large",
        "endTime": null
    },
    "incrNetType": "large",
    "netType": "large",
    "incrIgnoreType": null
}
```

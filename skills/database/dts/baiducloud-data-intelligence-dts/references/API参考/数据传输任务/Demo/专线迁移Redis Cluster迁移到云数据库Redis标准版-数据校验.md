# 专线迁移Redis Cluster迁移到云数据库Redis标准版-数据校验

## 创建数据校验任务

## 接口说明

创建数据校验任务。

## 请求结构

```
POST /v1/task/checksum
Host: dts.baidubce.com    
Authorization: authorization string  
{
    "type" : "checksum",
    "region" : "bd->bd",
    "assocDtsId" : "dtsmxxxxx",
    "amount" : 1,
    "version" : "new"
}
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **type** | **String** | 是 | 任务类型，这里固定取值为：checksum | checksum | Request Body 参数 |
| **region** | **String** | 是 | 任务所在的地域，字段格式为：源端地域->目标端地域，取值示例：bj->bj，su->gz | bj->bj | Request Body 参数 |
| **assocDtsId** | **String** | 是 | 关联迁移任务dtsId | dtsmxxxxx | Request Body 参数 |
| **amount** | **String** | 是 | 数据校验任务个数 | 1 | Request Body 参数 |
| **version** | **String** | 否 | 数据校验版本，可选值：new、old；非必须，默认值为new | new | Request Body 参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **result** | **Result** | 是 | 返回结果 | result |

### Result字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsCheckTasks** | **DtsCheckTasks[]** | 是 | 数据校验任务ID数组 | dtsCheckTasks |

### DtsCheckTasks字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务dtsCheckId，格式为： （1）dtsc[a-z0-9]{16}，共20位 （2）第4位c表示数据校验checksum （3）例如：dtscabcdefg01234sdns | dtscabcdefg01234sdns |

## 请求示例

```
POST /v1/task/checksum
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943 

{
    "type" : "checksum",
    "region" : "bd->bd",
    "assocDtsId" : "dtsmxxxxx",//关联迁移任务dtsgemk5wlk5sbh0lffh下的子任务，例如：assocDtsId:dtsmxxxxx
    "amount" : 1,
    "version" : "new"
}
```

## 响应示例

```
HTTP/1.1 200 OK

{
  "result": {
    "dtsCheckTasks": [{
       "dtsCheckId": "dtscmawbkgu7f250be1r"
     }]
  }
}
```

## 配置数据校验任务

## 接口说明

配置数据校验任务。

## 请求结构

```
POST /v1/task/checksum/{dtsCheckId}/config
Host: dts.baidubce.com    
Authorization: authorization string  
{
    "srcConnection": {
      "instanceType": "bcegateway",
      "dbType": "redis",
      "region": "bd"
    },
    "dstConnection": {
      "instanceType": "bcescs",
      "dbType": "redis",
      "region": "bd"
    },
    "granularity": "instance",
    "detailConfig": {
      "useAssocDtsTaskConn": "true"
    },
    "schemaMapping": []
}
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtscxxxyyy | URL参数 |
| **srcConnection** | **Connection** | 是 | 源端 | srcConnection | Request Body 参数 |
| **dstConnection** | **Connection** | 是 | 目标端 | dstConnection | Request Body 参数 |
| **granularity** | **String** | 是 | 传输任务的粒度（instance：实例级；dbtb：库表级） |  | instance |
| **schemaMapping** | **Schema[]** | 是 | schemaMapping | schemaMapping | Request Body 参 |
| **detailConfig** | **DetailConfig** | 是 | detailConfig | detailConfig | Request Body 参数 |

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
POST /v1/task/checksum/{dtsCheckId}/config
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943 

{
    "srcConnection": {
        "instanceType": "bcegateway",
        "dbType": "redis",
        "region": "bd"
    },
    "dstConnection": {
        "instanceType": "bcescs",
        "dbType": "redis",
        "region": "bd"
    },
    "granularity": "instance",
    "detailConfig": {
        "useAssocDtsTaskConn": "true"
    },
    "schemaMapping": []
}
```

## 响应示例

```
HTTP/1.1 200 OK

{
    "success": true,
    "result": null
}
```

## 数据校验前置检查

## 接口说明

当数据校验任务配置完任务，开始前置检查。

## 请求结构

```
POST /v1/task/checksum/{dtsCheckId}/precheck 
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtscxxxyyy | URL参数 |

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
POST /v1/task/checksum/{dtsCheckId}/precheck
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

## 启动数据校验任务

## 接口说明

当配置完任务，前置检查通过后，可以启动任务。

## 请求结构

```
POST /v1/task/checksum/{dtsCheckId}/start
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtscxxxyyy | URL参数 |

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
POST /v1/task/checksum/{dtsCheckId}/start
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

## 停止数据校验

## 接口说明

停止数据校验。

## 请求结构

```
POST /v1/checksum/task/{dtsCheckId}/shutdown
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtsmxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 否 | 暂未使用 | null |

## 请求示例

```
POST /v1/checksum/task/{dtsCheckId}/shutdown
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

## 查看数据校验比对结果

## 接口说明

查看数据校验比对结果。

## 请求结构

```
POST /v1/task/checksum/{dtsCheckId}/result
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtscxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 是 |  | null |

## 请求示例

```
POST /v1/task/checksum/{dtsCheckId}/result
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
        "checksumResult" : {
            
            "status" : "finished",//unconfig（未配置）；ready（未启动）；checking（前置检查中）；checkPass（前置检查通过）；checkFailed（前置检查失败）；running（校验中）；finished(校验成功)；runFailed(运行异常)；stopping（暂停中）；stopped（已暂停）
            "checksumResult" : "INCONSISTENT", // INCONSISTENT（不一致）；CONSISTENT（一致）
            "totalKeyCount" : "100",   // 源端的key总数
            "checkedKeyCount" : "99",  // 已校验的key总数
            "uncheckedKeyCount" : "1", // 不支持校验的key总数
            "uncheckedKeyList" : [     // 不支持校验的key列表
                {
                    "dbName" : "0",
                    "keyName" : "stream1",
                    "message" : "do not support checking stream"
                },
                {
                    "dbName" : "1",
                    "keyName" : "stream2",
                    "message" : "do not support checking stream"
                }
            ],
            "inconsistentCount" : "2", //不一致的数据行数
            "inconsistentList" : [
                {
                    "dbName" : "0",                      // key所在DB名
                    "inconsistentType" : "INCONSISTENT", // 不一致类型
                    "srcData" : "key_string1",           // 源端key名
                    "dstData" : "key_string1"            // 目标端key名
                },
                {
                    "dbName" : "1",
                    "inconsistentType" : "MISSING",
                    "srcData" : "key_hash2",
                    "dstData" : ""
                },
                {
                    "dbName" : "2",
                    "inconsistentType" : "REDUNDANCY",
                    "srcData" : "",
                    "dstData" : "key_list3"
                }
            ]
        }
    }
}
```

## 查看数据校验任务详情

## 接口说明

查看数据校验任务详情。

## 请求结构

```
GET /v1/task/checksum/{dtsCheckId}/detail
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求体参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsCheckId** | **String** | 是 | 数据校验任务ID | dtscxxxyyy | URL参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Object** | 是 |  | null |

## 请求示例

```
GET /v{version}/task/checksum/{dtsCheckId}/detail
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
        "dtsCheckTask": {
            "status": "finished",
            "createTime": "2022-11-24T08:59:10Z",
            "srcConnection": {
                "instanceType": "bcegateway",
                "dbType": "redis",
                "region": "bd",
                "dbHost": "100.80.143.80",
                "dbPort": 28,
                "dbUser": "",
                "dbPass": "",
                "instanceId": "",
                "subnetShortId": "sbn-ka9xp8yuj81n",
                "vpcId": "1cd2dd00-b2c8-4053-9550-594a2991cc6e",
                "vpcShortId": "vpc-2a0giawvdben",
                "zone": "cn-bd-c"
            },
            "dstConnection": {
                "instanceType": "public",
                "region": "bj",
                "dbType": "redis",
                "dbPort": 7020,
                "dbHost": "10.156.64.44",
                "dbUser": "",
                "dbPass": "",
                "instanceId": ""
            },
            "schemaMapping": [],
            "granularity": "instance",
            "detailConfig": {
                "useAssocDtsTaskConn": "true"
            },
            "assocDtsId": "dtsmmcgm8tfn91kjdx6l"
        }
    }
}
```

## 查看数据校验任务列表

## 接口说明

查看数据校验任务列表。

## 请求结构

```
POST /v1/task/checksum/{dtsId}/list
Host: dts.baidubce.com    
Authorization: authorization string

{
  "maxKeys" : 15,
  "marker" : "dtsmxxxyyyzzz",
}
```

## 请求参数

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| **dtsId** | **String** | 是 | 关联迁移任务ID | dtsmxxxyyy | URL参数 |
| **marker** | **String** | 否 | 分页参数，初次请求无需设置，后续请求使用上次响应中的nextMarker | dtsmxxxyyyzzz | Request Body 参数 |
| **maxKeys** | **Integer** | 否 | 分页参数，每页数据条数，默认为 10 | 15 | Request Body 参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必须 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **task** | **List<Object>** | 是 | 任务数组 | task |
| **nextMarker** | **String** | 是 | 分页参数，下一页标记 | dtsmxxxyyy |
| **maxKeys** | **Integer** | 是 | 分页参数，数据条数最大值 | 10 |
| **truncated** | **Boolean** | 是 | 是否截断 | false |

## 请求示例

```
POST /v1/task/list
Host: dts.baidubce.com    
Content-Type: application/json     
Authorization: bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943 
{
  "maxKeys" : 15,
  "marker" : "dtsmxxxyyyzzz"
}
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "nextMarker": null,
  "marker": null,
  "maxKeys": 10,
  "isTruncated": false,
  "task": [
    {
        "dtsCheckId": "dtsch51dbxyio8rnf86c",
        "status": "finished",
        "region": "bd->bd",
        "checksumResult": "CONSISTENT",//校验结果，可能值：CONSISTENT（一致），INCONSISTENT（不一致），NONE（未知，校验任务运行未结束）   
        "assocDtsId": "dtsmky23r0buci12l4zh",
        "createTime": "2022-11-25T05:41:04Z",
        "finishTime": "2022-11-25T05:41:31Z"
    }
 ]
}
```

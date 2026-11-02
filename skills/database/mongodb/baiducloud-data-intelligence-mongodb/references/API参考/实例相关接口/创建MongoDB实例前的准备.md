# 创建MongoDB实例前的准备

在创建云数据库 DocDB for MongoDB 实例前，您可以根据业务需求确定实例的地域、可用区、架构、规格和存储空间等配置。

## 查询地域

请求示例：

```
GET /v1/instance/flavor/availableRegionList
```

响应示例：

```
[
    "bj",
    "gz",
    "su",
    "bd",
    "fwh",
    "cd"
]
```

## 查询AZ

Body Parameters（AvailableZoneListRequest）:

| 字段名 | 含义 | 类型 | 取值范围 | 是否必填 |
| --- | --- | --- | --- | --- |
| serviceType | 服务类型 | String | replica / sharding | 是 |

请求示例：

```
POST /v1/instance/flavor/availableZoneList

{
    "serviceType": "replica"
}
```

Response(Normal): 返回 AvailableZoneList。

| 字段名 | 含义 | 类型 |
| --- | --- | --- |
| .zones | 可用区列表 | List |
| .zones[].zoneName | 逻辑可用区名 | String |
| .zones[].apiZoneName | API 可用区名 | String |

响应示例：

```
{
    "zones": [
        {
            "zoneName": "zoneC",
            "apiZoneName": "cn-gz-c"
        },
        {
            "zoneName": "zoneD",
            "apiZoneName": "cn-gz-d"
        }
    ]
}
```

## 查询可购买规格

Body Parameters（FlavorListRequest）:

| 字段名 | 含义 | 类型 | 取值范围 | 是否必填 | 注意事项 |
| --- | --- | --- | --- | --- | --- |
| type | 规格类型 | String | replica / mongos / shard | 是 | replica=副本集； mongos/shard=分片集对应节点 |
| zone | 可用区 | String | 否 | 否 | 命中则用该可用区，否则用第一个可用区； 变配场景会被实例所在可用区覆盖 |
| dbInstanceId | 实例 ID | String | 否 | 变配场景必填 |  |
| nodeId | 节点 ID | String | 条件必填 | 分片集变配场景必填 |  |

请求示例（分片集shard变配规格）：

```
POST /v1/instance/flavor/availableFlavorList

{
    "type": "shard",
    "dbInstanceId": "m-rcAqgx",
    "nodeId": "shd-nzDV7q"
}
```

响应示例：

```
[
    {
        "label": "1核2G",
        "value": "1,2",
        "min": 2,
        "max": 32,
        "marks": {
            "5": 5,
            "252": 252,
            "500": 500
        },
        "diskMin": 5,
        "diskMax": 500,
        "diskStep": 1,
        "maxConns": 2000
    }
]
```

## 相关API

* [创建副本集实例](https://cloud.baidu.com/doc/MONGODB/s/Ekdgskkrk)
* [创建分片集实例](https://cloud.baidu.com/doc/MONGODB/s/ikdgsphbp)

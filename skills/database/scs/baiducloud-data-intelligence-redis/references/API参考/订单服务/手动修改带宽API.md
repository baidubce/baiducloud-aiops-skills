# 手动修改带宽API

### 请求说明

* 本接口用于变更一个redis实例的带宽值。

### 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/modifyBandwidth HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{
    "shardBandwidthInfo": [
        {
            "shardName": "xxxxxxx",
            "nodeBandwidthInMB": "200"           
        },
        {
            "shardName": "xxxxxxx",
            "nodeBandwidthInMB": "200"
        }
    ]
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | 实例ID |
| shardBandwidthInfo | List<ShardBandwidth> | 是 | RequestBody参数 | 分片带宽列表。 |

#### ShardBandwidth

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| shardName | String | 分片hashName |
| nodeBandwidthInMB | Integer | 当前分片带宽大小，不能小于默认带宽。增量带宽额外收费。单位：MB。 |

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| orderId | String | 订单ID |

### 请求示例

Plain Text

```
POST /v1/instance/{instanceId}/modifyBandwidth HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{
    "shardBandwidthInfo": [
        {
            "shardName": "xxxxxxx",
            "nodeBandwidthInMB": "200"           
        },
        {
            "shardName": "xxxxxxx",
            "nodeBandwidthInMB": "200"
        }
    ]
}
```

### 返回示例

Plain Text

```
  HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "orderId": "xxx"
}
```

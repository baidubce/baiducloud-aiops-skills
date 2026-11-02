# 标准版升级集群版API

## 请求说明

通过调用API接口来将标准版实例升级为集群版。

* 不支持跨版本架构升级，例如，Redis 4.0 标准架构不支持升级至 Redis 5.0 集群架构。
* 不支持带了只读实例组的标准版实例升级到集群版，如需要升级需要先删除只读实例组才能升级。
* 热活或多活实例组中的实例不支持升级。
* 不支持单副本标准版升级架构。
* 升级后的总内存容量需要大于等于标准版总内存容量。
* 有维护时间内的任务未完成时不支持升级。
* 非运行中实例不支持升级。
* Redis7.0标准版不支持升级。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/clusterTypeChange HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| isDefer | Boolean | Body | 否 | 是否维护时间内执行。默认false。true：维护时间内执行；false：立即执行。 |
| nodeType | String | Body | 否 | 节点规格。- 可以是新的规格，需要是Redis集群版的规格。 - 可以为空，默认为原实例规格，但是需要确保原实例规格为集群版的规格，否则执行失败。 |
| shardNum | Integer | Body | 否 | 分片数量。- 可以设置新的分片数量； - 可以为空，默认为原实例分片数。 |
| replicationInfo | List<ReplicationItem> | Body | 否 | 副本信息。- 不支持减少副本，可以新增。 - 可以设置新的副本信息，需全量的副本信息。 - 可以为空，默认为原实例副本数。 |

## ReplicationItem

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| availabilityZone | String | 可通过调用获取可用区列表接口查询可用区列表。zoneName命名规范是“国家-region-可用区序列"，小写，例如北京可用区A为"cn-bj-a" |
| subnetId | String | 子网Id |
| isMaster | Integer | 是否是主节点 1代表主 0代表从。主节点有且仅有一个。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| orderId | String | 订单ID。 |

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-ozgdsbsqqnxi/clusterTypeChange HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{
    "nodeType": "cache.n1.small",
    "shardNum": 2,
    "replicationInfo": [
        {
            "availabilityZone": "cn-bj-a",
            "subnetId": "sbn-t94a1xpb4tw4",
            "isMaster": 1
        },
        {
            "availabilityZone": "cn-bj-a",
            "subnetId": "sbn-t94a1xpb4tw4",
            "isMaster": 0
        }
    ],
    "isDefer": false
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "orderId": "xxx"
}
```

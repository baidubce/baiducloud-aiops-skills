# 迁移可用区API

## 请求说明

**云数据库Redis**支持通过调用API将实例迁移到同地域内的其它可用区、子网。

* 迁移可用区功能不支持**热活实例组、多活实例组**、不支持只读节点。
* Redis**社区版、集群版、容量版**均支持可用区迁移功能。
* 主从节点同一个可用区下的子网需要保持一致。
* **Redis社区版只读节点**不支持迁移，但Redis社区版实例其它主从节点迁移时子网的选择会受到限制，即如果迁移到只读节点所在可用区时，子网信息默认需要与只读节点一致。
* 变更选取的可用区、子网不可与之前完全一致，即选取节点完全没变化时不支持变更。
* **开通公网**的实例不支持可用区迁移。
* 实例有待执行的**维护窗口**任务，不支持可用区迁移。

## 请求结构

Plain Text

```
POST /v1/instance/{instanceId}/azoneMigration
Host: redis.bj.baidubce.com
Authorization: authorization string
{
    "isDefer":"true",
    "replicationInfo": [
        {
           "availabilityZone": "cn-bj-a",
           "subnetId": "sbn-x94w3r601111",
           "isMaster": 1
        }
    ]
}
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID。 |
| isDefer | Boolean | Body | 是 | 是否维护时间内执行。- true：维护时间内执行 - false：立即执行 |
| replicationInfo | List<ReplicationItem> | Body | 是 | 副本信息。需全量的副本信息，可以修改可用区和子网。 |

## ReplicationItem

| 参数名称 | 参数类型 | 是否必须 | 描述 |
| --- | --- | --- | --- |
| availabilityZone | String | 是 | 可用区。示例：cn-bj-a |
| subnetId | String | 是 | 子网ID。示例：sbn-x94w3r601111 |
| isMaster | Integer | 是 | 是否是主节点。主节点有且仅有一个。- 1：主节点 - 0：从节点 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无。

## 请求示例

Plain Text

```
POST /v1/instance/{instanceId}/azoneMigration
Host: redis.bj.baidubce.com
Authorization: authorization string
{
    "isDefer":"true",
    "replicationInfo": [
        {
           "availabilityZone": "cn-bj-a",
           "subnetId": "sbn-x94w3r601111",
           "isMaster": 1
        }
    ]
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

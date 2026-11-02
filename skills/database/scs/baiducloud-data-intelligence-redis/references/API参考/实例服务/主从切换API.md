# 主从切换API

## 请求说明

主从切换，变更分片的主从节点关系，保障实例的高可用性。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/switchMasterSlave HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{
    "shards": [
        {
           "hashName": "",
           "nodeShowId": ""
        }
    ]
}
```

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| shards | List<SwitchMasterSlaveShard> | Body | 是 | 切换的分片列表。 |

### SwitchMasterSlaveShard参数信息

| 参数名称 | 参数类型 | 是否必须 | 描述 |
| --- | --- | --- | --- |
| hashName | String | 是 | 指定要切换的分片。可从实例详情接口RedisList字段中获取分片信息。 |
| nodeShowId | String | 是 | 指定该分片中要切换为主的节点ID。可从实例详情接口RedisList字段中获取分片中节点ID的信息。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无特殊返回参数。

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-elahimuhxjia/switchMasterSlave  HTTP/1.1
Host: redis.{region}.baidubce.com 
Authorization: authorization string
{
    "shards": [
        {
           "hashName": "scs-bj-elahimuhxjia-0",
           "nodeShowId": "scs-bj-elahimuhxjia_redis_67957_1"
        }
    ]
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
```

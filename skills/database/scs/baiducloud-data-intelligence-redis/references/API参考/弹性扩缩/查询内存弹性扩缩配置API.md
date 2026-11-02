# 查询内存弹性扩缩配置API

### 请求说明

* 查看实例的内存弹性扩缩配置信息。
* 目前仅标准版实例支持。

### 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/autoScalingConfig
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必须 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | 实例ID |

### 返回头域

除公共头域，无其它特殊头域。

### 返回参数

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| memUsageUpperThreshold | integer | 触发规格自动扩容的内存平均利用率阈值，单位为%，取值：70、80、90 |
| memUsageDownThreshold | integer | 触发规格自动缩容的内存平均利用率阈值，单位为% ，取值：20、30、40 |
| maxNodeType | String | 扩容规格上限 |
| minNodeType | String | 缩容规格下限 |
| observationWindowSizeForUpper | String | 观测窗口。参数值由数值和时间单位后缀组成，支持的数据库实例及其取值如下（其中时间后缀m表示分钟，h表示小时）：1m，3m、5m、10m、15m、30m。 |
| observationWindowSizeForDown | String | 观测窗口。参数值由数值和时间单位后缀组成，支持的数据库实例及其取值如下，（其中时间后缀m表示分钟，h表示小时）：5m、10m、15m、30m。 |

### 请求示例

Plain Text

```
 GET /v1/instance/{instanceId}/autoScalingConfig
 HOST: redis.bj.baidubce.com
 Content-Type: application/json   
 Authorization: bce-auth-v1/0255cb4f78f140728045b551d6a317ec/2018-11-13T05:57:04Z/1800/host/633fd6aadc177fce91e5e930c63886b5fb4da8938d9a02c9d13df4fdb8efdec5
```

### 返回示例

Plain Text

```
 HTTP/1.1 200 OK
    x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
    Content-Type: application/json
  {
  "memSpec": {
    "memUsageUpperThreshold": xxxx,
    "memUsageDownThreshold":xxxx,
    "maxNodeType": "xxxx",
    "minNodeType": "xxxx",
    "observationWindowSizeForUpper": "xxxx",
    "observationWindowSizeForDown": "xxxx",
   
  }
}
```

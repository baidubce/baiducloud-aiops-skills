# 维度值TopN和监控数据查询接口

## 接口描述

该接口可获取某个云产品实例下某个指标名的某些维度下的维度值TopN以及对应的监控数据。

## 请求结构

* method：POST
* 请求URL：/csm/api/v2/dimensions/top

## 请求参数

| 名称 | 类型 | 描述 | 是否必须 | 参数位置 |
| --- | --- | --- | --- | --- |
| userId | String | 用户ID | 是 | Body参数 |
| scope | String | 云产品标识，取值请参考[云产品标识列表](/doc/BCM/s/Ulucfgod5) | 是 | Body参数 |
| region | String | 区域标识，取值请参考[区域列表](/doc/BCM/s/5jwvym49g) | 是 | Body参数 |
| metricName | String | 监控指标名，仅限于使用如下字符集合："0~9、A~Z、a~z"、 "\_" | 是 | Body参数 |
| statistics | String | 统计方法类型，可选值：average、maximum、minimum、sum、sampleCount | 是 | Body参数 |
| dimensions | Map<String, String> | 实例维度和指标维度，实例维度：实例Id或父实例Id（必填）；指标维度：监控指标携带的维度（选填） | 是 | Body参数 |
| labels | Set<String> | 需要排序的指标维度 | 是 | Body参数 |
| startTime | String | 监控数据开始时间，请参考[日期与时间](/doc/BCM/s/4jwvym2tt)，UTC日期表示 | 是 | Body参数 |
| endTime | String | 监控数据结束时间，请参考[日期与时间](/doc/BCM/s/4jwvym2tt)，UTC日期表示 | 是 | Body参数 |
| order | String | 排序方式，可选值top（从大到小）、bottom（从小到大），默认top | 否 | Body参数 |
| topNum | int | 排序后保留的前topNum数量，默认值：10，最大为1000 | 否 | Body参数 |
| cycle | int | 统计周期，单位：秒，默认值：60 | 否 | Body参数 |

### 参数解释

* 名字空间scope、监控项metric、统计方法Statistic、维度Dimension等的概念请参考[核心概念](/doc/BCM/s/ujwvylt2m)。

## 响应参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| requestId | String | 请求标识ID |
| userId | String | 用户ID |
| serviceName | String | 云产品标识 |
| metricName | String | 指标名 |
| resourceId | String | 实例ID |
| dimensions | List<Dimension> | 指标维度 |
| dataPoints | List<TsdbQueryDataPoint> | 监控指标数据 |

### Dimension

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| name | String | 维度名 |
| value | String | 维度值 |

### TsdbQueryDataPoint

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| timestamp | String | 监控数据对应的时间 |
| average | Double | 统计周期内监控项的平均值 |
| sum | Double | 统计周期内监控项的和值 |
| maximum | Double | 统计周期内监控项的最大值 |
| minimum | Double | 统计周期内监控项的最小值 |
| sampleCount | Integer | 统计周期内监控项数据点数 |

## 请求示例

```
{
      "userId": "453bf9********************9090dc",
      "scope": "BCE_NAT",
      "region": "bj",
      "metricName": "ConnNumber",
      "statistics": "average",
      "startTime": "2024-07-08T11:30:53Z",
      "endTime": "2024-07-08T11:32:53Z",
      "dimensions": {
            "NatId": "nat-be********cw"
      },
      "labels": [
            "FixIp"
      ],
      "topNum": 2,
      "order": "top",
      "cycle": 60
}
```

## 响应示例

```
[
    {
        "requestId": "3adb033a103945c0921914c4c23d6ab8",
        "userId": "453bf9********************9090dc",
        "serviceName": "BCE_NAT",
        "metricName": "ConnNumber",
        "resourceId": "nat-be********cw",
        "dimensions": [
            {
                "name": "FixIp",
                "value": "100.2.107.13"
            }
        ],
        "dataPoints": [
            {
                "timestamp": "2024-07-08T11:30:53Z",
                "average": 335.0
            },
            {
                "timestamp": "2024-07-08T11:31:53Z",
                "average": 367.0
            },
            {
                "timestamp": "2024-07-08T11:32:53Z",
                "average": 456.0
            }
        ]
    },
    {
        "requestId": "3adb033a103945c0921914c4c23d6ab8",
        "userId": "453bf9********************9090dc",
        "serviceName": "BCE_NAT",
        "metricName": "ConnNumber",
        "resourceId": "nat-be********cw",
        "dimensions": [
            {
                "name": "FixIp",
                "value": "100.2.107.14"
            }
        ],
        "dataPoints": [
            {
                "timestamp": "2024-07-08T11:30:53Z",
                "average": 153.0
            },
            {
                "timestamp": "2024-07-08T11:31:53Z",
                "average": 148.0
            },
            {
                "timestamp": "2024-07-08T11:32:53Z",
                "average": 142.0
            }
        ]
    }
]
```

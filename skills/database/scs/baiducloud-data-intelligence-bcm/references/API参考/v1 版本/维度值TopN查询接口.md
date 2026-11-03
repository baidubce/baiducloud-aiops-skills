# 维度值TopN查询接口

## 接口描述

该接口可获取某个云产品实例下某个指标名的某些维度下的维度值TopN。

## 请求结构

* method：POST
* 请求URL：/csm/api/v2/dimensions/top

## 请求参数

| 名称 | 类型 | 描述 | 是否必须 | 参数位置 |
| --- | --- | --- | --- | --- |
| userId | String | 用户ID | 是 | Body参数 |
| scope | String | 云产品标识，取值请参考[云产品标识列表](/doc/BCM/s/Ulucfgod5) | 是 | Body参数 |
| region | String | 区域标识，取值请参考[区域列表](/doc/BCM/s/5jwvym49g) | 是 | Body参数 |
| metricName | String | 监控指标 | 是 | Body参数 |
| statistics | String | 统计方法类型，可选值：average、maximum、minimum、sum、sampleCount | 是 | Body参数 |
| dimensions | Map<String, String> | 实例维度和指标维度，实例维度：实例Id或父实例Id（必填）；指标维度：监控指标携带的维度（选填） | 是 | Body参数 |
| labels | Set<String> | 需要排序的指标维度 | 是 | Body参数 |
| startTime | String | 监控数据开始时间，请参考[日期与时间](/doc/BCM/s/4jwvym2tt)，UTC日期表示 | 是 | Body参数 |
| endTime | String | 监控数据结束时间，请参考[日期与时间](/doc/BCM/s/4jwvym2tt)，UTC日期表示 | 是 | Body参数 |
| order | String | 排序方式，可选值top（从大到小）、bottom（（从小到大）），默认top | 否 | Body参数 |
| topNum | int | 排序后保留的前topNum数量，默认值：10，最大为1000 | 否 | Body参数 |

### 参数解释

* 名字空间scope、监控项metric、统计方法Statistic、维度Dimension等的概念请参考[核心概念](/doc/BCM/s/ujwvylt2m)。

## 响应参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| requestId | String | 请求标识ID |
| topDatas | List<TopData> | 排序后的维度值列表 |

### TopData

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| order | int | 排名，从1开始 |
| dimensions | List<Dimension> | 维度信息 |

### Dimension

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| name | String | 维度名 |
| value | String | 维度值 |

## 请求示例

```
{
      "userId": "0b8ed5********************8fb898",
      "scope": "BCE_NAT",
      "region": "bj",
      "metricName": "ConnNumber",
      "statistics": "average",
      "startTime": "2024-04-27T07:10:01Z",
      "endTime": "2024-04-27T07:20:01Z",
      "dimensions": {
            "NatId": "nat-b51******70"
      },
      "labels": [
            "FixIp"
      ],
      "topNum": 2,
      "order": "top"
}
```

## 响应示例

```
{
      "requestId": "9083c1ec306b4fceb56190b71ac02a81",
      "topDatas": [
            {
                  "order": 1,
                  "dimensions": [
                        {
                              "name": "FixIp",
                              "value": "172.16.1.4"
                        }
                  ]
            },
            {
                  "order": 2,
                  "dimensions": [
                        {
                              "name": "FixIp",
                              "value": "172.16.1.5"
                        }
                  ]
            }
      ]
}
```

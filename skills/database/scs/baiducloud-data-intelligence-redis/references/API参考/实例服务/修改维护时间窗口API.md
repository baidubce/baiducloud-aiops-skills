# 修改维护时间窗口API

## 请求说明

通过调用API接口来修改维护时间窗口。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/timeWindow HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |
| startTime | String | Body | 是 | 开始时间。示例：04:00（即凌晨4点） |
| duration | Integer | Body | 是 | 持续时间。取值范围：1-8（单位：小时） |
| period | List<Integer> | Body | 是 | 维护周期。1-6分别代表周一到周六。0代表周日。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无特殊返回参数。

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-oqdgnbjfogjw/timeWindow HTTP/1.1
HOST: redis.{region}.baidubce.com
Authorization: authorization string
{
    "startTime": "04:30",
    "duration": 2,
    "period": [1,2,3,4,5,6,0]
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
```

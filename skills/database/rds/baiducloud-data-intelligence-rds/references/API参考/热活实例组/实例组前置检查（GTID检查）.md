# 实例组前置检查（GTID检查）

**接口描述**

本接口用于实例组前置检查（GTID检查）。

本接口为v1接口。

**请求结构**

Plain Text

```
POST /v{version}/instance/group/checkGtid HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
{
  "instanceId":"instanceId"
}
```

**请求头域**

除公共头域外，无其它特殊头域。

**请求参数**

| 参数名称 | 类型 | 是否必须 | 参数位置 | 示例值 | 描述 |
| --- | --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | 1 | API 版本号 |
| instanceId | String | 是 | RequestBody参数 | rds-X5luTeou | 实例 ID |

  

**响应头域**

除公共头域外，无其它特殊头域。

**返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| result | Boolean | 成功：true；失败：false |

  

**请求示例**

Plain Text

```
POST http://rds.bj.baidubce.com/v1/instance/group/checkGtid HTTP/1.1
HOST: rds.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
  "instanceId":"rds-X5luTeou"
}
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
{
  "result": true
}
```

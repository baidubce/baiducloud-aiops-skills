# 目标地域映射列表API

## **接口描述**

获取 RDS 数据备份副本目标地域列表，用于跨可用区/跨地域备份场景下查询当前实例可选的目标地域。

## **请求结构**

Plain Text

```
GET /v1/instance/{instanceId}/backup/target/region HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | 实例ID |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| regions | List | 可选的目标地域列表 |

## **请求示例**

Plain Text

```
GET http://rds.bj.baidubce.com/v1/instance/rds-RX7mPB1o/backup/target/region
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json
```

## **返回示例**

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5

{
  "regions": [
    "bj",
    "gz",
    "su"
  ]
}
```

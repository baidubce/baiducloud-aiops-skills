# 大版本升级前置检查API

## **接口描述**

对指定实例进行大版本升级前置检查，检查实例是否满足大版本升级条件。

当前只支持mysql引擎

## **请求结构**

Plain Text

```
GET /v{version}/rds/instance/{instanceId}/majorVersion/preCheck HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | API版本号。此接口值为1 |
| instanceId | String | 是 | URL参数 | 实例ID |
| checkType | String | 是 | Query参数 | 检查类型 ，枚举值为以下情况。**返回值包含（yes/no）** tdeStatus - 检查实例是否开启TDE sysdb - 检查实例是否存在sys库 gtid - 检查实例是否开启GTID noninnodb - 检查实例是否存在非InnoDB表 fts - 检查实例数据库是否有Fts索引 event - 检查实例数据库是否有event trigger - 检查实例数据库是否有trigger |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| tdeStatus | String | 检查实例是否开启TDE |
| sysdb | String | 检查实例是否存在sys库 |
| gtid | String | 检查实例是否开启GTID |
| noninnodb | String | 检查实例是否存在非InnoDB表 |
| fts | String | 检查实例数据库是否有Fts索引 |
| event | String | 检查实例数据库是否有event |
| trigger | String | 检查实例数据库是否有trigger |

> 注：以上字段可能为空不返回。

## **请求示例**

Plain Text

```
GET http://rds.bj.baidubce.com/v1/rds/instance/rds-RX7mPB1o/majorVersion/preCheck?checkType=1000
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## **返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
{
  "tdeStatus": "yes",
}
```

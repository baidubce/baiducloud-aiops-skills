# 表粒度查询用户列表API

## **接口描述**

查询指定实例下的全部表粒度账号列表。

## **请求结构**

Plain Text

```
GET /v2/instance/{instanceId}/account/tableLevel/list HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | RDS 实例 ID |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| users | List<TableLevelAccountListResponse> | 账号列表，见下表 |

**TableLevelAccountListResponse**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| user | String | 账号名 |
| host | String | 来源主机 |
| status | String | 账号状态 |
| type | String | 账号类型 |
| superUserFlag | String | 是否超级用户 |
| remark | String | 备注 |
| supportBns | Boolean | 是否支持 BNS，默认 `false` |
| wrFlag | String | 读写标识 |

## **请求示例**

Plain Text

```
GET http://rds.bj.baidubce.com/v2/instance/rds-RX7mPB1o/account/tableLevel/list
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
  "users": [
    {
      "user": "user1",
      "host": "%",
      "status": "available",
      "type": "common",
      "superUserFlag": "0",
      "remark": "",
      "supportBns": false,
      "wrFlag": ""
    }
  ]
}
```

## **错误码**

| HTTP status code | 错误码 | 错误信息 | 描述 |
| --- | --- | --- | --- |
| 400 | ParamValidationFailed | Parameter validate error. | 参数验证失败 |
| 403 | PermissionDeny | permission denied | 用户无该接口权限 |
| 403 | InvalidInstanceStatus | instance status is invalid | 实例状态不在可操作白名单内 |
| 404 | ResourceNotExist | Resource do not exist. | 实例不存在 |
| 500 | InternalServerError | Internal service error. | 内部服务错误 |

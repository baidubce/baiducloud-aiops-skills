# 表粒度更新用户描述API

## **接口描述**

更新指定表粒度账号的备注信息。

## **请求结构**

Plain Text

```
PUT /v2/instance/account/tableLevel/update_desc HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json

{
  "instanceId": "rds-RX7mPB1o",
  "user": "user1",
  "host": "%",
  "remark": "data team owner"
}
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

无 URL 参数。

### **请求体参数**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| instanceId | String | 是 | RDS 实例 ID |
| user | String | 是 | 账号名 |
| host | String | 是 | 来源主机 |
| remark | String | 是 | 新备注 |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

无返回内容。

## **请求示例**

Plain Text

```
PUT http://rds.bj.baidubce.com/v2/instance/account/tableLevel/update_desc
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json

{
  "instanceId": "rds-RX7mPB1o",
  "user": "user1",
  "host": "%",
  "remark": "data team owner"
}
```

## **返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

## **错误码**

| HTTP status code | 错误码 | 错误信息 | 描述 |
| --- | --- | --- | --- |
| 400 | ParamValidationFailed | Parameter validate error. | 参数验证失败 |
| 403 | PermissionDeny | permission denied | 用户无该接口权限 |
| 403 | InvalidInstanceStatus | instance status is invalid | 实例状态不在可操作白名单内 |
| 404 | ResourceNotExist | Resource do not exist. | 实例不存在 |
| 500 | InternalServerError | Internal service error. | 内部服务错误 |

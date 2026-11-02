# 表粒度查询用户详情API

## **接口描述**

按 `instanceId + user + host` 查询表粒度账号详情，包含其完整权限配置。

## **请求结构**

Plain Text

```
POST /v2/instance/account/tableLevel/detail HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json

{
  "instanceId": "rds-RX7mPB1o",
  "user": "user1",
  "host": "%"
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

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| user | String | 账号名 |
| host | String | 来源主机 |
| password | String | 密码（一般不返回明文） |
| type | String | 账号类型 |
| superUserFlag | String | 是否超级用户 |
| remark | String | 备注 |
| privilege | TableLevelPrivilegeRequest | 权限定义，见下表 |

**TableLevelPrivilegeRequest**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| type | String | 权限类型 |
| globals | List<String> | 全局权限项列表 |
| databases | List<TableLevelDbPrivilege> | 库级权限列表，见下表 |
| tables | List<TableLevelTbPrivilege> | 表级权限列表，见下表 |
| proxys | List<ProxyWrFlagInfo> | Proxy 读写配置列表，见下表 |

**TableLevelDbPrivilege**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| db | String | 数据库名 |
| privs | List<String> | 该库授予的权限项列表 |

**TableLevelTbPrivilege**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| db | String | 数据库名 |
| table | String | 表名 |
| privs | List<String> | 该表授予的权限项列表 |

**ProxyWrFlagInfo**

| 参数名称 | 类型 | 描述 |
| --- | --- | --- |
| appId | String | Proxy 实例 ID |
| account | String | 关联账号名 |
| wrFlag | String | 读写标识 |

## **请求示例**

Plain Text

```
POST http://rds.bj.baidubce.com/v2/instance/account/tableLevel/detail
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json

{
  "instanceId": "rds-RX7mPB1o",
  "user": "user1",
  "host": "%"
}
```

## **返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5

{
  "user": "user1",
  "host": "%",
  "type": "common",
  "superUserFlag": "0",
  "remark": "",
  "privilege": {
    "type": "custom",
    "globals": ["SELECT"],
    "databases": [{"db": "db1", "privs": ["SELECT"]}],
    "tables": [{"db": "db1", "table": "t1", "privs": ["SELECT"]}],
    "proxys": []
  }
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

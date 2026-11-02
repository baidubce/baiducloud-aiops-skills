# 表粒度新增账号API

## **接口描述**

为指定 RDS 实例新增一个表粒度账号，可同时设置全局 / 库 / 表三级权限。

## **请求结构**

Plain Text

```
POST /v2/instance/{instanceId}/account/tableLevel/create HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json

{
  "user": "user1",
  "host": "%",
  "password": "P@ssw0rd",
  "type": "common",
  "superUserFlag": "0",
  "remark": "",
  "privilege": {
    "type": "custom",
    "globals": ["SELECT"],
    "databases": [{"db": "db1", "privs": ["SELECT", "INSERT"]}],
    "tables": [{"db": "db1", "table": "t1", "privs": ["SELECT"]}]
  }
}
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL参数 | RDS 实例 ID |

### **请求体参数**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| user | String | 是 | 账号名，需匹配账号名规则 |
| host | String | 否 | 来源主机 |
| password | String | 否 | 账号密码 |
| type | String | 否 | 账号类型 |
| superUserFlag | String | 否 | 是否超级用户 |
| remark | String | 否 | 备注 |
| privilege | TableLevelPrivilegeRequest | 否 | 权限定义，见下表 |

**TableLevelPrivilegeRequest**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| type | String | 否 | 权限类型 |
| globals | List<String> | 否 | 全局权限项列表 |
| databases | List<TableLevelDbPrivilege> | 否 | 库级权限列表，见下表 |
| tables | List<TableLevelTbPrivilege> | 否 | 表级权限列表，见下表 |
| proxys | List<ProxyWrFlagInfo> | 否 | Proxy 读写配置列表，见下表 |

**TableLevelDbPrivilege**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| db | String | 否 | 数据库名 |
| privs | List<String> | 否 | 该库授予的权限项列表 |

**TableLevelTbPrivilege**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| db | String | 否 | 数据库名 |
| table | String | 否 | 表名 |
| privs | List<String> | 否 | 该表授予的权限项列表 |

**ProxyWrFlagInfo**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| appId | String | 否 | Proxy 实例 ID |
| account | String | 否 | 关联账号名 |
| wrFlag | String | 否 | 读写标识 |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

无返回内容。

## **请求示例**

Plain Text

```
POST http://rds.bj.baidubce.com/v2/instance/rds-RX7mPB1o/account/tableLevel/create
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json

{
  "user": "user1",
  "host": "%",
  "password": "P@ssw0rd",
  "type": "common",
  "superUserFlag": "0",
  "remark": "",
  "privilege": {
    "type": "custom",
    "globals": ["SELECT"],
    "databases": [{"db": "db1", "privs": ["SELECT", "INSERT"]}],
    "tables": [{"db": "db1", "table": "t1", "privs": ["SELECT"]}]
  }
}
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

**错误码**

| HTTP status code | 错误码 | 错误信息 | 描述 |
| --- | --- | --- | --- |
| 400 | ParamValidationFailed | Parameter validate error. | 参数验证失败 |
| 400 | AdminPassDecryptionException | Invalid encryption code found for the admin password. | 密码 IAM 解密失败或密码为空 |
| 403 | PermissionDeny | permission denied | 用户无该接口权限 |
| 403 | InvalidInstanceStatus | instance status is invalid | 实例状态不在可操作白名单内 |
| 403 | SuperAccountExist | Super privilege account allowed to create only one. | 已存在超级账号，不能再创建 |
| 403 | PGAccountExist | PostgreSQL can only create one account. | PostgreSQL 实例已有账号，不允许再创建 |
| 403 | InvalidAction | Invalid Action. | SQLServer 实例尝试创建非 Common 类型账号 |
| 404 | ResourceNotExist | Resource do not exist. | 实例不存在 |
| 500 | InternalServerError | Internal service error. | 内部服务错误 |

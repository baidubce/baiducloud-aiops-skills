# 申请 Shard、Config Server 组件内网访问

为分片集实例的 Shard、Config Server 组件申请内网访问地址，使客户端可以通过 VPC 内网直接连接指定组件。

## 注意事项

* 仅支持分片集实例的 Shard、Config Server 组件。
* 实例必须处于允许申请内网访问的状态。
* 调用方需要具备实例的操作权限。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/allocateNodePrivateAccess?allocateNodePrivateAccess HTTP/1.1
Host: mongodb.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json
```

## 请求头域

除公共请求头域外，无其他特殊请求头域。

## 请求参数

### Path 参数

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | 是 | URL 参数 | 分片集实例 ID。框架会使用该值覆盖请求体中的`dbInstanceId`。 |

### Body 参数

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| dbInstanceId | String | 是 | 请求 Body | 数据库实例 ID，建议与 Path 中的`instanceId` 保持一致。 |
| nodeIds | Array | 是 | 请求 Body | 需要申请内网访问的 Shard 或 Config Server 组件短 ID 列表。 |
| accountPassword | String | 否 | 请求 Body | 组件账号密码。申请 Config Server 内网访问时可传入；传入后后端会解密并校验密码格式。 |

## 返回头域

除公共响应头域外，无其他特殊响应头域。

## 返回参数

无。

## 请求示例

Plain Text

```
PUT /v1/instance/m-CH2TVe/allocateNodePrivateAccess?allocateNodePrivateAccess HTTP/1.1
Host: mongodb.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json

{
  "dbInstanceId": "m-CH2TVe",
  "nodeIds": ["shd-nzDV7q", "cfg-abc123"],
  "accountPassword": "******"
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
```

# 设置加密策略API

## **接口描述**

修改指定实例的加密策略。

## **请求结构**

Plain Text

```
PUT /v1/instance/{instanceId}?updateEncryptPolicy HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
Content-Type: application/json
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| instanceId | String | 是 | 实例ID |
| backupPolicy | List< UpdateEncryptPolicyRequest> | 是 | 加密策略请求体 |

**UpdateEncryptPolicyRequest**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| encryptStrategy | List<EncryptPolicyRequest> | 是 | 加密策略配置 |

**EncryptPolicyRequest**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| encryptEnable | Boolean | 是 | 是否开启存储加密 |
| keyManagementType | String | 是 | 密钥管理方式，自托管(self\_kms)/百度KMS(baidu\_kms)，当前仅支持self\_kms |
| keyManagementServiceName | String | 是 | 密钥管理服务名称，当前为 rds |
| secretKeyID | String | 否 | 密钥ID |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

无返回内容。

## **请求示例**

Plain Text

```
PUT http://rds.bj.baidubce.com/v1/instance/rds-RX7mPB1o?updateEncryptPolicy
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json

{
  "instanceId": "rds-RX7mPB1o",
  "backupPolicy": {
    "encryptStrategy": {
      "encryptEnable": true,
      "keyManagementType": "baidu_kms",
      "keyManagementServiceName": "rds",
      "secretKeyID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  }
}
```

## **返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

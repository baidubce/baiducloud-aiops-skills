# 查询vpc列表

## 接口说明

查询VPC列表。

## 请求结构

```
GET /v{version}/task/vpc?region={region}
Host: dts.baidubce.com    
Authorization: authorization string
```

## 请求参数

| 参数名称 | 参数类型 | 是否必选 | 描述 | 示例值 | 参数位置 |
| --- | --- | --- | --- | --- | --- |
| version | String | 是 | API版本号 | "1" | URL参数 |
| region | String | 是 | 地域 | "bd" | Query参数 |

## 响应头参数

除公共头域，无其它特殊头域。

## 响应体参数

### 响应体字段数据结构说明

| 参数名称 | 参数类型 | 是否必选 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **success** | **Boolean** | 是 | 是否成功 | true |
| **result** | **Result** | 是 | 返回结果 | result |

### Result字段数据结构说明

| 参数名称 | 参数类型 | 是否必选 | 描述 | 示例值 |
| --- | --- | --- | --- | --- |
| **vpcs** | **vpc []** | 是 | 可用区列表 | vpc |

## 请求示例

```
GET /v1/task/vpc?region=bd
Host: dts.baidubce.com    
Content-Type:application/json
Authorization:bce-auth-v1/5a6f0606bf5e48f29dd132aa76aa5182/2017-06-12T13:13:05Z/1800/content-type;host;x-bce-date/8baeafe6bfc35b0cf6205e87e4ce6c0dbb442375951ace4d16e6c7a4dab95943
```

## 响应示例

```
HTTP/1.1 200 OK
{
  "vpcs": [{
        "vpcId": "86568b59-babd-4db9-adda-185a8ca5c965",
        "shortId": "vpc-gwe9zqdk2i32",
        "name": "rdsop-bd",
        "cidr": "192.168.0.0/16",
        "status": 0,
        "securityGroupNum": 0,
        "subnetNum": 0,
        "createTime": "2022-05-31T10:15:52Z",
        "description": "",
        "defaultVpc": false,
        "ipv6Cidr": "",
        "tags": null,
        "auxiliaryCidr": null,
        "relay": false
    }]
}
```

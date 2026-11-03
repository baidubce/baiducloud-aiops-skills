# 自动续费API

## 自动续费资源列表查询接口getRenewResourceList

### 接口描述

分页获取预付费资源自动续费详情。

### 权限说明

请求发起人需要具有合法的AccessKeyID和SecretAccessKey才能发起请求，请参考 鉴权认证。

### 注意事项

如果请求中没有用户验证信息（即匿名访问），返回403 Forbidden，错误信息：AccessDenied。

### 请求结构

Plain Text

```
POST /v{version}/renew/resource/list HTTP/1.1 
Host: billing.baidubce.com 
ContentType: application/json; charset=utf-8
Content-Length: <Content_Length>
Authorization: authorization string
{
  "queryAccountId":"your account id",
  "serviceType":"BCC",
  "region":"bj",
  "expiredDays":30,
  "shortOrInstanceIds":null,
  "pageNo":1,
  "pageSize":100
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 名称 | 类型 | 参数位置 | 描述 | 是否必须 |
| --- | --- | --- | --- | --- |
| queryAccountId | String | RequestBody参数 | 查询资源账户，若为空则表示当前登陆账户。只有主账户可以代查其财务圈（或者虚商组织）子账户的资源信息，其他查询场景会提示 | AccessDenied |
| serviceType | String | RequestBody参数 | 产品类型，例：BCC，EIP等，注意仅允许查询支持自动续费的产品 | 必须 |
| region | String | RequestBody参数 | 区域，bj,su,gz等 | 可选 |
| expiredDays | Integer | RequestBody参数 | 查询预付费资源过期天数，可以为null，默认查询全量，不能为负，不能大于90天 | 可选 |
| shortOrInstanceIds | List< String > | RequestBody参数 | 资源长短ID列表，可以通过订单 或者 月账单等OPEN API查询到相关感兴趣的资源ID信息。 | 可选 |
| pageNo | Integer | RequestBody参数 | 分页查询的页数，从1开始计数，缺省值为1 | 可选 |
| pageSize | Integer | RequestBody参数 | 每页包含的最大数量，最大数量通常不超过1000，缺省值为100。 | 可选 |

### 响应头域

除公共头域外，无其它特殊头域。

### 响应参数

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| accountId | String | 查询账户不是子账户时，返回查询账户accountId；是子账户时，返回查询账户所在企业组织的主账户的accountId |
| loginName | String | 查询账户不是子账户时，返回查询账户的登录名；是子账户时，返回查询账户所在企业组织的主账户的登录名 |
| subAccountId | String | 查询账户不是子账户时，返回”/”；是子账户时，返回查询账户的accountId |
| subLoginName | String | 查询账户不是子账户时，返回”/”；是子账户时，返回查询账户的登录名 |
| ouName | String | 查询账户不是子账户时，返回”/”；是子账户时，返回查询账户所在组织单元的单元名 |
| pageNo | Integer | 分页查询编号，从1开始计数 |
| pageSize | Integer | 分页查询分页大小 |
| totalCount | Integer | 当前查询条件总条目 |
| resources | List< RenewResource > | 资源自动续费信息详情列表 |

### 请求示例

> 说明：一次请求最多返回100个资源的自动续费的信息。

Plain Text

```
POST / HTTP/1.1
Host: billing.baidubce.com
Date: Wed, 06 Apr 2019 06:34:40 GMT
Authorization: AuthorizationString
```

### 响应示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: d4591fcf-025b-46bc-81eb-91ddda4e27bc
Server: BWS
Date: Tue, 09 Apr 2019 11:01:10 GMT
Content-Type: application/json;charset=UTF-8 
{
     "accountId":"xxx",
     "loginName":"xxx",
     "subAccountId":"/",
     "subLoginName":"/",
     "ouName":"/",
     "pageNo":1,
     "pageSize":20,
     "totalCount":1,
     "resources":[
      {
          "serviceType":"BCC",
          "region":"bj",
          "shortId":"resource short id",
          "instanceId":"resource uuid",
          "expireTime":"2019-01-31T16:00:00Z",
          "aloneRenewEnable":true,
          "alreadyRenewSet":true,
          "renewTimeUnit":"month",
          "renewTime":5,
          "nextRenewTime":"2019-01-31"
        }
       ]
}
```

## 为预付费资源配置自动续费接口createRenewResourceRule

### 接口描述

针对支持自动续费的产品，针对相关的预付费资源，进行配置自动续费的规则。返回参数为空。

### 权限说明

请求发起人需要具有合法的AccessKeyID和SecretAccessKey才能发起请求，请参考 鉴权认证。

### 注意事项

如果请求中没有用户验证信息（即匿名访问），返回403 Forbidden，错误信息：AccessDenied。

### 请求结构

Plain Text

```
POST /v{version}/renew/resource/rule/create HTTP/1.1 
Host: billing.baidubce.com 
ContentType: application/json; charset=utf-8
Content-Length: <Content_Length>
Authorization: authorization string
{
  "accountId":"your account id",
  "serviceType":"BCC",
  "region":"bj",
  "instanceId":"resource uuid",
  "renewTimeUnit":"month",
  "renewTime":5
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 名称 | 类型 | 参数位置 | 描述 | 是否必须 |
| --- | --- | --- | --- | --- |
| accountId | String | RequestBody参数 | 账户ID，若不传，标记当前登录账户；若传，仅支持加入主账户财务圈组织的子账户的账户ID，由财务圈主账户发起请求，标志主账户代替子账户进行资源管理 | 可选 |
| serviceType | String | RequestBody参数 | 产品类型，例：BCC，EIP等 | 必须 |
| region | String | RequestBody参数 | 区域，例如：bj | 必须 |
| instanceId | String | RequestBody参数 | 资源长ID，是资源的唯一标示uuid，指定需要配置的资源 | 必须 |
| renewTimeUnit | String | RequestBody参数 | 自动续费时长单位，只有两种，month&year，分别表示按月和按年 | 必须 |
| renewTime | String | RequestBody参数 | 自动续费时长，renewTimeUnit为month表示月数，可选月份为1-9个月，renewTimeUnit为年标志年数，可选年数为1-3年 | 必须 |

## 数据类型

### Model对象定义

#### RenewResource 资源自动续费关联信息

| 名称 | 类型 | 描述 |
| --- | --- | --- |
| serviceType | String | 产品类型，例：BCC，BOS等 |
| region | String | 区域，例如：bj |
| shortId | String | 资源短ID |
| accountId | String | 订单所有者账户ID |
| instanceId | String | 资源长ID |
| expireTime | String | 预付费资源当前到期时间，UTC格式参考yyyy-MM-ddTHH:mm:ssZ |
| aloneRenewEnable | Boolean | 是否可以单独开通自动续费，当前仅CDS的系统盘不支持单独开通自动续费 |
| alreadyRenewSet | Boolean | 该预付费资源实例是否已经开通了自动续费 |
| renewTimeUnit | String | 自动续费时长单位，只有两种，month&year，分别表示月和年 |
| renewTime | String | 自动续费时长，renewTimeUnit为month表示月数，renewTimeUnit为年标志年数 |

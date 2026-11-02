# 删除部署集API

## 请求说明

通过调用API删除部署集。
有绑定的实例，不支持删除。

## 请求结构

Plain Text

```
DELETE /v1/deploySet/{deploySetId} HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| deploySetId | String | Path | 是 | 部署集ID。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无特殊返回参数。

## 请求示例

Plain Text

```
DELETE /v1/deploySet/dset-cb0ce309-aee1-4309-b041-85532fe36738 HTTP/1.1
Host: redis.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 1214cca7-4ad5-451d-9215-71cb844c0a50
Content-Type: application/json;charset=UTF-8
```

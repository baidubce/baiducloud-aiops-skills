# 删除IP白名单

### 请求说明

删除IP白名单。

### 请求结构

Plain Text

```
PUT /v2/group/{groupId}/white_list/delete HTTP/1.1
Host: redis.{region}.baidubce.com
Authorization: authorization string
{
  "whiteLists" : [ "whiteLists0", "whiteLists1" ]
}
```

### 请求头域

除公共头域外，无其它特殊头域。

### 请求参数

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| groupId | String | 是 | URL参数 | 热活实例组ID |
| whiteLists | List<String> | 是 | RequestBody参数 | IP列表，逗号分隔 |

  

### 返回头域

除公共头域外，无其它特殊头域。

### 返回参数

无特殊返回参数。

### 请求示例

Plain Text

```
PUT /v2/group/scs-group-qpplfjtozixy/white_list/delete HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json 
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
{
  "whiteLists" : [ "127.0.0.1", "111.112.113.114/32" ]
}
```

### 返回示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

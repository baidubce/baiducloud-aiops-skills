# 发起大版本升级API

## **接口描述**

对指定实例发起大版本升级操作。

mysql引擎不支持跨版本升级，每次只能升级一个大版本，版本顺序直接参考 [MySQL版本](https://cloud.baidu.com/doc/RDS/s/9jwvz0wd3#mysql%E7%89%88%E6%9C%AC)

mysql升级前需进行前置检查和迁移评估，通过后可发起；pg引擎发起大版本升级前无需此操作

SQL Server引擎不支持

## **请求结构**

Plain Text

```
PUT /v{version}/rds/instance/{instanceId}?upgradeMajorVersion HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

## **请求头域**

除公共头域外，无其它特殊头域。

## **请求参数**

| 参数名称 | 类型 | 是否必选 | 参数位置 | 描述 |
| --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | API版本号。此接口值为1 |
| instanceId | String | 是 | URL参数 | 实例ID |

## **请求体参数**

| 参数名称 | 类型 | 是否必选 | 描述 |
| --- | --- | --- | --- |
| targetMajorVersion | String | 是 | 目标大版本 |
| effectiveTime | String | 是 | 任务类型， immediate - 立即升级 timewindow - 时间窗口 |

## **返回头域**

除公共头域外，无其它特殊头域。

## **返回参数**

无返回内容。

## **请求示例**

Plain Text

```
PUT http://rds.bj.baidubce.com/v1/rds/instance/rds-RX7mPB1o?upgradeMajorVersion
Host: rds.bj.baidubce.com
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2015-08-11T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
Content-Type: application/json

{
  "targetMajorVersion": "8.0",
  "effectiveTime": "immediate"
}
```

## **返回示例**

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: d8752367-38e8-45e4-b4c7-e53be3137ce5
```

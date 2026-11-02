# 获取SSL加密证书

**接口说明**

获取SSL加密证书。

**请求结构**

Plain Text

```
GET /v{version}/instance/ssl/static/ca HTTP/1.1
Host: rds.bj.baidubce.com
Authorization: authorization string
```

**请求头域**

除公共头域外，无其他特殊头域。

**请求参数**

| 参数名称 | 参数类型 | 是否必须 | 参数位置 | 示例值 | 描述 |
| --- | --- | --- | --- | --- | --- |
| version | Integer | 是 | URL参数 | 1 | API 版本号 |

**返回头域**

除公共头域外，无其他特殊头域。

**返回参数**

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| caContent | String | ca证书内容 |

**请求示例**

Plain Text

```
GET   /v1/instance/ssl/static/ca HTTP/1.1
HOST: rds.bj.baidubce.com
Content-Type: application/json
Authorization: bce-auth-v1/f81d3b34e48048fbb2634dc7882d7e21/2017-11-21T04:17:29Z/3600/host/74c506f68c65e26c633bfa104c863fffac5190fdec1ec24b7c03eb5d67d2e1de
```

**返回示例**

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "caContent": “
    "-----BEGIN CERTIFICATE-----
	MIIC7DCCAdQCAQEwDQYJKoZIhvcNAQELBQAwPDE6MDgGA1UEAwwxTXlTUUxfU2Vy
	dmVyXzUuNy4xN19BdXRvX0dlbmVyYXRlZF9DQV9DZXJ0aWZpY2F0ZTAeFw0xODA0
	MTAxMTE3MzlaFw0yODA0MDcxMTE3MzlaMDwxOjA4BgNVBAMMMU15U1FMX1NlcnZl
	cl81LjcuMTdfQXV0b19HZW5lcmF0ZWRfQ0FfQ2VydGlmaWNhdGUwggEiMA0GCSqG
	SIb3DQEBAQUAA4IBDwAwggEKAoIBAQDUSZaTHZnFHOEFlWIZvVZddJIaPu0j+ev8
	xTr8oC/b/G+YCe2FQ4EZQydgmAw/IxuVDUxUpZ6KXyiGQ0EXw0jFm6bvZNrCyr0w
	XrRYFK4/iFJux+KCp+WhMmaj64niKZadyDpDHanuccfB/HbttaS1NUoj744UvOys
	tyrc2kuTkArBnoSuSejR8Sn4lshh05r/TWw49A4+b2olbSEdkwU8RpBRfuVW47wT
	n3uj/MlOKA+gO8AJeBfMEkIl+rwBTrGEw9nall1AZUHKoDkYOUHO/jY9GjrlgefR
	0xG846RMHvspLMy8OivxxwI9+wu/orw8MS82J1n/aGDSncupAlgFAgMBAAEwDQYJ
	KoZIhvcNAQELBQADggEBAEt844mRxc5VYtwjy+HhudX4cA6gBS+OhxprCu+w2hpM
	7IP3oFg/TDYBj6il0dORYHKh6sfwVtq9O2aB3401GoAptY2E45FPV/3FihK6EuFh
	8oPhWfiHkuy/l50TCNcFExF88X2+1WwbpclE6wtl2i3rZQFgMsXSFjzfe/fPdENf
	1+c44Jn2NLKQuCoeQ3loilutAhyUaw46i5QVECKbFKduf+QrKtm/lZoqOLw622pp
	thUkwhDQtiGoXJ1q0QPtk+90puXWL9/6KfPZAK6s8nc1q1YhdPrjcgLvywzKjAOA
	KdqkT9XW27fQk1I+wpXEz2qH9p0BD+nwA9JqR92aPyM=
	-----END CERTIFICATE-----"
    ”
}
```

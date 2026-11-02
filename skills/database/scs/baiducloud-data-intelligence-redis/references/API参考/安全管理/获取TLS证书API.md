# 获取TLS证书API

## 请求说明

通过调用API来获取Redis的TLS证书。

## 请求结构

Plain Text

```
GET /v1/instance/{instanceId}/tls
Host: redis.{region}.baidubce.com
Authorization: authorization string
```

## 请求头域

除公共头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 集群ID |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

| 参数名称 | 参数类型 | 描述 |
| --- | --- | --- |
| status | String | ca证书状态：tocreate（创建中）、inuse（使用中）、todelete（删除中）、deleted（已删除、已失效） |
| createTime | String | 创建时间。 |
| expireTime | String | 过期时间。 |
| ca | String | ca证书。 |

## 请求示例

Plain Text

```
GET /v1/instance/scs-bj-elahimuhxjia/tls HTTP/1.1
HOST: redis.bj.baidubce.com
Content-Type: application/json   
Authorization: bce-auth-v1/0255cb4f78f140728045b551d6a317ec/2018-11-13T05:46:05Z/1800/host/70268ec1d0491c86e67f345ad3aee4cf7f8924dade9b7f3e2f1a95814a00c129
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
x-bce-request-id: 7869616F-7A68-6977-656E-406261696475
Content-Type: application/json
{
    "status": "inuse",
    "createTime": "2024-10-25T03:28:16Z",
    "expireTime": "2025-10-25T03:28:16Z",
    "ca": "-----BEGIN CERTIFICATE-----\nMIIEnTCCAoWgAwIBAgICBVAwDQYJKoZIhvcNAQELBQAwADAeFw0yNDEwMjUwMzI4\nMTZaFw00NDEwMjUwMzI4MTZaMAAwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIK\nAoICAQDJFfSiMhLGhzpe5w6FGzA4SdT34J1A8YiKFXHzkFb8RPAH8QM6EzYWNnAp\nTWRCFzLRlR4zQYMvXS7hAkdODimlOvqhZ26Z4CYTgc9EsLGCKPXeH6YI4252ltHm\nU4zfuICvnKKU6C63PFxkVUzHy/vqnpV6UE6h37EhJ6KMKORb49hhZH7vswQH4sd8\nYh5i+mxoTsRssreY0amTGaVudaRjGrDr/S6fml9o+tbY04rfsEpGW+3WhAaDmFyA\nqHUqhYkh1c4fFLrRwFuAK1GBF2JlMZ/fErANsG2RCbWJ8a758MfRBwCX2unk1r0y\n7wBPnuOqH618BrR+pUNC1upyBKwQDl9+jCOSXIxrFjJv7kiCw+ENTW66hIRaZ/Vo\nJwhlpexip70xucGSawPBr4c/gk2BMpSfhhOrA0BU/GpO7nSNlxj4fagQNCEbfESG\nSGanXSEI0yC0CumVLJQeHz8yezpwi/hXy6uU7Wfsl8pEzBC7uYawV05mrsydE0hU\nm8mGUsdHLCJElrEgYC0b/7B8WgPtqfiVXgQBdfUOxPViFfz8WLQMuGTWdHmLAQly\n9xAuYkBXbZXxMfrDC/PvuOMMy2Uv8ZtC0llQdkAYtdsS95/4pvRZjo88pJAz6S6n\nbO6/tHlkmsxE2v87j8AbAY9Qyx5AybU40zBw3djoqCjjeYW8pQIDAQABoyEwHzAd\nBgNVHQ4EFgQUgnx/eMuUYJSMipmCbtLj1I6Foo8wDQYJKoZIhvcNAQELBQADggIB\nADpl0jDmiBGajg5C5kJc2+ijJ0R0QqoIBaCrY4vJhjPeixMRGjyoptILOhMXSGoV\nSmj0NM30AqsIfG6OavkoBWiPY597Qx7fr9g0oT188+QGhHBJkEdNDTuar1iHp4h9\n94kMgwSPByUAID4nPCkk9w3w5qGX2FDVitpvIDykJQkKkLgZMzT8i/z400OFdBK7\n7vV74RFzKBgFdKUb8aq9z690zqygedDsbkpAS6LMJG1D1o28NtzuC8VvmGA5+qXu\n+NZEaCVGy5Z5Wa33mA9iJIxMb+X2KzpNuVL0PP/L3G88GBln/JZMzu1ZWHYA/vpb\nx47KPtH7saAUhF4kOajf/wC/GqzSBQXmJ7CyJnJfPhjIeAIGWEGDNXF6AHESzhL7\nxJfH4QuyiYxNZ0vLIVVObyhnGPiLAiR2SrLiZ1FuM8lA3U2YNiywFWVxNrmJ5fBW\nmDK/Uug9NGx4jdpCNDmS7HgOK2G+ls1tVZU7EDmrGt+2B68SwgxRgVfUg1P6nRbM\nahBLHuf+5aGd2c+b1MVA5ODgEaHTNyFOUQw8PzCnrUJLTb/5KIl59uT5PA4O9BRN\nRdTRr4BXjoGcsDZhZCKgPmDC4var4omNRHBgDl8WqD7boImIXBAZOK9pbFHesTFD\nF4aqka1Kx6c48cmomRnUmbSgEfNvwcXHpaDu9sXh1E91\n-----END CERTIFICATE-----\n"
}
```

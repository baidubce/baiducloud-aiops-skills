# Sample-Code

以查询实例列表接口为例，进行说明。请查看以下示例：

## Python示例

Plain Text

```
# -*- coding: utf-8 -*-
import json
import httplib
from datetime import datetime
import sign_sample  # 鉴权计算模块，参考百度云鉴权认证机制

if __name__ == "__main__":
    signer_obj = sign_sample.BceCredentials('730fxxxxxxxxxxxxxxx', '75xxxxxxxxxxxxxxxxxxxxxx')   #百度云账号的ak、sk

    request = {
        'method': 'GET',
        'uri': '/v1/instance',
        'params': {},
        'headers': {
            'host': 'rds.bj.baidubce.com',  # RDS openAPI的endpoint
            'x-bce-date': datetime.utcnow(),
            'x-bce-if-match': 'v1'
            }
        }
    requestBody = {}

    auth = sign_sample.sign(signer_obj, request["method"], request["uri"],request["headers"], request["params"],0,1800, request["headers"]) 
    print "Authorization:" + auth

    req = httplib.HTTPConnection(request["headers"]["host"])     
    request['headers']["Authorization"] = auth 
    req.request(request['method'], request['uri'], json.dumps(requestBody), request['headers'])

    response = req.getresponse()
    print "httpStatus: " + str(response.status)
    print "header: " + str(response.getheaders())
    print json.loads(response.read())
```

## 其他参考

鉴权与认证Sample Code：[查看详情](/doc/Reference/s/wjwvz1xt2)

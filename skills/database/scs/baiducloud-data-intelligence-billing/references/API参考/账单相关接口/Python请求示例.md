# Python请求示例

## 资源月账单查询Python demo代码示例

### 前置条件

**pip install bce-python-sdk**

### 请求示例

Plain Text

```
from baidubce.auth import bce_v1_signer
from baidubce import protocol
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.http import bce_http_client, http_content_types, http_headers
from baidubce.http import handler
from baidubce.http import http_methods

def query_demo(config, month, begin_time, end_time, product_type, service_type, page_no, page_size):      
    return bce_http_client.send_request(
        config,
        bce_v1_signer.sign,
        [handler.parse_error, handler.parse_json],
        http_methods.GET,
        b"/v1/bill/resource/month",
        None,
        {http_headers.CONTENT_TYPE: http_content_types.JSON},
        {
            "month": month,
            "beginTime": begin_time,
            "endTime": end_time,
            "productType": product_type,
            "serviceType": service_type,
            "pageNo": page_no,
            "pageSize": page_size
         })
         
if __name__ == '__main__':
    conf = BceClientConfiguration(
        credentials=BceCredentials("替换成用户的AccessKey", "替换成用户的SecretKey"),
        endpoint="billing.baidubce.com",
        protocol=protocol.HTTP,
        connection_timeout_in_mills=60000
    )
 
    res = query_demo(conf, "2021-02", "2021-02-01", "2021-02-28", "postpay", "BCC", 1, 10)
    print(res.raw_data)  # 打印出http响应
```

# API规格

## 公共请求头

下表列出了所有 Redis API 所携带的公共头域。HTTP 协议的标准头域不在这里列出。

| 头域（Header） | 是否必须 | 说明 |
| --- | --- | --- |
| Authorization | 必须 | 包含Access Key与请求签名 |
| Content-Type | 可选 | application/json; charset=utf-8 |
| x-bce-date | 可选 | 表示日期的字符串，符合BCE API规范 |
| x-bce-content-sha256 | 可选 | 表示内容部分的SHA256签名的十六进制字符串。这里内容指HTTP Request Payload Body。即Content部分在被HTTP encode之前的原始数据 |

公共头域将在每个Redis
API中出现，是必需的头域，其中x-bce-content-sha256头域只出现在POST和PUT请求中。

POST、PUT、DELETE等请求数据放在request body中。

## 公共响应头

下表列出了所有 Redis API 的公共响应头域。HTTP 协议的标准响应头域不在这里列出。

| 头域（Header） | 说明 |
| --- | --- |
| Content-Type | 只支持JSON格式，application/json; charset=utf-8 |
| x-bce-request-id | Redis后端生成，并自动设置到响应头域中 |

其中，request id使用UUID version4由Redis服务生成。

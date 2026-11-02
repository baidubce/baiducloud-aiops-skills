# API简介

Redis API依据BCE API规范进行设计，符合简单易用原则，对外提供 Restful API。

Redis API对于每个 HTTP 请求，认证签名放在 Authorization 头域中，后端统一认证。且后端在 Response 头域中会添加 x-bce-request-id，作为请求唯一标识，方便追踪定位问题。

如果您是初次调用百度智能云产品的API，可以观看[API入门视频指南](https://cloud.baidu.com/doc/APIGUIDE/index.html)，快速掌握调用API的方法。

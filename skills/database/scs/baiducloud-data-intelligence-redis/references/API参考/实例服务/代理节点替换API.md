# 代理节点替换API

## 请求说明

**云数据库 Redis**支持通过调用API替换实例中的**代理节点（Proxy）**。代理节点是实例的接入层组件，负责客户端连接管理、请求转发与负载均衡，是实例高可用的关键一环。当单个或多个代理节点出现异常时，可通过在控制台或OpenAPI一键完成替换，替换后的新节点会自动同步配置并重新接入集群。

**使用说明：**

* Redis 集群架构均支持代理节点替换。
* 支持替换单个代理节点，也支持批量替换多个代理节点。
* 实例状态须为「运行中」才可执行替换。
* 执行时间支持「立即执行」与「维护窗口执行」两种方式：`isDefer=false` 表示立即执行，`isDefer=true` 表示创建维护窗口任务。
* **替换代理节点期间，连接中断时间小于 1 分钟**，建议在业务低峰期执行，并确保业务具备自动重连能力。

## 请求结构

Plain Text

```
PUT /v1/instance/{instanceId}/proxyNode
Host: scs.bj.baidubce.com
Authorization: authorization string
{
    "proxyList": ["proxy-node-1", "proxy-node-2"],
    "defer": false
}
```

## 请求头域

除公共请求头域外，无其它特殊头域。

## 请求参数

| 参数名称 | 参数类型 | 参数位置 | 是否必须 | 描述 |
| --- | --- | --- | --- | --- |
| instanceId | String | Path | 是 | 实例ID。 |
| proxyList | List<String> | Body | 是 | 待替换的代理节点列表。支持单选、批量选择。 |
| defer | Boolean | Body | 否 | 是否维护时间内执行。`false` 表示立即执行；`true` 表示创建维护窗口任务。默认值为 `false`。 |

## 返回头域

除公共头部，无其它特殊头部。

## 返回参数

无。

## 请求示例

Plain Text

```
PUT /v1/instance/scs-bj-elahimuhxjia/proxyNode
Host: scs.bj.baidubce.com
Authorization: authorization string
{
    "proxyList": ["proxy-node-1", "proxy-node-2"],
    "defer": false
}
```

## 返回示例

Plain Text

```
HTTP/1.1 200 OK
Content-Type: application/json;charset=UTF-8
x-bce-request-id: 73c4e74c-310d-4a5e-8d4e-d70b9e0a2e33
```

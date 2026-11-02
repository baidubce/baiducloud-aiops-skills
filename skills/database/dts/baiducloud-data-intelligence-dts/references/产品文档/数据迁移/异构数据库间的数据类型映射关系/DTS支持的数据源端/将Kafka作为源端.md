# 将Kafka作为源端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称 DTS），将源端为自建Kafka实例或者消息服务 for Kafka实例中的数据迁移至目标端为Kafka（含自建/消息服务）实例的场景。

## 2. 将Kafka作为DTS源的前置条件

1. Kafka版本需要在0.10及以上。
2. Kafka已配置好访问控制参数（无访问控制、SASL/PLAIN、SASL/SCRAM-SHA-256、SASL/SCRAM-SHA-512）。
3. 确保Kafka的网络连通性，注意为DTS服务器开通[IP白名单](https://cloud.baidu.com/doc/DTS/s/cjwvxji7o)。

## 3. 将Kafka作为DTS源的注意事项

1. 仅支持目标端为Kafka，暂不支持目标端为其他数据类型。
2. 仅支持增量同步，支持配置同步开始时间（Topic中最早Message、启动任务后新产生的Message、自定义起始时间）。
3. 支持针对同一源端Kafka配置多个消费者消费数据。

## 4. 使用Kafka作为源

### 4.1 连接设置

#### 4.1.1 创建任务

首先，在创建任务界面配置数据传输任务的部分上下游连接信息。
源端可根据数据源接入方式选择不同的接入类型：

**接入类型：自建数据存储（百度消息服务-共享版）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_a8dd262.png)

* 接入类型：支持百度消息服务共享版实例。
* 数据类型：固定选择Kafka。
* 地域：百度消息服务共享版实例所在的百度云逻辑地域。
* 并发消费者数量：并发消费者，每一个消费者对应一个子任务。并发消费者数量与最终费用相关。

**接入类型：自建数据存储（百度消息服务-专享版）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7021208.png)

* 接入类型：支持百度消息服务专享版实例。
* 数据类型：固定选择Kafka。
* 地域：百度消息服务专享版实例所在的百度云逻辑地域。
* 并发消费者数量：并发消费者，每一个消费者对应一个子任务。并发消费者数量与最终费用相关。

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_5dbdc9f.png)

* 接入类型：支持公网Kafka实例。
* 数据类型：固定选择Kafka。
* 地域：自建数据存储实例所在的百度云逻辑地域。
* 并发消费者数量：并发消费者，每一个消费者对应一个子任务。并发消费者数量与最终费用相关。

**接入类型：自建数据存储（专线接入）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_1abd36a.png)

* 接入类型：支持专线接入Kafka实例。
* 数据类型：固定选择Kafka。
* 地域：自建数据存储实例所在的百度云逻辑地域。
* 并发消费者数量：并发消费者，每一个消费者对应一个子任务。并发消费者数量与最终费用相关。
* 专线接入所在网络：仅接入类型选择专线接入时存在。专线接入有三个可选项分别为：该地域的VPC列表、该地域的可用区列表、选定可用区对应的子网列表。VPC列表中请选择专线所在的VPC。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_84d419d.png)

* 允许一键反向：源端Kafka数据流暂不支持开启一键反向。
* 链路规格：根据限流需求按需选择。

完成配置后点击【下一步】按钮完成创建任务，返回列表页。

#### 4.1.2 配置任务

列表页点击任务操作栏右侧【配置任务】按钮进入配置任务界面。

![image](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6947226.png)

**接入类型：百度消息服务-共享版**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7e5100e.png)

* topic：接入类型为百度消息服务-共享版时，表示百度消息服务-共享版主题。

**接入类型：百度消息服务-专享版**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7f4f3ee.png)

* 实例ID：接入类型为百度消息服务-专享版时，表示百度消息服务-专享版集群名称/ID。
* topic：接入类型为百度消息服务-专享版时，表示百度消息服务-专享版主题。

**接入类型：公网**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_b847443.png)

* 版本：Kafka 0.9版本不支持消费者组，因此固定选择0.10及以上。
* Broker列表：支持格式IP:端口，IP与端口以英文冒号分割，多个地址以英文逗号分隔，如：182.168.1.1:9092,182.168.1.2:9093。
* topic：接入类型为百度消息服务-专享版时，表示百度消息服务-专享版主题。
* 访问控制：支持 无访问控制 或 SASL/PLAIN TEXT。
* 鉴权机制：若访问控制选择SASL/PLAIN TEXT，需要选择Kafka实例配置的鉴权机制。目前支持：SASL/PLAIN、SASL/SCRAM-SHA-256、SASL/SCRAM-SHA-512。
* 账号：若访问控制选择SASL/PLAIN TEXT，需要填入Kafka实例配置的访问账号。
* 密码：若访问控制选择SASL/PLAIN TEXT，需要填入Kafka实例配置的访问密码。

**接入类型：专线接入**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_a96e692.png)

* 版本：Kafka 0.9版本不支持消费者组，因此固定选择0.10及以上。
* Broker列表：支持格式IP:端口，IP与端口以英文冒号分割，多个地址以英文逗号分隔，如：182.168.1.1:9092,182.168.1.2:9093。
* topic：接入类型为百度消息服务-专享版时，表示百度消息服务-专享版主题。
* 访问控制：支持 无访问控制 或 SASL/PLAIN TEXT。
* 鉴权机制：若访问控制选择SASL/PLAIN TEXT，需要选择Kafka实例配置的鉴权机制。目前支持：SASL/PLAIN、SASL/SCRAM-SHA-256、SASL/SCRAM-SHA-512。
* 账号：若访问控制选择SASL/PLAIN TEXT，需要填入Kafka实例配置的访问账号。
* 密码：若访问控制选择SASL/PLAIN TEXT，需要填入Kafka实例配置的访问密码。
* 授权白名单：若Kafka实例配置了网络白名单限制，请在白名单中加入此处的授权白名单IP，确保Kafka实例可与该IP连通。

完成配置后点击【授权白名单进入下一步】，进入对象映射配置页。

### 4.2 对象映射

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_f772d14.png)

配置任务-对象映射界面源端Kafka配置参数说明如下：

* 迁移类型：仅支持增量迁移。
* 分区同步策略：仅支持按原始Key分配。
* 限制传输速度：增量迁移阶段更细粒度的限流策略，支持按照每秒迁移的行数和每秒迁移的数据量限制任务的传输速度。
* 重试时间：源端/目标端实例无法连接后自动重试，用户可根据实际情况调整重试时间，或者在源端和目标端的实例释放后尽快释放DTS实例。
* Buffer：本地内存缓冲消息个数，默认为1000。
* 传输对象：源端Kafka实例仅支持传输对象为整个实例。

完成配置后点击【保存并预检查】，开始执行预检查。

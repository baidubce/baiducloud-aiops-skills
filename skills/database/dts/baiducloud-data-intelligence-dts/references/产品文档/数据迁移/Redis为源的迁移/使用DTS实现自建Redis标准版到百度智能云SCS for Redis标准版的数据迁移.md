# 使用DTS实现自建Redis标准版到百度智能云SCS for Redis标准版的数据迁移

## 1 概览

本文主要介绍自建 Redis 标准版实例和云数据库 SCS for Redis 标准版实例之间的数据迁移。

* Redis标准版：**单分片主从架构**的Redis集群，技术架构参见：[Redis产品架构](https://cloud.baidu.com/doc/SCS/s/mjxbn357r#%E6%95%B0%E6%8D%AE%E9%93%BE%E8%B7%AF)
* Redis企业集群版：**多分片sharding架构**的Redis集群，技术架构参见：[Redis产品架构](https://cloud.baidu.com/doc/SCS/s/mjxbn357r#%E6%95%B0%E6%8D%AE%E9%93%BE%E8%B7%AF)
* Redis社区集群版：即**Redis官方推出的Redis Cluster**，详细介绍参见：[Scaling with Redis Cluster](https://redis.io/docs/management/scaling/)

## 2 需求场景

适用于使用百度智能云数据传输服务DTS（以下简称DTS），将自建 Redis 标准版实例的数据，通过公网/专线迁移到云数据库 SCS for Redis 标准版实例中。

## 3 方案概述

### 3.1 迁移前置条件

* Redis标准版支持的版本为：**2.8、3.x、4.x、5.x、6.x、7.x**
* 源端Redis标准版实例必须能够执行`PSYNC`命令
* 目标Redis实例的存储空间需大于源Redis标准版实例已使用的存储空间
* 只支持**整个实例**的迁移

### 3.2 前置工作

为保证全量迁移阶段Redis标准版实例可以缓存增量数据，并在全量迁移结束后可以继续执行增量迁移，您需要确保参数`repl-backlog-size`、`client-output-buffer-limit`满足迁移需求。

如下为调参示例，您可以根据业务的实际情况灵活调整参数取值。

Plain Text

```
config set repl-backlog-size 2147483648
config set client-output-buffer-limit "slave 0 0 0"
```

### 3.3 注意事项

* DTS在执行全量迁移时将占用源库和目标库一定的资源，可能会导致数据库负载上升。如果数据库业务量较大或服务器规格较低，可能会加重数据库压力，甚至导致数据库服务不可用。建议您在执行数据同步前谨慎评估，在业务低峰期执行数据同步。
* 如果源库中的某些Key使用了过期（expire）策略，由于可能存在Key已过期但未被及时删除的情况，所以在目标库中查看到的Key数量（例如通过info命令查看）会比源库的Key数量少。**源和目标库中，未设置过期策略或未过期的Key数量是一致的。**
* 对于List类型KEY，DTS在执行全量迁移时，不会清空下游已有的数据，因此可能导致出现重复数据。
* 增量迁移阶段，为了计算增量同步延迟，DTS会在源端Redis实例中插入一个key：`DTS_REDIS_TIMESTAMP_HEARTBEAT`，用于记录更新时间点。**同步过程中会过滤该Key，同步任务结束，该Key就会过期**。

## 4 配置步骤

### 4.1 配置数据迁移

#### 4.1.1 创建任务

首先，在创建任务界面配置数据传输任务的部分上下游连接信息，创建任务时支持源端/目标端位置选择**百度智能云数据库**和**自建数据存储**。

**源端**可根据数据源接入方式选择不同的接入类型：

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_2728dec.png)

* **接入类型**：支持公网/BCC/BBC/DCC自建Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：自建数据存储所在的百度云逻辑地域。

**接入类型：自建数据存储（VPC）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_5292cb8.png)

* **接入类型**：支持VPC接入Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：VPC接入实例所在的百度云逻辑地域。

**接入类型：自建数据存储（专线）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_69076b1.png)

* **接入类型**：支持专线接入Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：专线接入实例所在的百度云逻辑地域。
* **专线接入所在网络**：**仅接入类型选择专线接入时存在**。专线接入有三个可选项分别为：该地域的VPC列表、该地域的可用区列表、选定可用区对应的子网列表。**VPC列表中请选择专线所在的VPC**。

**目标端**接入类型可直接选择云数据库SCS for Redis：

**接入类型：云数据库SCS for Redis**

![DST_SCS.png](https://bce.bdstatic.com/doc/bce-doc/DTS/DST_SCS_b1135be.png)

* **接入类型**：支持云数据库SCS for Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：云数据库SCS for Redis实例所在的百度云逻辑地域。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_1d0a853.png)

* **允许一键反向**：**建议开启**。开启后，可以支持割接后执行一键反向，一键建立反向回滚同步任务。
* **链路规格**：根据限流需求按需选择。

完成配置后点击**【下一步】**完成创建任务，返回列表页。

#### 4.1.2 配置任务

列表页点击任务操作栏右侧**【配置任务】**按钮进入配置任务界面。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6947226.png)

由于创建任务页面开启了允许一键反向，可以看到正向数据流与反向数据流两部分配置。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_8452913.png)

* **正向数据流**：将云下环境的数据迁移到云上环境。
* **反向数据流**：在流量割接后，如果希望保留云下环境用于灾备，可以通过反向数据流将云上环境的业务流量同步回云下环境，保证云上与云下数据一致。

##### 4.1.2.1 正向数据流

**正向数据流 - 源端**连接信息配置：

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_a4c4f9f.png)

* **IP**：接入类型为公网时，需要填入Redis标准版实例IP。
* **实例ID**：接入类型为BCC/BBC/DCC自建时，表示BCC/BBC/DCC实例ID。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

**接入类型：自建数据存储（VPC）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d705fc7.png)

* **专线接入所在网络**：可选项会展示该地域的VPC列表，**VPC列表中请选择Redis标准版实例所在的VPC**。
* **IP**：接入类型为VPC接入时，需要填入Redis标准版实例IP。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

**接入类型：自建数据存储（专线）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_0187334.png)

* **IP**：接入类型为专线接入时，需要填入Redis标准版实例IP。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

**正向数据流 - 目标端**连接信息配置：

**接入类型：云数据库SCS for Redis**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_11dfd66.png)

* **实例ID**：接入类型为云数据库SCS for Redis时，表示云数据库SCS for Redis标准版实例ID。
* **密码**：云数据库SCS for Redis标准版实例的访问密码。

##### 4.1.2.2 反向数据流

配置反向数据流时

* 如果确认正向数据流的源端可接受写流量，且反向数据流写入正向数据流的源端不会影响业务的稳定性，此处可以选择[是]。**反向数据流会把正向数据流的源端当作目标端，目标端当作源端**，无需额外配置。
* 如果正向数据流的源端不可写，或反向数据流写入正向数据流的源端会影响业务的稳定性，此处应当选择[否]。您可以单独配置反向数据流。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6854370.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_f0552f1.png)

完成配置后点击**【授权白名单进入下一步】**，进入对象映射配置页。

##### 4.1.2.3 对象映射

配置任务-对象映射界面Redis标准版配置参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_70255b9.png)

* **迁移类型**：支持全量迁移和增量迁移，其中增量迁移为必选。
* **自定义同步点**：**仅当迁移类型中只选择增量迁移时生效**。DTS将从指定的同步点开始增量同步。当未指定增量的自定义同步点时，DTS将默认从最新同步点进行增量迁移。若指定的自定义同步点失效时会导致任务报错，建议连接源端实例后执行`info replication`，将获取到的master\_repl\_offset值作为源端最新的增量同步点，offset示例：179123563。
* **同步点失效的处理策略**：增量迁移阶段，若任务的同步点在源端Redis标准版实例中已失效，DTS支持选择不同的处理策略。

  + 同步点失效时直接报任务失败：用户可以自行清空目标端实例数据后，重新执行全量+增量迁移，适用于对数据一致性要求更高的业务场景；
  + 同步点失效时自动重新开始全量和增量迁移：DTS在感知到同步点失效后，不清空目标端实例数据，直接重新开始执行全量+增量迁移。**这一策略可能会导致目标端实例中数据多于源端实例**，适用于对传输链路稳定性要求更高的业务场景；
* **限制传输速度**：全量迁移和增量迁移阶段更细粒度的限流策略，支持按照**每秒迁移的行数**和**每秒迁移的数据量**限制任务的传输速度。
* **重试时间**：源端/目标端实例无法连接后自动重试，用户可根据实际情况调整重试时间，或者在源端和目标端的实例释放后尽快释放DTS实例。
* **传输对象**：源端Redis标准版实例仅支持传输对象为整个实例。

完成配置后点击**【保存并预检查】**，开始执行预检查。

#### 4.1.3 预检查和启动任务

DTS会在预检查阶段对任务配置及源端/目标端Redis标准版实例做检查，确认是否满足数据迁移需求。其中，检查结果分为四类：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_9f7ddd2.png)

* **失败**：表示该检查项不通过，且严重影响数据迁移的正常执行。失败的检查项无法强制通过，建议您根据修复建议处理后重新预检查。
* **警告**：表示该检查项不通过，对数据迁移有一定负面影响。您可以确认后点击【强制通过】强制通过检查。
* 成功：表示该检查项通过。
* 未开始：表示该检查项未开始执行。

若出现检查失败，您可以修改任务配置后重新执行预检查，或返回列表页后重新执行预检查。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_89a80a7.png)

预检查通过后，您可直接启动数据迁移任务。此时DTS会启动正向数据流执行数据迁移，挂起反向数据流。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_26fba43.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_f1274b2.png)

### 4.2 执行数据校验

当观察到正向数据流进入复制变更阶段，且延迟追平后，可以点击任务ID进入任务详情页。选择右侧数据一致性校验，点击【创建一致性校验】后，可根据需要调整数据校验配置。完成后点击【确定】，启动数据校验。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_3a78f18.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_eacf30e.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_8b4ec2b.png)

执行完成的数据校验任务状态为**任务结束**，您可以点击【查看详情】查看数据校验详情，可以看到校验结果和数据不一致统计。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_af01534.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_89537b3.png)

### 4.3 建立反向同步

**在流量割接期间，您需要先确保源端（云下环境）Redis标准版实例已停写**，此时即可执行一键反向。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_b947fd1.png)

点击【一键反向】后，会展示当前正向数据流的同步延迟，推荐在当前延时值小于预期延时的条件下进行一键反向操作，避免延迟过大导致的数据不一致。

在您确认源端（云下环境）Redis标准版实例已停写，无增量数据产生后，点击【确定】即可开始执行一键反向。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d6a0b38.png)

此时任务会进入**挂起中**状态，开始挂起正向数据流，启动反向数据流。等待一段时间后，任务将恢复**运行中**状态，此时正向数据流已被挂起，反向数据流开始运行。一键反向执行完成。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_59afeb2.png)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_8bf3d77.png)

**在一键反向执行完成后，您可以把流量割接到目标端（云上环境）SCS for Redis标准版实例**。此时反向数据流会将云上环境的流量同步到云下环境。

## 5 DTS支持迁移的Redis数据类型

| Redis数据类型 | DTS是否支持 |
| --- | --- |
| STRING | 支持 |
| HASH | 支持 |
| SET | 支持 |
| ZSET | 支持 |
| LIST | 支持 |
| STREAM | 支持 |
| LUA SCRIPT | 支持 |

## 相关产品

[云数据库 SCS for Redis](https://cloud.baidu.com/product/scs.html)

# 将Redis标准版作为源端

## 1 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称 DTS），将源端为自建Redis标准版或者云数据库SCS for Redis标准版实例中的数据迁移至目标端为Redis（含标准版/企业集群版/社区集群版）实例的场景。

* Redis标准版：**单分片主从架构**的Redis集群，技术架构参见：[Redis产品架构](https://cloud.baidu.com/doc/SCS/s/mjxbn357r#%E6%95%B0%E6%8D%AE%E9%93%BE%E8%B7%AF)
* Redis企业集群版：**多分片sharding架构**的Redis集群，技术架构参见：[Redis产品架构](https://cloud.baidu.com/doc/SCS/s/mjxbn357r#%E6%95%B0%E6%8D%AE%E9%93%BE%E8%B7%AF)
* Redis社区集群版：即**Redis官方推出的Redis Cluster**，详细介绍参见：[Scaling with Redis Cluster](https://redis.io/docs/management/scaling/)

## 2 将Redis标准版作为DTS源的前置条件

* 支持的版本为：**2.8、3.0、3.2、4.0、5.0、6.0、7.0**
* 源端Redis标准版实例必须能够执行`PSYNC`命令
* 目标Redis实例的存储空间需大于源Redis标准版实例已使用的存储空间
* 只支持**整个实例**的迁移

## 3 将Redis标准版作为DTS源的注意事项

* DTS在执行全量迁移时将占用源库和目标库一定的资源，可能会导致数据库负载上升。如果数据库业务量较大或服务器规格较低，可能会加重数据库压力，甚至导致数据库服务不可用。建议您在执行数据同步前谨慎评估，在业务低峰期执行数据同步。
* 如果源库中的某些Key使用了过期（expire）策略，由于可能存在Key已过期但未被及时删除的情况，所以在目标库中查看到的Key数量（例如通过info命令查看）会比源库的Key数量少。**源和目标库中，未设置过期策略或未过期的Key数量是一致的。**
* 增量迁移阶段，为了计算增量同步延迟，DTS会在源端Redis实例中插入一个key：`DTS_REDIS_TIMESTAMP_HEARTBEAT`，用于记录更新时间点。**同步过程中会过滤该Key，同步任务结束，该Key就会过期**。
* 源端Redis标准版同步到目标端Redis社区集群版（Redis Cluster）的操作限制：由于Redis社区集群版只允许单个命令操作单个slot，若在源库执行多Key操作时，Key不在同一个slot或涉及多个slot，则会出现报错：`CROSSSLOT Keys in request don't hash to the same slot`。建议在DTS同步过程中仅执行单Key操作，以免导致链路中断。

## 4 使用Redis标准版作为源

使用Redis标准版实例作为源端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考最佳实践文档。在**任务配置**和**对象映射**部分与其他数据源有些许不同。

### 4.1 连接设置

#### 4.1.1 创建任务

首先，在创建任务界面配置数据传输任务的部分上下游连接信息，创建任务时支持源端位置选择**百度智能云数据库**和**自建数据存储**。

**接入类型：云数据库SCS for Redis**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7e3d502.png)

* **接入类型**：支持云数据库SCS for Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：云数据库SCS for Redis实例所在的百度云逻辑地域。

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_2728dec.png)

* **接入类型**：支持公网/BCC/BBC/DCC自建接入Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：自建数据存储接入实例所在的百度云逻辑地域。

**接入类型：自建数据存储（VPC）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_5292cb8.png)

* **接入类型**：支持VPC接入Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：VPC接入实例所在的百度云逻辑地域。

**接入类型：自建数据存储（专线）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_69076b1.png)

* **接入类型**：支持专线自建接入Redis标准版实例。
* **数据类型**：固定选择Redis标准版。
* **地域**：专线接入实例所在的百度云逻辑地域。
* **专线接入所在网络**：**仅接入类型选择专线接入时存在**。专线接入有三个可选项分别为：该地域的VPC列表、该地域的可用区列表、选定可用区对应的子网列表。**VPC列表中请选择专线所在的VPC**。

完成配置后点击**【下一步】**完成创建任务，返回列表页。

#### 4.1.2 配置任务

列表页点击任务操作栏右侧**【配置任务】**按钮进入配置任务界面。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6947226.png)

**接入类型：云数据库SCS for Redis**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_12d8547.png)

* **实例ID**：接入类型为云数据库SCS for Redis时，表示云数据库SCS for Redis标准版实例ID。
* **密码**：云数据库SCS for Redis标准版实例的访问密码。

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_a4c4f9f.png)

* **IP**：接入类型为公网时，需要填入Redis标准版实例IP。
* **实例ID**：接入类型为BCC/BBC/DCC自建接入时，表示BCC/BBC/DCC实例ID。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

**接入类型：自建数据存储（VPC）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d705fc7.png)

* **专线接入所在网络**：可选项会展示该地域的VPC列表，**VPC列表中请选择Redis标准版实例所在的VPC**。
* **IP**：接入类型为VPC自建接入时，需要填入Redis标准版实例IP。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

**接入类型：自建数据存储（专线）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_0187334.png)

* **IP**：接入类型为专线自建接入时，需要填入Redis标准版实例IP。
* **端口**：Redis标准版实例的访问端口。
* **密码**：Redis标准版实例的访问密码。

完成配置后点击**【授权白名单进入下一步】**，进入对象映射配置页。

### 4.2 对象映射

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_2617b08.png)

配置任务-对象映射界面源端Redis标准版配置参数说明如下：

* **迁移类型**：支持全量迁移和增量迁移，其中增量迁移为必选。
* **自定义同步点**：**仅当迁移类型中只选择增量迁移时生效**。DTS将从指定的同步点开始增量同步。当未指定增量的自定义同步点时，DTS将默认从最新同步点进行增量迁移。若指定的自定义同步点失效时会导致任务报错，建议连接源端实例后执行`info replication`，将获取到的master\_repl\_offset值作为源端最新的增量同步点，offset示例：179123563。
* **同步点失效的处理策略**：增量迁移阶段，若任务的同步点在源端Redis标准版实例中已失效，DTS支持选择不同的处理策略。

  + 同步点失效时直接报任务失败：用户可以自行清空目标端实例数据后，重新执行全量+增量迁移，适用于对数据一致性要求更高的业务场景；
  + 同步点失效时自动重新开始全量和增量迁移：DTS在感知到同步点失效后，不清空目标端实例数据，直接重新开始执行全量+增量迁移。**这一策略可能会导致目标端实例中数据多于源端实例**，适用于对传输链路稳定性要求更高的业务场景；
* **限制传输速度**：全量迁移和增量迁移阶段更细粒度的限流策略，支持按照**每秒迁移的行数**和**每秒迁移的数据量**限制任务的传输速度。
* **重试时间**：源端/目标端实例无法连接后自动重试，用户可根据实际情况调整重试时间，或者在源端和目标端的实例释放后尽快释放DTS实例。
* **传输对象**：源端Redis标准版实例仅支持传输对象为整个实例。

完成配置后点击**【保存并预检查】**，开始执行预检查。

## 5 DTS支持的Redis源数据类型

| Redis数据类型 | DTS是否支持 |
| --- | --- |
| STRING | 支持 |
| HASH | 支持 |
| SET | 支持 |
| ZSET | 支持 |
| LIST | 支持 |
| STREAM | 支持 |
| LUA SCRIPT | 支持 |

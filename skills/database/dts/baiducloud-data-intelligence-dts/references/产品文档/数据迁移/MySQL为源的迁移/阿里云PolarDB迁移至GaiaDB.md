# 阿里云PolarDB迁移至GaiaDB

## 1 概览

本文主要介绍阿里云 PolarDB 实例和云原生数据库 GaiaDB 实例之间的数据迁移。

* 云原生数据库 GaiaDB ：详细介绍参见：[云原生数据库 GaiaDB](https://cloud.baidu.com/doc/GaiaDB/index.html)

## 2 需求场景

适用于使用百度智能云数据传输服务 DTS（以下简称 DTS ），将阿里云 PolarDB 实例的数据，通过公网迁移到云原生数据库 GaiaDB 实例中。

## 3 方案概述

### 3.1 迁移前置参数设置

首先，您需要对迁移所需的 PolarDB 参数值进行设置。若需要增量迁移，源端 PolarDB 需要开启 binlog 功能，且 binlog\_format 参数值需要设置为"ROW"， binlog\_row\_image 参数值需要设置为"FULL"。

### 3.2 公网连接及IP白名单设置

您需要打开阿里云 PolarDB 的公网访问功能以便 DTS 可以连通。进入 PolarDB 实例详情的“基本信息”一栏，点击下方"数据库连接"->"主地址"->"公网"后的"申请"按钮，在弹出的对话框中输入自定义的访问地址前缀，点击确定即可开通。成功开通后，主地址的公网一栏会显示用于公网访问的域名和端口信息，可用于后续 DTS 任务的连接配置。

![polardb开公网.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/polardb%E5%BC%80%E5%85%AC%E7%BD%91_760e8a6.jpg)

开通 PolarDB 公网访问后，您还需要在实例的IP白名单中对 DTS 的IP段进行放行。进入 PolarDB 实例详情侧边栏的"配置与管理"->"集群白名单"页面，点击"新增白名单分组"按钮，在右侧弹出的页面中输入IP白名单分组名称（例如 "baidu\_dts"），在白名单内IP地址一栏中填写 DTS 的IP地址列表（DTS 各个地域对应的IP地址列表请查看文档[添加DTS服务IP白名单](https://cloud.baidu.com/doc/DTS/s/cjwvxji7o)）。

![polardb开ip白名单.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/polardb%E5%BC%80ip%E7%99%BD%E5%90%8D%E5%8D%95_f29ca60.jpg)

### 3.3 数据库账号设置

最后，您还需要在 PolarDB 实例中创建用于 DTS 迁移使用的数据库账号。进入 PolarDB 实例详情侧边栏的"配置与管理"->"账号管理"页面，点击"创建账号"按钮，在右侧弹出的页面中输入账号名及密码，账号类型请务必选择"高权限账号"。点击确定即可创建对应的数据库账号。

![polardb创建账号.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/polardb%E5%88%9B%E5%BB%BA%E8%B4%A6%E5%8F%B7_06a50ea.jpg)

### 3.4 注意事项

* DTS在执行全量迁移时将占用源库和目标库一定的资源，可能会导致数据库负载上升。如果数据库业务量较大或服务器规格较低，可能会加重数据库压力，甚至导致数据库服务不可用。建议您在执行数据同步前谨慎评估，在业务低峰期执行数据同步。
* 如果源库中待迁移的表没有主键或唯一约束，且所有字段没有唯一性，可能会导致目标数据库中出现重复数据。

## 4 配置步骤

### 4.1 配置数据迁移

#### 4.1.1 创建任务

首先，在 DTS 创建任务界面配置数据传输任务的部分上下游连接信息：

* **源端位置**选择 "自建数据存储"；
* **源端接入类型**选择 "公网"；
* **源端数据类型**选择 "MySQL"；
* **源端地域**根据阿里云 PolarDB 所在的地域就近选择；
* **目标端位置**选择 "百度智能云数据库"；
* **目标端接入类型**选择 "云原生数据库 GaiaDB"；
* **目标端数据类型**选择 "GaiaDB"；
* **目标端地域**选择 GaiaDB 实例所在的地域。

![百度DTS创建任务.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/%E7%99%BE%E5%BA%A6DTS%E5%88%9B%E5%BB%BA%E4%BB%BB%E5%8A%A1_9b86b24.jpg)

* **同步方向**：选择"单向同步"。
* **允许一键反向**：**建议开启**。开启后，可以支持割接后执行一键反向，一键建立反向回滚同步任务。
* **链路规格**：根据限流需求按需选择。

完成配置后点击**【下一步】按钮**完成创建任务，返回列表页。

#### 4.1.2 配置任务

列表页点击任务操作栏右侧**【配置任务】**按钮进入配置任务界面。

![百度DTS配置任务.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/%E7%99%BE%E5%BA%A6DTS%E9%85%8D%E7%BD%AE%E4%BB%BB%E5%8A%A1_2610716.jpg)

由于创建任务页面开启了允许一键反向，可以看到正向数据流与反向数据流两部分配置。

* **正向数据流**：将云下环境的数据迁移到云上环境。
* **反向数据流**：在流量割接后，如果希望保留云下环境用于灾备，可以通过反向数据流将云上环境的业务流量同步回云下环境，保证云上与云下数据一致。

##### 4.1.2.1 正向数据流

**正向数据流 - 源端**连接信息配置：

**接入类型：自建数据存储（公网）**

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_dfde532.png)

* **主机名/IP**：填入 3.2 一节中开通的 PolarDB 实例公网域名。
* **端口**：填入 PolarDB 实例的端口。
* **账号**：填入 3.3 一节中创建的 PolarDB 实例的访问账号。
* **密码**：填入 3.3 一节中创建的 PolarDB 实例的访问密码。

**正向数据流 - 目标端**连接信息配置：

**接入类型：云原生数据库 GaiaDB**

![目标端GaiaDB信息.jpg](https://bce.bdstatic.com/doc/bce-doc/DTS/%E7%9B%AE%E6%A0%87%E7%AB%AFGaiaDB%E4%BF%A1%E6%81%AF_541615a.jpg)

* **实例ID**：接入类型为云原生数据库 GaiaDB 时，可以直接选择要迁移到的目标端实例ID。

##### 4.1.2.2 反向数据流

配置反向数据流时

* 如果确认正向数据流的源端可接受写流量，且反向数据流写入正向数据流的源端不会影响业务的稳定性，此处可以选择[是]。**反向数据流会把正向数据流的源端当作目标端，目标端当作源端**，无需额外配置。
* 如果正向数据流的源端不可写，或反向数据流写入正向数据流的源端会影响业务的稳定性，此处应当选择[否]。您可以单独配置反向数据流。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6854370.png)

完成配置后点击**【授权白名单进入下一步】**按钮，进入对象映射配置页。

##### 4.1.2.3 对象映射

配置任务-对象映射界面MySQL版配置参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_f496a61.png)

* **迁移类型**：支持结构迁移、全量迁移和增量同步，其中增量同步为必选。
* **同步语句选择**：增量同步阶段，支持指定需要同步的SQL语句类型，可多选。
* **特殊DDL过滤**：增量同步阶段，在选择了同步DDL语句的情况下，支持过滤。
* **自定义同步位点**：当未选择结构迁移和全量迁移，仅选择了增量同步时，可以指定增量同步的起始位点，DTS支持选择三种起始位点。详情可见：[自定义同步位点](https://cloud.baidu.com/doc/DTS/s/Zktxy8bw2)。

  + binlog：以binlog位点作为起始位点，格式参考：mysql-bin.000001:4；
  + gtidset：以gtid集合作为起始位点，格式参考：3f36fc07-d556-11e9-b75c-a0d3c1fa9c05:1-2454163；
  + timestamp：以时间点作为起始位点，DTS将根据该时间点自动找寻对应的binlog或gtidset位点；
* **限制传输速度**：全量迁移和增量同步阶段更细粒度的限流策略，支持按照**每秒迁移的行数**和**每秒迁移的数据量**限制任务的传输速度。详情可见：[迁移限速](https://cloud.baidu.com/doc/DTS/s/Xlez0ok7o)。
* **重试时间**：源端/目标端实例无法连接后自动重试，用户可根据实际情况调整重试时间，或者在源端和目标端的实例释放后尽快释放DTS实例。
* **同步Online DDL**：指定是否同步由gh-ost, pt-osc、DMS工具执行的表结构变更操作。详情可见：[同步Online DDL](https://cloud.baidu.com/doc/DTS/s/6l1eqk7vw)。
* **传输对象**：DTS支持三种配置传输对象方式。

  + 整个实例：将源端除系统库外的所有数据迁移到目标端，不迁移的系统库为：mysql、sys、information\_schema、performance\_schema。
  + 手动选择：选择此选项时，将出现如下的库表选择页面，页面左侧会展示源端所有的库表信息，在页面左侧选择需要迁移的库表，库表信息将会被自动添加到页面右侧。点击右侧库表名旁的"编辑"按钮可以设置库表名映射、列名映射、行过滤、列过滤(白名单)、列过滤(黑名单)等功能；（注："编辑"功能在一键反向任务中不可用）。
  + 模式匹配（在一键反向任务中，该选项不可用），详情可见：[自定义迁移对象](https://cloud.baidu.com/doc/DTS/s/dl1es97ak)。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_a1f0bfa.png)

完成配置后点击**【保存并预检查】按钮**，开始执行预检查。

#### 4.1.3 预检查和启动任务

DTS会在预检查阶段对任务配置及源端/目标端实例做检查，确认是否满足数据迁移需求。其中，检查结果分为四类：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_fe0a338.png)

* **失败**：表示该检查项不通过，且严重影响数据迁移的正常执行。失败的检查项无法强制通过，建议您根据修复建议处理后重新预检查。
* **警告**：表示该检查项不通过，对数据迁移有一定负面影响。您可以确认后点击【强制通过】按钮强制通过检查。
* 成功：表示该检查项通过。
* 未开始：表示该检查项未开始执行。

若出现检查失败，您可以修改任务配置后重新执行预检查，或返回列表页后重新执行预检查。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7d95bca.png)

预检查通过后，您可直接启动数据迁移任务。此时DTS会启动正向数据流执行数据迁移，挂起反向数据流。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_602e5dd.png)
![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_54d8091.png)

### 4.2 执行数据校验

在列表页观察到正向数据流进入复制变更阶段，且延迟追平。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_b3fa337.png)

可以点击任务ID进入任务详情页。选择右侧数据一致性校验，点击【创建一致性校验】按钮后，可根据需要调整数据校验配置。完成后点击【确定】按钮，启动数据校验。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_3172e82.png)
![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d7dd8cc.png)

执行完成的数据校验任务状态为**任务结束**，您可以点击【查看详情】查看数据校验详情，可以看到校验结果和数据不一致统计。对校验结果的详细解释可见：[创建数据校验任务](https://cloud.baidu.com/doc/DTS/s/jl443q585)

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_7cbc45b.png)
![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_59cfff3.png)

### 4.3 建立反向同步

**在流量割接期间，您需要先确保源端 PolarDB 实例已停写**，此时即可执行一键反向。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d5e724b.png)

点击【一键反向】按钮后，会展示当前正向数据流的同步延迟，推荐在当前延时值小于预期延时的条件下进行一键反向操作，避免延迟过大导致的数据不一致。

在您确认源端 PolarDB 实例已停写，无增量数据产生后，点击【确定】按钮即可开始执行一键反向。

* **自定义同步点**：执行一键反向时，可以指定反向任务的同步起始点，若不指定，则默认从当前时间点开始同步。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_0fa7696.png)

此时任务会进入**挂起中**状态，开始挂起正向数据流，启动反向数据流。等待一段时间后，任务将恢复**运行中**状态，此时正向数据流已被挂起，反向数据流开始运行。一键反向执行完成。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_1a83934.png)
![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_f94feab.png)

**在一键反向执行完成后，您可以把流量割接到目标端 GaiaDB 实例**。此时反向数据流会将云上环境的流量同步到云下环境。

## 5 DTS支持迁移的MySQL数据类型

| MySQL数据类型 | DTS是否支持 |
| --- | --- |
| BOOLEAN | 支持 |
| TINYINT | 支持 |
| SMALLINT | 支持 |
| MEDIUMINT | 支持 |
| INT | 支持 |
| BIGINT | 支持 |
| DECIMAL | 支持 |
| FLOAT | 支持 |
| DOUBLE | 支持 |
| BIT | 支持 |
| YEAR | 支持 |
| DATE | 支持 |
| TIME | 支持 |
| DATETIME | 支持 |
| TIMESTAMP | 支持 |
| CHAR | 支持 |
| VARCHAR | 支持 |
| BINARY | 支持 |
| VARBINARY | 支持 |
| TINYTEXT | 支持 |
| TEXT | 支持 |
| MEDIUMTEXT | 支持 |
| LONGTEXT | 支持 |
| TINYBLOB | 支持 |
| BLOB | 支持 |
| MEDIUMBLOB | 支持 |
| LONGBLOB | 支持 |
| SET | 支持 |
| ENUM | 支持 |
| JSON | 支持 |
| GEOMETRY | 支持 |

## 相关产品

[云原生数据库 GaiaDB](https://cloud.baidu.com/doc/GaiaDB/index.html)

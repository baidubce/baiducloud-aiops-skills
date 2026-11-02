# 将PostgreSQL作为源端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS(以下简称 DTS), 将自建PostgreSQL中的数据迁移至DTS已经支持的数据目标端的场景。

## 2. 将PostgreSQL数据库作为DTS源端的限制

* **不支持包含时区类型列的时间戳。**
* **增量同步不支持同步关系型数据库的DDL语句。**
* **一个数据迁移任务只能对一个数据库进行数据迁移，如果有多个数据库需要迁移，则需要为每个数据库创建数据迁移任务。**
* **如果源端数据库没有主键或唯一约束，且所有字段没有唯一性，可能会导致目标数据库中出现重复数据。**
* **复制多个同名但名称具有不同大小写的表（例如，table1、TABLE1 和 Table1）会导致无法预测的行为。**
* **PostgreSQL至PostgreSQL的结构迁移，暂不支持trigger、extension的迁移。**
* **PostgreSQL至异构数据源的结构迁移，暂仅支持库表结构迁移，不支持函数、视图等其他对象的迁移。**

## 3. 将PostgreSQL数据库作为源端的前置条件

### 3.1 环境要求

DTS支持将PostgreSQL 9.4 、10.10版本自建数据库作为源端。

### 3.2 数据库账号权限要求

源端：

| 数据库 | 全量迁移 | 增量迁移 |
| --- | --- | --- |
| 自建PostgreSQL数据库 | 迁移对象的select权限 | superuser |

**自建PostgreSQL数据库，数据库账号创建及授权方法请参见[CREATE USER](https://www.postgresql.org/docs/10/sql-createuser.html?spm=a2c4g.11186623.2.22.243cf4e980SPdI)和[GRANT](https://www.postgresql.org/docs/10/sql-grant.html?spm=a2c4g.11186623.2.23.243cf4e980SPdI)语法。**

### 3.3 网络配置

将DTS的IP地址加入至自建PostgreSQL的配置文件pg\_hba.conf中，并启用复制和套接字连接。

Plain Text

```
   # Replication Instance
   host all all 10.1.4.56/00 md5
   # Allow replication connections from localhost, by a user with the
   # replication privilege.
   host replication dms 10.1.4.56/00 md5
```

PostgreSQL的pg\_hba.conf配置文件控制客户端身份验证。文件通常存储在数据库集群的数据目录中。

### 3.4 源端自建PostgreSQL增量迁移准备工作

1. **安装逻辑流复制插件**

   登录自建PostgreSQL所属的服务器，下载wal2json逻辑流复制插件，下载地址如下：
   <https://github.com/eulerto/wal2json>
   按照官方指导安装wal2json插件。
2. **修改PostgreSQL相关参数配置**

   修改postgresql.conf配置文件中的如下参数：

   1. 将max\_replication\_slots 设置为大于1的整数, max\_replication\_slots的值应根据您需要同时运行的任务数进行设置。例如，要同时运行十二个任务，您需要设置至少十二个slot。

      示例：`max_replication_slots = 12`
   2. 将wal\_level 设置为logical，开启wal 逻辑日志。

      示例：`wal_level = logical`
   3. 将wal\_sender\_timeout 设置为0，复制连接处于不活跃状态的时间超过wal\_sender\_timeout 时，会被源端库终止。该参数的默认值为 60 秒，但我们建议您将该参数设置为零，这样会禁用超时机制。

      示例：`wal_sender_timeout = 0`
   4. 将max\_wal\_senders 设置为大于10的整数， max\_wal\_senders 参数用于设置可以运行的并发任务数，建议和max\_replication\_slots设置的值一致。

      示例：`max_wal_senders = 12`
3. **重启PostgreSQL数据库**
4. **将要迁移表的replica identity设置为FULL**

   Plain Text

   ```
   1ALTER TABLE TABLENAME REPLICA IDENTITY FULL;
   ```

## 4. 使用PostgreSQL数据库作为源端

使用PostgreSQL数据库作为源端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考典型实践文档。
在任务配置参数和对象映射部分与其他数据源有些许不同。

### 4.1 任务配置参数

![peizhirenwu.png](https://bce.bdstatic.com/doc/bce-doc/DTS/peizhirenwu_3fcae26.png)

如上图所示。目前DTS的源端支持公网自建PostgreSQL实例，PostgreSQL源端配置参数说明如下：

* **接入类型**：支持公网/BCC/BBC/DCC自建PostgreSQL实例。
* **数据类型**：固定选择PostgreSQL。
* **IP/端口**：自建PostgreSQL数据库的访问IP与服务端口。
* **数据库**：自建PostgreSQL数据库中待迁移的数据库名。
* **账号**：自建PostgreSQL的数据库账号。
* **密码**：该数据库账号对应的密码。

> **注意：**当接入类型为 **云数据库 RDS** 时，仅需选择目标实例，无需填写连接信息及账号密码。

### 4.2 对象映射

PostgreSQL为三级schema,当需要向两级schema的目的端进行数据迁移时, DTS提供了两种库表名映射方式供用户选择。如下图所示，选择好的迁移对象会出现在右边的已选择对象列表中。DTS支持上下游库表名映射、列过滤黑白名单等功能。可以点击【编辑】，对每一个迁移对象配置映射和过滤规则。目标数据库对象可以映射为源库中database和schema:

* **1. 数据库对象映射为源库中的Database**: 忽略PostgreSQL中的schema, PostgreSQL中不同schema下的表均映射到mysql指定库中，目标端库名默认使用源端的库名。
* **2. 数据库对象映射为源库中的Schema**: 忽略PostgreSQL中的库名，PostgreSQL中不同schema映射为mysql中不同库，目标库名默认使用源端schema名。

完成对象映射配置后，点击【保存并预检查】，启动任务的前置检查。

![peizhirenwu1.png](https://bce.bdstatic.com/doc/bce-doc/DTS/peizhirenwu1_b8ad8df.png)

## 5. DTS支持的PostgreSQL源端数据类型

下表列出了使用DTS时支持的PostgreSQL源端数据类型以及与DTS数据类型的默认映射。

有关如何查看目标端映射的数据类型的信息，请参阅有关目标端数据源的数据类型映射部分。

| PostgreSQL数据类型 | DTS字段类型 |
| --- | --- |
| INTEGER | DTS\_TYPE\_INT4 |
| INTEGER[] | DTS\_TYPE\_STRING |
| TEXT[] | DTS\_TYPE\_STRING |
| BIT | DTS\_TYPE\_BYTES |
| BIT VARYING | DTS\_TYPE\_BYTES |
| MONEY | DTS\_TYPE\_NUMBER |
| CHARACTER | DTS\_TYPE\_STRING |
| CHARACTER VARYING | DTS\_TYPE\_STRING |
| TEXT | DTS\_TYPE\_STRING |
| BYTEA | DTS\_TYPE\_BYTES |
| COMPLEX | DTS\_TYPE\_STRING |
| ENUM | DTS\_TYPE\_STRING |
| CIDR | DTS\_TYPE\_STRING |
| POINT | DTS\_TYPE\_STRING |
| LINE | DTS\_TYPE\_STRING |
| LSEG | DTS\_TYPE\_STRING |
| BOX | DTS\_TYPE\_STRING |
| PATH | DTS\_TYPE\_STRING |
| POLYGON | DTS\_TYPE\_STRING |
| CIRCLE | DTS\_TYPE\_STRING |
| INET | DTS\_TYPE\_STRING |
| MACADDR | DTS\_TYPE\_STRING |
| MACADDR8 | DTS\_TYPE\_STRING |
| JSON | DTS\_TYPE\_STRING |
| SMALLINT | DTS\_TYPE\_INT2 |
| BIGINT | DTS\_TYPE\_INT8 |
| NUMERIC(P,S) | 如果精度介于 0 和 38 之间，则使用 DTS\_TYPE\_NUMBER, 如果精度为 39 或更大的值，则使用 DTS\_TYPE\_STRING |
| DECIMAL(P,S) | 如果精度介于 0 和 38 之间，则使用 DTS\_TYPE\_NUMBER, 如果精度为 39 或更大的值，则使用 DTS\_TYPE\_STRING |
| DECIMAL | DTS\_TYPE\_STRING |
| NUMBER | DTS\_TYPE\_STRING |
| DECIMAL(p) | DTS\_TYPE\_NUMBER |
| NUMBER(p) | DTS\_TYPE\_NUMBER |
| REAL | DTS\_TYPE\_FLOAT |
| DOUBLE PRECISION | DTS\_TYPE\_DOUBLE |
| SMALLSERIAL | DTS\_TYPE\_INT2 |
| SERIAL | DTS\_TYPE\_INT4 |
| BIGSERIAL | DTS\_TYPE\_INT8 |
| TIME WITHOUT TIME ZONE | DTS\_TYPE\_TIME |
| DATE | DTS\_TYPE\_DATE |
| TIMESTAMP WITHOUT TIMEZONE | DTS\_TYPE\_DATETIME |
| INTERVAL | DTS\_TYPE\_STRING |
| BOOLEAN | DTS\_TYPE\_BOOLEAN |

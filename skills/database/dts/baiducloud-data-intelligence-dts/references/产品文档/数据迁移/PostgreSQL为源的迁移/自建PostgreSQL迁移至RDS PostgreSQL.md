# 自建PostgreSQL迁移至RDS PostgreSQL

本文主要介绍自建 PostgreSQL 实例和云数据库 RDS PostgreSQL 实例之间的数据迁移。

## 前提条件

* 自建 PostgreSQL 数据库版本为 9.4、10.10 及以上版本。
* 已创建存储空间大于自建 PostgreSQL 数据库占用存储空间的目标 RDS PostgreSQL 实例。创建方式，请参见 [创建 PostgreSQL 实例](https://cloud.baidu.com/doc/RDS/s/ejzy199f5)。

## 限制说明

| 类型 | 说明 |
| --- | --- |
| 源端限制 | * 待同步的表需具备主键或唯一约束，且字段具有唯一性，否则可能会导致目标数据库中出现重复数据。 * 如同步对象为表级别，单次同步任务支持的表数量有限，当超出数量限制，任务提交后会显示请求报错，此时建议您拆分待同步的表，分批配置多个任务，或者配置整库的同步任务。 * DTS 不支持迁移源库中的临时表、系统内部的触发器、函数、视图、拓展。 * 待迁移的数据库名称中间不能包含短划线（-），例如 dts-testdata。 * 如需进行增量迁移，WAL日志：   + 需开启，即设置 **wal\_level** 参数的值为 logical。   + 如为增量迁移任务，DTS 要求源数据库的 WAL 日志保存 24 小时以上，如为全量迁移和增量迁移任务，DTS 要求源数据库的 WAL 日志至少保留 7 天以上（您可在全量迁移完成后将 WAL 日志保存时间设置为 24 小时以上），否则 DTS 可能因无法获取 WAL 日志而导致任务失败，极端情况下甚至可能会导致数据不一致或丢失。 * 在库表结构同步和全量同步阶段，请勿执行库或表结构变更的 DDL 操作，否则会导致数据同步任务失败。 * 若源库有长事务，且实例包含增量迁移任务，则可能会导致源库长事务提交前的预写日志 WAL（Write-Ahead Logging）无法清理而堆积，从而造成源库磁盘空间不足。 |
| 其他限制 | * 一个 DTS 任务只能对一个数据库进行数据迁移，如果有多个数据库需要迁移，则需要为每个数据库创建数据迁移任务。 * 不支持包含时区类型列的时间戳。 * 复制多个同名但名称具有不同大小写的表（例如，table1、TABLE1 和 Table1）会导致无法预测的行为。 * 全量迁移会并发执行 INSERT 操作，导致目标数据库的表产生碎片，因此全量迁移完成后目标实例的表空间比源实例的表空间大。 * DTS 会在源库中创建以下临时对象，用于获取增量数据的 DDL 等。在同步期间，请勿删除源库中的临时对象，否则会导致 DTS 任务异常。临时表会在 DTS 任务结束后自动删除。    + 表：baidu\_dts\_ddl\_log   + 函数：baidu\_dts\_capture\_ddl   + 事件触发器：baidu\_dts\_capture\_ddl\_end、baidu\_dts\_capture\_ddl\_drop |
| 特殊情况 | 当目标库为 RDS PostgreSQL 时：   * 不支持 RDS 代理实例，仅支持主实例 * PostgreSQL 14、15 版本默认密码加密算法不一样，需要调整后才能正常迁移，步骤如下：   1. 修改参数 password\_encryption = 'md5'。   2. 重启 PostgreSQL 数据库。 |

## 支持的SQL操作

| 操作类型 | SQL操作语句 |
| --- | --- |
| DML | INSERT、UPDATE、DELETE |
| DDL | CREATE TABLE、CREATE TABLE ... AS SELECT、ALTER TABLE、CREATE INDEX、ALTER INDEX、DROP INDEX、TUNCATE TABLE（源库 PostgreSQL 为 PostgreSQL 11 及以上版本）、DROP TABLE **注意**：   * 不支持同步通过调用 FUNCTION 等方式执行的 DDL。 * 若源库单次提交的多条 SQL 中包含非同步对象的 DDL，则该 DDL 不会被同步。 |

## 数据库账号权限要求

| 数据库 | 结构迁移 | 全量迁移 | 增量迁移 |
| --- | --- | --- | --- |
| 源端 | pg\_catalog 的 usage 权限 | 迁移对象的 select 权限 | superuser |
| 目标端 | 迁移对象的 create、usage 权限 | schema 的 owner 权限 | schema 的 owner 权限 |

> **说明**
>
> * 自建 PostgreSQL 数据库，数据库账号创建及授权方法请参见 [CREATE USER](https://www.postgresql.org/docs/10/sql-createuser.html?spm=a2c4g.11186623.2.22.243cf4e980SPdI) 和 [GRANT](https://www.postgresql.org/docs/10/sql-grant.html?spm=a2c4g.11186623.2.23.243cf4e980SPdI) 语法。

## 准备工作

### 网络准备

将 DTS 的 IP 地址加入至自建 PostgreSQL 的配置文件 pg\_hba.conf 中，并启用复制和套接字连接。

SQL

```
   # Replication Instance
   host all all 10.1.4.56/00 md5
   # Allow replication connections from localhost, by a user with the
   # replication privilege.
   host replication dms 10.1.4.56/00 md5
```

### 迁移准备

PostgreSQL 的 pg\_hba.conf 配置文件控制客户端身份验证。文件通常存储在数据库集群的数据目录中。

1. 安装逻辑流复制插件

   登录自建 PostgreSQL 所属的服务器，下载 wal2json 逻辑流复制插件，下载地址如下： <https://github.com/eulerto/wal2json> 按照官方指导安装 wal2json 插件。
2. 修改 PostgreSQL postgresql.conf 配置文件中的如下参数：

   1. 将 max\_replication\_slots 设置为大于 1 的整数，max\_replication\_slots 的值应根据您需要同时运行的任务数进行设置。例如，要同时运行十二个任务，您需要设置至少十二个 slot。

   示例：`max_replication_slots = 12`

   2. 将 wal\_level 设置为 logical，开启 wal 逻辑日志。

   示例：`wal_level = logical`

   3. 将 wal\_sender\_timeout 设置为 0，复制连接处于不活跃状态的时间超过 wal\_sender\_timeout 时，会被源端库终止。该参数的默认值为 60 秒，但我们建议您将该参数设置为零，这样会禁用超时机制。

   示例：`wal_sender_timeout = 0`

   4. 将 max\_wal\_senders 设置为大于 10 的整数，max\_wal\_senders 参数用于设置可以运行的并发任务数，建议和 max\_replication\_slots 设置的值一致。

   示例：`max_wal_senders = 12`
3. 重启 PostgreSQL 数据库
4. 将要迁移表的 replica identity 设置为 FULL

   SQL

   ```
   1ALTER TABLE TABLENAME REPLICA IDENTITY FULL;
   ```

## 操作步骤

1. 登录 [DTS 控制台](https://console.bce.baidu.com/dts/#/dts/migration/list)。
2. 点击 **创建数据传输任务** 进入 DTS 创建任务页面，详情参见 [购买流程](https://cloud.baidu.com/doc/DTS/s/clw60a6mz)。
3. 创建任务成功后自动返回任务列表页面，选择新创建的任务，点击 **更多操作—>配置任务**。
4. 在配置任务页面，配置源库及目标库信息，本文以 **公网** 接入方式为例介绍配置流程。

   配置流程

   | 类别 | 配置 | 说明 |
   | --- | --- | --- |
   | 任务基本属性 | 任务名称 | DTS 会自动生成一个任务名称，建议配置具有业务意义的名称（无唯一性要求），便于后续识别。 |
   | 源端连接设置 | IP/端口 | 填入源端 PostgreSQL 数据库的访问 IP 与端口，本示例中填入公网地址。 |
   | 数据库 | 选择默认连接的数据库。 |
   | 账号 | 填入源端 PostgreSQL 数据库的账号。 |
   | 密码 | 填入该数据库账号对应的密码。 |
   | 目标端连接设置 | 实例 ID | 选择目标 RDS PostgreSQL 实例 ID。 |
   | 数据库 | 选择默认连接的数据库。 |
   | 账号 | 填入目标端 PostgreSQL 数据库的账号。 |
   | 密码 | 填入该数据库账号对应的密码。 |
5. 配置完成后，点击页面下方的 **授权白名单进入下一步**。

   如果源或目标数据库是 BCC/BBC/DCC 自建或 IDC 自建数据库或其他云数据库，则需要您手动添加对应地区 DTS 服务的 IP 地址，以允许来自 DTS 服务器的访问。

   > **警告：**
   >
   > DTS 自动添加或您手动添加 DTS 服务的 IP 地址段可能会存在安全风险，一旦使用本产品代表您已理解和确认其中可能存在的安全风险，并且需要您做好基本的安全防护，包括但不限于加强账号密码强度防范、限制各网段开放的端口号、内部各 API 使用鉴权方式通信、定期检查并限制不需要的网段等等。
6. 配置任务对象映射。

   | 配置 | 说明 |
   | --- | --- |
   | 迁移类型 | 根据需求及各引擎对迁移类型的支持情况，选择迁移类型。 |
   | 限制传输速度 | 根据实际情况，选择是否对全量迁移和增量同步任务进行更细粒度的限流策略设置（设置 **每秒迁移的行数** 和 **每秒迁移的数据量**），以缓解目标库压力。详情参见：[迁移限速](https://cloud.baidu.com/doc/DTS/s/Xlez0ok7o)。 |
   | 传输对象 | 手动选择：选择此选项时，在页面左侧选择需要迁移的库表，库表信息将会被自动添加到页面右侧。模式匹配：详情参见：[模式匹配](https://cloud.baidu.com/doc/DTS/s/dl1es97ak#%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D)。 |
7. 上述配置完成后，点击页面下方的 **保存并预检查**。

   > **说明**
   >
   > * 在迁移任务正式启动之前，会先进行预检查。只有预检查通过后，才能成功启动迁移任务。
   > * 如果预检查失败，请查看失败检查项的提示，并根据提示修复后重新进行预检查。
   > * 如果预检查产生警告：
   >
   >   + 对于不可以忽略的检查项，请查看失败检查项的提示，并根据提示修复后重新进行预检查。
   >   + 对于可以忽略无需修复的检查项，您可以点击 **强制通过**，在弹出的窗口中勾选风险确认信息并点击 **确定**，跳过告警检查项重新进行预检查。如果选择屏蔽告警检查项，可能会导致数据不一致等问题，给业务带来风险。
8. 前置校验提示校验成功后，点击 **立即开启任务**。
9. 迁移任务正式开始，您可以在任务列表页面查看具体进度。

## 后续操作（可选）

### 业务切换

详情参见 [业务切换流程](https://cloud.baidu.com/doc/DTS/s/Rlz2cwt8c)。

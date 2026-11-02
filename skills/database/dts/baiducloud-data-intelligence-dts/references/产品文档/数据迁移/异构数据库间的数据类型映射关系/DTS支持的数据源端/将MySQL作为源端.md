# 将MySQL作为源端

## 1 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称DTS），将自建MySQL实例或云数据库RDS MySQL实例中的数据迁移至DTS已经支持的数据目标端的场景。

## 2 将MySQL数据库作为DTS源的限制

* 如果源库中待迁移的表没有主键或唯一约束，且所有字段没有唯一性，可能会导致目标数据库中出现重复数据。
* 若需要增量迁移，源端需要开启binlog，且binlog\_format参数值需要设置为"ROW"。
* 若需要增量迁移，且源端为MySQL 5.6及以上版本，源端binlog\_row\_image参数值需要设置为"FULL"。
* 若需要增量迁移，源端server\_id参数值需要设为大于1的整数。

## 3 将MySQL数据库作为DTS源的前置条件

### 3.1 环境要求

DTS支持将MySQL 5.1、5.5、5.6、5.7或8.0版本数据库作为源。

### 3.2 数据库账号授权

| 数据库 | 结构迁移 | 全量迁移 | 增量迁移 |
| --- | --- | --- | --- |
| 源端MySQL版本为5.1时 | SELECT,SHOW VIEW,SUPER | SELECT,SHOW VIEW,SUPER | SELECT,SHOW VIEW,SUPER,REPLICATION SLAVE |
| 源端MySQL版本大于或等于5.5时 | SELECT,SHOW VIEW,REPLICATION CLIENT | SELECT,SHOW VIEW,REPLICATION CLIENT | SELECT,SHOW VIEW,REPLICATION CLIENT,REPLICATION SLAVE |

## 4 使用MySQL数据库作为DTS源

使用MySQL数据库作为源，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考最佳实践文档。在任务配置参数部分与其他数据源有些许不同。

### 连接设置

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_71580b6.png)

如上图所示，目前DTS的源端支持自建MySQL实例和云数据库RDS for MySQL实例。以选择公网自建MySQL实例为例，源端配置参数说明如下：

接入类型："公网"表示使用的是公网自建MySQL实例

数据类型：固定选择"MySQL"

主机名/IP：填写MySQL数据库的访问IP

端口：填写MySQL数据库的服务端口

账号：填写MySQL数据库的数据库账号

密码：填写MySQL数据库账号对应的密码

填写完成后可以点击"测试连通性"按钮验证填入的信息是否正确。

> **注意：**当接入类型为 **云数据库 RDS** 时，仅需选择目标实例，无需填写连接信息及账号密码。

### 对象映射

点击"授权白名单进入下一步"按钮，进入迁移对象选择页面。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_644bc5e.png)

* 在该页面，可以根据实际需求选择组合结构迁移、全量迁移和增量同步。
* 若选择了增量同步，可以指定增量同步过程中同步的SQL语句类型，当前可选的SQL语句类型包含：INSERT、UPDATE、DELETE、DDL；此外若选择了DDL语句的同步，可以额外指定是否过滤特殊的DDL同步，如DROP、和TRUNCATE语句，如下图所示。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_6cbe1ba.png)

* 传输对象包含两种选择类型："整个实例"和"手动选择"。选择"手动选择"时，在页面左边选上需要迁移的库表，库表信息将会被自动添加到页面右边；点击对应库表名旁的"编辑"按钮可以设置库表名映射、行过滤、列黑白名单过滤等功能，如下图所示。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_754fd52.png)

* 上述配置完成后，点击"保存并预检查"可开始预检查操作。

## 5 DTS支持的MySQL源数据类型

下表列出了使用DTS时支持的MySQL源数据类型以及与DTS数据类型的默认映射。
有关如何查看目标端映射的数据类型的信息，请参阅有关目标端数据源的数据类型映射部分。

| MySQL数据类型 | DTS数据类型 | DTS是否支持 |
| --- | --- | --- |
| BOOLEAN | DTS\_TYPE\_INT1 | 支持 |
| TINYINT | DTS\_TYPE\_INT1 | 支持 |
| SMALLINT | DTS\_TYPE\_INT2 | 支持 |
| MEDIUMINT | DTS\_TYPE\_INT4 | 支持 |
| INT | DTS\_TYPE\_INT4 | 支持 |
| BIGINT | DTS\_TYPE\_INT8 | 支持 |
| DECIMAL | DTS\_TYPE\_DECIMAL | 支持 |
| FLOAT | DTS\_TYPE\_FLOAT | 支持 |
| BIT | DTS\_TYPE\_BYTES(8) | 支持 |
| YEAR | DTS\_TYPE\_INT2 | 支持 |
| DATE | DTS\_TYPE\_DATE | 支持 |
| TIME(fsp) | DTS\_TYPE\_STRING | 支持 |
| DATETIME(fsp) | DTS\_TYPE\_DATETIME(fsp) | 支持 |
| TIMESTAMP(fsp) | DTS\_TYPE\_DATETIME(fsp) | 支持 |
| CHAR(N) | DTS\_TYPE\_STRING(N) | 支持 |
| VARCHAR(N) | DTS\_TYPE\_STRING(N) | 支持 |
| BINARY(N) | DTS\_TYPE\_BYTES(N) | 支持 |
| VARBINARY(N) | DTS\_TYPE\_BYTES(N) | 支持 |
| TINYTEXT | DTS\_TYPE\_STRING(255) | 支持 |
| TEXT | DTS\_TYPE\_STRING(65,535) | 支持 |
| MEDIUMTEXT | DTS\_TYPE\_STRING(16,777,215) | 支持 |
| LONGTEXT | DTS\_TYPE\_STRING(4,294,967,295) | 支持 |
| TINYBLOB | DTS\_TYPE\_BYTES(255) | 支持 |
| BLOB | DTS\_TYPE\_BYTES(65,535) | 支持 |
| MEDIUMBLOB | DTS\_TYPE\_BYTES(16,777,215) | 支持 |
| LONGBLOB | DTS\_TYPE\_BYTES(4,294,967,295) | 支持 |
| SET | - | 仅在下游为MySQL时支持 |
| ENUM | - | 仅在下游为MySQL时支持 |
| JSON | DTS\_TYPE\_STRING(4,294,967,295) | 支持 |

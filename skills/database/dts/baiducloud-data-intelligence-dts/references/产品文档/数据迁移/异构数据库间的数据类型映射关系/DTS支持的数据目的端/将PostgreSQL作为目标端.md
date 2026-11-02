# 将PostgreSQL作为目标端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS，将DTS已经支持的数据源迁移至PostgreSQL目标端中的场景。

## 2. 将PostgreSQL数据库作为DTS目标端的限制

* **不支持非PostgreSQL数据库至PostgreSQL数据库的结构迁移**。

## 3. 将PostgreSQL数据库作为DTS目标端的前置条件

### 3.1 环境要求

DTS支持将PostgreSQL10以上版本自建数据库作为目标端。

### 3.2 数据库账号权限要求

目标端：

| 数据库 | 结构迁移 | 全量迁移 | 增量迁移 |
| --- | --- | --- | --- |
| 自建PostgreSQL数据库 | 迁移对象的create、usage权限 | schema的owner权限 | schema的owner权限 |

**自建PostgreSQL数据库，数据库账号创建及授权方法请参见[CREATE USER](https://www.postgresql.org/docs/10/sql-createuser.html?spm=a2c4g.11186623.2.22.243cf4e980SPdI)和[GRANT](https://www.postgresql.org/docs/10/sql-grant.html?spm=a2c4g.11186623.2.23.243cf4e980SPdI)语法。**

## 4. 使用PostgreSQL数据库作为DTS目标端

使用PostgreSQL数据库作为目标端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考典型实践文档。
在任务配置参数和对象映射部分与其他数据源有些许不同。

### 4.1 任务配置参数

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_541f7d9.png)

如上图所示。目前DTS的目标端支持公网自建PostgreSQL实例，PostgreSQL目标端配置参数说明如下：

* **接入类型**：支持公网/BCC/BBC/DCC自建PostgreSQL实例。
* **数据类型**：固定选择PostgreSQL。
* **IP/端口**：自建PostgreSQL数据库的访问IP与服务端口。
* **数据库**：自建PostgreSQL数据库中待迁移的数据库名。
* **账号**：自建PostgreSQL的数据库账号。
* **密码**：该数据库账号对应的密码。

### 4.2 对象映射

PostgreSQL为三级schema，当需要由两级schema的源端向PostgreSQL进行数据迁移时，目前DTS会将源端库名映射为目标端的schema名。DTS提供库表名映射功能供用户选择，如下图所示，选择好的迁移对象会出现在右边的已选择对象列表中。DTS支持上下游库表名映射、列过滤黑白名单等功能。可以点击【编辑】，对每一个迁移对象配置映射和过滤规则。

完成对象映射配置后，点击【保存并预检查】，启动任务的前置检查。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_0754ef0.png)

## 5. DTS支持的PostgreSQL目标端数据类型

下表列出了使用DTS时支持的DTS数据类型与PostgreSQL目标端数据类型的默认映射。

有关如何查看源端映射的数据类型的信息，请参阅有关源端数据源的数据类型映射部分。

| DTS字段类型 | POSTGRESQL数据类型 |
| --- | --- |
| DTS\_TYPE\_INT1 | smallint |
| DTS\_TYPE\_INT2 | smallint |
| DTS\_TYPE\_INT4 | integer |
| DTS\_TYPE\_INT8 | bigint |
| DTS\_TYPE\_NUMBER | 如果precision <= 147455 && scale <= 16383 时使用decimal (p,s) ; 否则使用character varying |
| DTS\_TYPE\_FLOAT | real |
| DTS\_TYPE\_DOUBLE | double precision |
| DTS\_TYPE\_BYTES | bytea |
| DTS\_TYPE\_DATE | date |
| DTS\_TYPE\_TIME | 如果小数位数 => 0 且 <= 6 使用 time; 否则使用character varying |
| DTS\_TYPE\_DATETIME | 如果小数位数 => 0 且 <= 6 使用 datetime; 否则使用character varying |
| DTS\_TYPE\_STRING | 如果定长, 使用 character(n) ; 如果变长，使用 character varying(n) |

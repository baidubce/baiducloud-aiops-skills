# 将Oracle作为源端

## 1 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称 DTS），将自建 Oracle 实例中的数据迁移至 DTS 已经支持的数据目标端的场景。

## 2 将Oracle数据库作为DTS源的限制

* 增量同步不支持同步关系型数据库的DDL语句。
* 如果源库中待迁移的表没有主键或唯一约束，且所有字段没有唯一性，可能会导致目标数据库中出现重复数据。注意：增量同步使用物化视图日志（mlog）方案时，不支持无主键表的迁移。
* 增量同步使用物化视图日志（mlog）方案时：若需要同时选择全量和增量迁移，源端不可存在迁移表相关的物化视图日志；若只选择增量迁移，需要提前在源端创建迁移表相关的物化视图日志。
* 增量同步使用归档日志（logminer）方案时：需按要求开启归档模式和Supplemental Logging，详情可见下文：[对象映射配置](#%E5%AF%B9%E8%B1%A1%E6%98%A0%E5%B0%84)。

## 3 将Oracle数据库作为DTS源的前置条件

### 3.1 环境要求

DTS支持将Oracle 10g、11g、12c（需使用PDB连接模式）、18c（需使用PDB连接模式）、19c（需使用PDB连接模式）版本自建数据库作为源。

## 3.2 数据库账号权限要求

源端：

| 数据库 | 结构迁移 | 全量迁移 | 增量迁移 |
| --- | --- | --- | --- |
| 自建Oracle数据库 | DBA权限 | DBA权限 | DBA权限 |

自建Oracle数据库，数据库账号创建及授权方法请参见[CREATE USER](https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_8003.htm?spm=a2c4g.11186623.2.24.67b25d9fbmW9I7)和[GRANT](https://docs.oracle.com/cd/B19306_01/server.102/b14200/statements_9013.htm?spm=a2c4g.11186623.2.25.67b25d9fbmW9I7)语法。

## 4 使用Oracle数据库作为DTS源

使用Oracle数据库作为源，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考典型实践文档。 在任务配置参数部分与其他数据源有些许不同。

### 连接设置

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_204e51f.png)

如上图所示，目前DTS的源端支持自建Oracle实例，Oracle源端配置参数说明如下：

**接入类型**：支持公网、云服务器BCC、物理服务器BBC和专属服务器DDC的自建Oracle实例。

**数据类型**：固定选择Oracle。

**主机名/IP**：填写Oracle数据库的访问IP。

**端口**：填写Oracle数据库的服务端口。

**账号**：填写Oracle数据库的数据库账号。

**密码**：填写Oracle数据库账号对应的密码。

**Service Name**：填写Oracle实例的Service Name或SID。

**导出类型**：指定DTS服务从Oracle读取数据所采用的字符集，可选值为："默认"、"UTF8" 和"GBK"；选择"默认"时，DTS将使用下列语句查询得到的Oracle实例使用的字符集作为导出类型。

Plain Text

```
select userenv('language') as charset from dual
```

填写完成后可以点击"测试连通性"按钮验证填入的信息是否正确。

### 对象映射

点击"授权白名单进入下一步"按钮，进入迁移对象选择页面。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_e8a3a78.png)

* 在该页面，可以根据实际需求选择组合结构迁移、全量迁移和增量同步。
* 若选择了增量同步，可以指定增量同步过程中同步的SQL语句类型，当前可选的SQL语句类型包含：INSERT、UPDATE、DELETE，不支持DDL语句的迁移，如下图所示。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_764fec7.png)

* 如上图所示，增量同步当前支持两种可选的迁移方案：物化视图日志（mlog）方案和归档日志方案（logminer）。若选择归档日志（logminer）方案，需要满足如下要求：

  + Oracle数据库需开启归档模式（ARCHIVELOG），详情请见[ARCHIVELOG](https://docs.oracle.com/database/121/ADMIN/archredo.htm?spm=a2c4g.11186623.2.13.58d9384eanYisR#ADMIN11330)。
  + Oracle数据库需开启Supplemental Logging，且要求开启数据库级别的Minimal Supplemental Logging，对同步表要求开启ALL COLUMN LOGGING，详情请见[Supplemental Logging](https://docs.oracle.com/database/121/SUTIL/GUID-D857AF96-AC24-4CA1-B620-8EA3DF30D72E.htm?spm=a2c4g.11186623.2.12.58d9384eanYisR#SUTIL1582)。
* 传输对象当前仅支持"手动选择"。在页面左边选上需要迁移的库表，库表信息将会被自动添加到页面右边；点击对应库表名旁的"编辑"按钮可以设置库表名映射、行过滤、列黑白名单过滤等功能，如下图所示。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d966e12.png)

* 上述配置完成后，点击"保存并预检查"可开始预检查操作。

## 5 DTS支持的Oracle源数据类型

下表列出了使用 DTS 时支持的 Oracle 源数据类型以及与 DTS 数据类型的默认映射。

有关如何查看目标端映射的数据类型的信息，请参阅有关目标端数据源的数据类型映射部分。

| Oracle数据类型 | DTS字段类型 | DTS是否支持 |
| --- | --- | --- |
| number | DTS\_TYPE\_NUMBER | 支持 |
| binary\_float | DTS\_TYPE\_NUMBER（precision=65，scale=8） | 支持 |
| binary\_double | DTS\_TYPE\_DOUBLE | 支持 |
| float | DTS\_TYPE\_DOUBLE | 支持 |
| char | DTS\_TYPE\_STRING | 支持 |
| varchar2 | DTS\_TYPE\_STRING | 支持 |
| nchar | DTS\_TYPE\_STRING | 支持 |
| nvarchar2 | DTS\_TYPE\_STRING | 支持 |
| clob | DTS\_TYPE\_STRING | 支持 |
| nclob | DTS\_TYPE\_STRING | 支持 |
| blob | DTS\_TYPE\_BYTES | 支持 |
| raw | DTS\_TYPE\_BYTES | 支持 |
| long raw | DTS\_TYPE\_BYTES | 支持 |
| long | DTS\_TYPE\_STRING | 支持 |
| date | DTS\_TYPE\_DATETIME | 支持 |
| timestamp | DTS\_TYPE\_DATETIME | 支持 |
| timestamp with time zone | - | 不支持 |
| timestamp with local time zone | - | 不支持 |
| interval year to month | - | 不支持 |
| interval day to second | - | 不支持 |
| bfile | - | 不支持 |
| xmltype | - | 不支持 |
| rowid | - | 不支持 |
| urowid | - | 不支持 |
| sdo\_geometry | - | 不支持 |

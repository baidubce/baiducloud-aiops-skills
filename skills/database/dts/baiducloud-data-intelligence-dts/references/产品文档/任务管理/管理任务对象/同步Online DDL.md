# 同步Online DDL

## 使用场景

使用 gh-ost、pt-online-schema-change（下文简称 pt-osc ）工具对源库中的表执行 Online DDL 操作，需要将 Online DDL 变更产生的临时表迁移到目标库。

DTS 支持在选择迁移对象时，提前关联对象表的临时表名，在后续源库产生临时表时一并进行迁移。

使用 gh-ost 工具对表 `表名` 做 Online DDL，DTS 支持迁移临时表 `_表名_ghc`、`_表名_gho`、`_表名_del` 到目标库。

使用 pt-osc 工具对表 `表名` 做 Online DDL，DTS 支持迁移临时表 `_表名_new`、 `_表名_old` 到目标库。

## 前提条件

目前仅 MySQL、GaiaDB 支持同步 Online DDL。

## 注意事项

* 通过 DTS 进行增量迁移任务时，在源端进行 Online DDL 同步操作后，数据同步结束之前需要在目标端同时保存两份数据，即需两倍数据量的空间。若目标端空间容量小于两倍数据量的大小，则会同步失败。
* 多表归并任务中执行 Online DDL 操作导致目标端数据丢失。 通过 DTS 进行多表归并任务时，若在源端进行 Online DDL 操作，对源端的表结构等进行了调整修改。同步到目标端时，会出现数据丢失的情况。

## 同步 Online DDL 不适用场景

### Online DDL 描述

若在源端进行 Online DDL 操作，会创建临时表、变更临时表结构并将原始表的全量数据拷贝到临时表，最后会使用 rename 命令将临时表切换成新的业务表。用 gh-ost，pt-osc，DMS SQL 上线的功能可能会产生 Online DDL 的行为。

由于该工作机制，在通过 DTS 进行增量迁移时，若在源端进行 Online DDL 操作，可能会出现如下风险。

### 同步 Online DDL 可能存在的风险

以 RDS MySQL（源库）向 RDS MySQL（目标库）进行多表归并任务为例，说明源库进行 Online DDL 操作导致目标库数据缺失的情况。

**场景 1**：当用户配置了从源端1 RDS MySQL 和源端 2 RDS MySQL 到目标端 RDS MySQL 的多表归并任务，则数据迁移的逻辑如下：

* 源库 1 的表 A1 迁移至目标库表。
* 源库 2 的表 A2 迁移至目标库表。

假设源端 1 的学生信息表 A1 中有 2 条记录，源端 2 的学生信息表 A2 中有 2 条记录。则多表归并后，目标端学生信息表中应有 4 条记录。

若在源端 2 的学生信息表 A2 中进行 Online DDL 操作，修改列名字段 `ID` 为 `StudentID`。同步到目标端，会导致源端 2 的学生信息表 A2 更新后的数据替换了目标端学生信息表的数据，源端 1 的学生信息表 A1 的 2 条数据就会丢失，如下图所示。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_5fdfec4.png)

* 执行 Online DDL 操作目标端表结构与源端不一致导致目标端数据丢失，通过 DTS 进行增量迁移任务时，在源端进行 Online DDL 同步操作后，目标端表中的数据被源端表中的数据完全替换。若目标端的表结构和源端不一致，表结构差异部分（包括差异部分的全部数据）会丢失。

**场景 2**：在目标端数据库学生信息表增加了新列 `GPA`。源端学生信息表进行同步 Online DDL 操作，修改列名字段 `ID` 为 `StudentID`，同步到目标端会导致目标端学生信息表中新增的 `GPA` 列数据丢失。

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_75f07a1.png)

## 操作步骤

1. 在 **对象映射** 步骤中，迁移类型勾选 **增量同步，**点击 **同步 Online DDL** 开关。
2. 在弹出的窗口中，点击 **确认**。

# 将Palo作为目标端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS，将DTS已经支持的数据源迁移至Palo目标端中的场景。

## 2. 将Palo数据库作为DTS目标端的限制

* **不支持结构迁移**。

## 3. 将Palo数据库作为DTS目标端的前置条件

### 3.1 数据库账号权限要求

目标端：

| 数据库 | 全量增量迁移 |
| --- | --- |
| Palo数据库 | LOAD\_PRIV：对指定的库或表的导入权限 |

## 4. 使用Palo数据库作为DTS目标端

使用Palo数据库作为目标端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考最佳实践文档。
在任务配置参数和对象映射部分与其他数据源有些许不同。

### 4.1 任务配置参数

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_38add9b.png)

如上图所示。目前DTS的Palo目标端配置参数说明如下：

* **接入类型**：支持公网/BCC/BBC/DCC/VPC/专线接入。
* **数据类型**：固定选择Palo。
* **主机名/IP**：Palo数据库的访问IP（FE)。
* **端口**：Palo数据库的访问端口(FE mysql协议端口，一般为9030）。
* **HTTP IP**：Palo数据库的数据导入端口（DTS采用stream load方式导入数据，此处为BE的vip的underlay ip，可以联系Palo值班同学获取）。
* **HTTP 端口**：Palo数据库的数据导入端口（一般为8040）。
* **数据库**：Palo数据库中待迁移的数据库名。
* **账号**：Palo的数据库账号。
* **密码**：该数据库账号对应的密码。

### 4.2 对象映射

DTS提供库表名映射功能供用户选择，页面左侧会展示源端所有的库表信息，在页面左侧选择需要迁移的库表，库表信息将会被自动添加到页面右侧。DTS支持上下游库表名映射、列过滤黑白名单等功能。可以点击【编辑】，对每一个迁移对象配置映射和过滤规则。

完成对象映射配置后，点击【保存并预检查】，启动任务的前置检查。

## 5. DTS支持的Palo目标端数据类型

下表列出了使用DTS时支持的DTS数据类型与Palo目标端数据类型的默认映射。

有关如何查看源端映射的数据类型的信息，请参阅有关源端数据源的数据类型映射部分。

| DTS字段类型 | Palo数据类型 |
| --- | --- |
| DTS\_TYPE\_BOOLEAN | tinyint |
| DTS\_TYPE\_INT1 | tinyint |
| DTS\_TYPE\_INT2 | smallint |
| DTS\_TYPE\_INT4 | integer |
| DTS\_TYPE\_INT8 | bigint |
| DTS\_TYPE\_FLOAT | float |
| DTS\_TYPE\_DOUBLE | double |
| DTS\_TYPE\_DATE | date |
| DTS\_TYPE\_TIME | datetime |
| DTS\_TYPE\_DATETIME | datetime |
| DTS\_TYPE\_STRING | 如果定长 && 字节长度 <= 255 字节, 使用 CHAR. 如果字节长度 <= 65535 字节, 使用 VARCHAR |
| DTS\_TYPE\_NUMBER | 如果precision <= 27 && scale <= 9时：DECIMAL (p,s), 否则varchar(....) |

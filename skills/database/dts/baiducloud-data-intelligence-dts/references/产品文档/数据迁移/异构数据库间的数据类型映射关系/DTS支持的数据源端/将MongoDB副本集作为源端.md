# 将MongoDB副本集作为源端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称 DTS），将自建或者云上 MongoDB 副本集实例中的数据迁移至目标端为 MongoDB 实例的场景。

## 2. 将MongoDB副本集作为DTS源的前置条件

* 支持的版本为：**3.0、3.2、3.4、3.6、4.0、4.2**。
* 迁移账号必须**具有root权限的角色**。
* 只支持**实例级别**的迁移。
* **"\_id"** 数据类型限制：

  + 支持迁移的数据类型：Double、String、Binary data、ObjectId、Boolean、Date、32-bit integer、64-bit integer、Decimal128。
  + 不支持迁移的数据类型：Object、Array、Undefined、Null、Regular Expression、DBPointer、JavaScript、Symbol、JavaScript code with scope、Timestamp、Min key、Max key。
  + **以上限制只针对"\_id"字段，其他字段类型不受限制**。

## 3. 使用MongoDB副本集作为源端

使用MongoDB副本集数据库作为源端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考典型实践文档。

**任务配置**参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_4492d95.png)

* 接入类型：支持公网/BCC/BBC/DCC/VPC接入/专线接入/云数据库DocDB for MongoDB。
* 数据类型：MongoDB副本集。
* IP/端口：源端是自建实例时，可填写主从连接串/主节点/从节点，例如：127.0.0.1:27017,127.0.0.2:27018 / 127.0.0.1:27017 / 127.0.0.2:27018。
* 账号：填写实例中具有root权限的账号。
* 密码：填写账号对应的密码。
* 实例ID：接入类型是云数据库时，选择实例ID即可。

**对象映射**参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_25c19ac.png)

* MongoDB副本集支持结构迁移、全量迁移、增量同步。其中如果选择了结构迁移，就可以选择"账号迁移"，可以迁移的账号和角色会展示在列表中。
* 账号迁移限制：

  + 不支持迁移 admin.root 账号。
  + 只支持迁移鉴权方式为 SCRAM-SHA-1 / SCRAM-SHA-256 的账号。
  + 不支持迁移目标端已存在账号。

上述配置完成后，可开始预检查操作。

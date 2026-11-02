# 将MongoDB分片集作为源端

## 1. 适用场景

本文适用于使用百度智能云数据传输服务DTS（以下简称 DTS），将自建或者云上 MongoDB 分片集实例中的数据迁移至目标端为 MongoDB 实例的场景。

## 2. 将MongoDB分片集作为DTS源的前置条件

* 支持的版本为：**3.0、3.2、3.4、3.6、4.0、4.2**。
* 源端为自建MongoDB分片集时，Mongos和Shard必须配置相同的账号密码，账号必须具有root权限；源端为云数据库DocDB for MongoDB时，Mongos账号必须具有root权限，Shard使用默认账号shard\_readonly
* 只支持**实例级别**的迁移。
* **"\_id"** 数据类型限制：

  + 支持迁移的数据类型：Double、String、Binary data、ObjectId、Boolean、Date、32-bit integer、64-bit integer、Decimal128。
  + 不支持迁移的数据类型：Object、Array、Undefined、Null、Regular Expression、DBPointer、JavaScript、Symbol、JavaScript code with scope、Timestamp、Min key、Max key。
  + **以上限制只针对"\_id"字段，其他字段类型不受限制**。

## 3. 将MongoDB分片集作为DTS源的前置操作

1. 关闭源端 MongoDB 分片集的 Balancer，以防出现数据不一致的现象。

   登录源端实例的 **mongos** 节点，切换到 config 数据库

   Plain Text

   ```
   1 use config
   ```

   查看 Balancer 是否在执行

   Plain Text

   ```
   1 sh.isBalancerRunning()
   2 
   3 如果执行命令返回 true ，表示正在执行，需要等待 Balancer 执行完毕，再进行下一步
   ```

   关闭 Balancer

   Plain Text

   ```
   1 sh.stopBalancer()
   ```
2. 清理源端实例存在的孤儿文档。

   复制以下代码到本地文件，并将文件命名为 cleanupOrphaned.js

   Plain Text

   ```
   1function cleanupOrphaned(coll) {
   2  var nextKey = { };
   3  var result;
   4
   5  while ( nextKey != null ) {
   6    result = db.adminCommand( { cleanupOrphaned: coll, startingFromKey: nextKey } );
   7
   8    if (result.ok != 1)
   9       print("Unable to complete at this time: failure or timeout.")
   10
   11    printjson(result);
   12
   13    nextKey = result.stoppedAtKey;
   14  }
   15}
   16
   17var dbName = 'test'
   18db = db.getSiblingDB(dbName)
   19db.getCollectionNames().forEach(function(collName) {
   20    cleanupOrphaned(dbName + "." + collName);
   21});
   ```
3. 修改 cleanupOrphaned.js 脚本文件，将数据库名称 **test** 替换为需要清理孤儿文档的数据库名称。
   执行以下命令，依次清理每个 **shard** 节点存在的孤儿文档。

   Plain Text

   ```
   1 mongo --host <Shardhost> --port <Primaryport>  --authenticationDatabase <database> -u <username> -p <password> cleanupOrphaned.js
   ```

Plain Text

```
1* Shardhost：Shard 节点的 IP 地址。
2* Primaryport：Shard 节点中的 Primary 节点的服务端口。
3* database：鉴权数据库名，即数据库账号所属的数据库。
4* username：登录数据库的账号。
5* password：登录数据库的密码。
```

## 4. 使用MongoDB分片集作为源端

使用MongoDB分片集数据库作为源端，在任务创建、任务配置、前置检查、任务启动、任务暂停、任务终止的操作流程请参考典型实践文档。

**任务配置**参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_d1cc32c.png)

* 接入类型：支持公网/BCC/BBC/DCC/VPC接入/专线接入/云数据库DocDB for MongoDB。
* 数据类型：MongoDB分片集。
* Mongos：可填写单个或多个Mongos的url，多个url之间以逗号隔开。
* Shard：可填写单个或多个Shard的url，每个Shard连接方式支持主从连接串，主从之间以逗号隔开；不同Shard的url之间以分号隔开。
* 账号：填写实例中具有root权限的账号。
* 密码：填写账号对应的密码。
* 实例ID：接入类型是云数据库时，选择实例ID即可。

**对象映射**参数说明如下：

![image.png](https://bce.bdstatic.com/doc/bce-doc/DTS/image_25c19ac.png)

* MongoDB分片集支持结构迁移、全量迁移、增量同步。其中如果选择了结构迁移，就可以选择"账号迁移"，可以迁移的账号和角色会展示在列表中。
* 账号迁移限制：

  + 不支持迁移 admin.root 账号。
  + 只支持迁移鉴权方式为 SCRAM-SHA-1 / SCRAM-SHA-256 的账号。
  + 不支持迁移目标端已存在账号。

上述配置完成后，可开始预检查操作。

# 自建MongoDB分片集迁移至DocDB MongoDB

本文主要介绍自建 MongoDB（分片集架构） 中的各个 Shard 节点迁移至云数据库 DocDB MongoDB（副本集架构或分片集架构）。

## 前提条件

* 已创建目标端云数据库 DocDB MongoDB（副本集架构或分片集架构）。创建方式，请参见 [创建 MongoDB 实例](https://cloud.baidu.com/doc/MONGODB/s/Dkdr5gema)。
* 目标端云数据库 DocDB MongoDB 实例的存储空间须大于源端 MongoDB 实例占用的存储空间。

  > **说明**
  >
  > 若目标端 MongoDB 为分片集架构实例，例如自建数据库中有三个 Shard 节点，其中第二个 Shard 节点占用的存储空间最多（500GB），那么分片集架构实例中的每个 Shard 节点的存储空间均需要大于 500 GB。

## 限制说明

### 应用限制

| 类型 | 说明 |
| --- | --- |
| 源端限制 | * DTS 要求源数据库的 Oplog 日志至少保留 7 天以上，否则 DTS 可能因无法获取 Oplog 日志而导致任务失败，极端情况下甚至可能会导致数据不一致或丢失。 |
| 其他限制 | * 建议源库和目标库的 MongoDB 的版本保持一致，或者从低版本迁移至高版本以保障兼容性。当高版本迁移至低版本时，可能存在数据库兼容性或数据丢失的问题。 * 不支持迁移 admin、local 和 config 库中的数据。 * 不保留事务信息，即源库中的事务迁移到目标库时会转变为单条的记录。 * 执行数据迁移前需评估源库和目标库的性能，同时建议业务低峰期执行数据迁移。否则全量数据迁移时 DTS 占用源和目标库一定读写资源，可能会导致数据库的负载上升。 |

### 操作限制

迁移过程中请勿进行如下操作，否则会导致迁移任务失败。

* 在结构迁移和全量迁移阶段，请勿执行库或集合的结构变更，否则数据迁移任务会失败。
* 在迁移过程中，请勿向目标库中写入新的数据，否则将导致源和目标数据不一致。

## 迁移类型说明

* 结构迁移

将源端 MongoDB 中迁移对象的结构迁移到目标 MongoDB 实例中。

* 全量迁移

将源端 MongoDB 数据库迁移对象的存量数据，全部迁移到目标端 MongoDB 实例中。

* 增量迁移

将源端 MongoDB 数据库的增量更新数据到目标端 MongoDB 实例中。

## 数据库账号权限要求

| 数据库 | 结构迁移 | 全量迁移 | 增量迁移 |
| --- | --- | --- | --- |
| 源端 | ROOT | ROOT | ROOT |
| 目标端 | ROOT | ROOT | ROOT |

## 准备工作（MongoDB 分片集为源端）

1. 关闭自建 MongoDB 分片集的均衡器（Balancer），以防出现数据不一致。

   1. 登录源端实例的 **mongos**节点，切换到 config 数据库。

      ```
      1 use config
      ```
   2. 查看 Balancer 是否在执行。

      ```
      1 sh.isBalancerRunning()
      ```

      > **说明**
      >
      > 如果执行命令返回 true ，表示正在执行，需要等待 Balancer 执行完毕，再进行下一步
   3. 关闭 Balancer。

      ```
      1 sh.stopBalancer()
      ```
2. 清除自建 MongoDB 分片集中，因块迁移失败而产生的孤儿文档。

   > **说明**
   >
   > 如果未清除孤儿文档，将影响迁移性能，而且可能在迁移过程会遇到 `_id` 冲突的文档，导致迁移错误的数据。

   1. 复制以下代码到本地文件，并将文件命名为 cleanupOrphaned.js。

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
   2. 修改 cleanupOrphaned.js 脚本文件，将数据库名称 `test` 替换为需要清理的孤儿文档数据库名。

      > **说明**
      >
      > 如果您有多个数据库，您需要重复执行本步骤和步骤 c。
   3. 执行如下命令，清理 Shard 节点中指定数据库下所有集合的孤儿文档。

      > **注意**：
      >
      > 您需要重复执行本步骤，为每个 Shard 节点清理孤儿文档。

      ```
      1mongo --host <Shardhost> --port <Primaryport>  --authenticationDatabase <database> -u <username> -p <password> cleanupOrphaned.js
      ```

      > **说明**
      >
      > * ：Shard 节点的 IP 地址。
      > * ：Shard 节点中的 Primary 节点的服务端口。
      > * ：鉴权数据库名，即数据库账号所属的数据库。
      > * ：登录数据库的账号。
      > * ：登录数据库的密码。

## 操作步骤

1. 登录 [DTS 控制台](https://console.bce.baidu.com/dts/#/dts/migration/list)。
2. 点击 **创建数据传输任务** 进入 DTS 创建任务页面，详情参见 [购买流程](https://cloud.baidu.com/doc/DTS/s/clw60a6mz)。

   > **注意**：
   >
   > 当源端数据类型为 MongoDB 分片集时，分片数量需与集群 shard 数量保持一致，以保证传输性能。如集群 shard 数为 5，则该处值为 5。
3. 创建任务成功后自动返回任务列表页面，选择新创建的任务，点击 **更多操作—>配置任务**。
4. 在配置任务页面，配置源库及目标库信息。

   配置流程

   | 类别 | 配置 | 说明 |
   | --- | --- | --- |
   | 任务基本属性 | 任务名称 | DTS 会自动生成一个任务名称，建议配置具有业务意义的名称（无唯一性要求），便于后续识别。 |
   | 源端连接设置 | Mongos | 填写 Mongos url，多个 url 之间以英文逗号分隔。 |
   | Shard | 分片集 MongoDB 可支持同时设置主从 Shard 的 IP:端口，当源端/目标端主从切换等导致的原有主节点变动时，可顺序连接原从节点，提升传输链路高可用能力。 当您需要同时设置主从 Shard 的 IP:端口时，需按 Shard 维度分别填写主从 Shard 的 IP:端口，主从 Shard 地址之间以英文逗号分隔，不同 Shard 之间以分号分隔。 **注意**：Shard 的 url 总数必须与创建任务时填写的分片数量保持一致。 |
   | 账号 | 填写源端 Mongos 和 Shard 节点共用的，且有 root 权限的账号。 |
   | 密码 | 填入该数据库账号对应的密码。 |
   | 目标端连接设置 | 实例 ID | 选择目标 MongoDB 实例 ID。 |
   | 账号 | 填写有 root 权限的账号。 |
   | 密码 | 填入该数据库账号对应的密码。 |
5. 配置完成后，点击页面下方的 **授权白名单进入下一步**。

   如果您主动为 DocDB MongoDB 关联了自定义的 VPC 安全组规则，则需要您手动添加对应地区 DTS 服务的 IP 地址，以允许来自 DTS 服务器的访问，操作步骤请参见 [为您的 VPC 安全组添加 DTS 网段的放行规则](https://cloud.baidu.com/doc/DTS/s/cjwvxji7o#%E4%B8%BA%E6%82%A8%E7%9A%84-vpc-%E5%AE%89%E5%85%A8%E7%BB%84%E6%B7%BB%E5%8A%A0-dts-%E7%BD%91%E6%AE%B5%E7%9A%84%E6%94%BE%E8%A1%8C%E8%A7%84%E5%88%99)。

   > **警告：**
   >
   > DTS 自动添加或您手动添加 DTS 服务的 IP 地址段可能会存在安全风险，一旦使用本产品代表您已理解和确认其中可能存在的安全风险，并且需要您做好基本的安全防护，包括但不限于加强账号密码强度防范、限制各网段开放的端口号、内部各 API 使用鉴权方式通信、定期检查并限制不需要的网段等等。
6. 配置任务对象映射。

   | 配置 | 说明 |
   | --- | --- |
   | 迁移类型 | 根据需求及各引擎对迁移类型的支持情况，选择迁移类型。 |
   | 限制传输速度 | 根据实际情况，选择是否对全量迁移和增量同步任务进行更细粒度的限流策略设置（设置 **每秒迁移的行数** 和 **每秒迁移的数据量**），以缓解目标库压力。详情参见：[迁移限速](https://cloud.baidu.com/doc/DTS/s/Xlez0ok7o)。 |
   | 传输对象 | * 整个实例：将源端除系统库外的所有数据迁移到目标端。 * 手动选择：选择此选项时，在页面左侧选择需要迁移的对象，对象信息将会被自动添加到页面右侧。 * 模式匹配：详情参见：[模式匹配](https://cloud.baidu.com/doc/DTS/s/dl1es97ak#%E6%A8%A1%E5%BC%8F%E5%8C%B9%E9%85%8D)。 |
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

### 数据校验

详情参见 [配置数据校验](https://cloud.baidu.com/doc/DTS/s/jl443q585)。

### 业务切换

详情参见 [业务切换流程](https://cloud.baidu.com/doc/DTS/s/Rlz2cwt8c)。

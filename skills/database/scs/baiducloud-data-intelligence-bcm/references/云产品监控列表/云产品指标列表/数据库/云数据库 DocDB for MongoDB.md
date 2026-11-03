# 云数据库 DocDB for MongoDB

云数据库 DocDB for MongoDB包含2种监控对象类型，分别是：副本集实例（Replica）和分片集实例（Shard），各个类型包含的监控指标列表如下：

## 副本集实例（Replica）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| DeletedDocumentCount | 删除文档数 | 个/秒 | InstanceId、NodeId |  |
| InsertedDocumentCount | 插入文档数 | 个/秒 | InstanceId、NodeId |  |
| ReturnDocumentCount | 返回文档数 | 个/秒 | InstanceId、NodeId |  |
| UpdatedDocumentCount | 更新文档数 | 个/秒 | InstanceId、NodeId |  |
| CommandOPCount | command操作数 | 次/秒 | InstanceId、NodeId |  |
| DeleteOPCount | delete操作数 | 次/秒 | InstanceId、NodeId |  |
| GetMoreOPCount | getmore操作数 | 次/秒 | InstanceId、NodeId |  |
| InsertOPCount | insert操作数 | 次/秒 | InstanceId、NodeId |  |
| QueryOPCount | query操作数 | 次/秒 | InstanceId、NodeId |  |
| UpdateOPCount | update操作数 | 次/秒 | InstanceId、NodeId |  |
| CurrentConnections | 实例连接数 | 个 | InstanceId、NodeId |  |
| ReplicationLag | 主从延迟 | 秒 | InstanceId、NodeId |  |
| OplogReservedTime | oplog保存时长 | 秒 | InstanceId、NodeId |  |
| MongodbProcessAlive | Mongodb进程是否存在 | 个 | InstanceId、NodeId |  |
| OplogSize | oplog大小 | 字节 | InstanceId、NodeId |  |
| CpuUsage | CPU使用率 | % | InstanceId、NodeId |  |
| MemoryUsage | 内存使用率 | % | InstanceId、NodeId |  |
| DiskUsage | 磁盘空间使用率 | % | InstanceId、NodeId |  |
| DiskUsed | 磁盘空间使用量 | MB | InstanceId、NodeId |  |
| IOWait | IO等待时间占比 | % | InstanceId、NodeId |  |
| NetInBytes | 入口流量 | 字节/秒 | InstanceId、NodeId |  |
| NetOutBytes | 出口流量 | 字节/秒 | InstanceId、NodeId |  |
| DiskIOWaitTime | 进程等待IO时间 | 毫秒 | InstanceId、NodeId |  |
| OpenCursorsCount | cursor打开数量 | 个 | InstanceId、NodeId |  |
| TimedoutCursorsCount | 最近1分钟cursor超时数量 | 个 | InstanceId、NodeId |  |
| CurrentQueueReaders | 读锁等待队列长度 | 个 | InstanceId、NodeId |  |
| CurrentQueueWriters | 写锁等待队列长度 | 个 | InstanceId、NodeId |  |
| ActiveReaders | 使用全局读锁客户端数 | 个 | InstanceId、NodeId |  |
| ActiveWriters | 使用全局写锁客户端数 | 个 | InstanceId、NodeId |  |
| WriteConcurrentTransactionsOut | 写事务并发数 | 个 | InstanceId、NodeId |  |
| ReadConcurrentTransactionsOut | 读事务并发数 | 个 | InstanceId、NodeId |  |
| WriteConcurrentTransactionsAvailable | 可用的写事务并发数 | 个 | InstanceId、NodeId |  |
| ReadConcurrentTransactionsAvailable | 可用的读事务并发数 | 个 | InstanceId、NodeId |  |
| WiredTigerCacheUsage | WiredTiger Cache使用率 | % | InstanceId、NodeId |  |
| WiredTigerDirtyCachePercent | WiredTiger Cache脏页率 | % | InstanceId、NodeId |  |
| CollscanCount | 最近1分钟profile记录的Collscan数 | 个 | InstanceId、NodeId |  |
| SlowOpCount | 最近1分钟profile的记录数 | 个 | InstanceId、NodeId |  |
| AverageSlowOpMillis | 最近1分钟profile记录的平均时间 | 毫秒 | InstanceId、NodeId |  |
| ConnectionsUsage | 实例连接使用率 | % | InstanceId、NodeId |  |
| ScannedKeys | 扫描索引数 | 个/秒 | InstanceId、NodeId |  |
| ScannedDocs | 扫描文档数 | 个/秒 | InstanceId、NodeId |  |
| ScanAndOrder | 无法使用索引排序请求数 | 次/秒 | InstanceId、NodeId |  |
| WriteConflict | 写冲突次数 | 次/秒 | InstanceId、NodeId |  |

## 分片集实例（Shard）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| DeletedDocumentCount | 删除文档数 | 个/秒 | InstanceId、NodeId |  |
| InsertedDocumentCount | 插入文档数 | 个/秒 | InstanceId、NodeId |  |
| ReturnDocumentCount | 返回文档数 | 个/秒 | InstanceId、NodeId |  |
| UpdatedDocumentCount | 更新文档数 | 个/秒 | InstanceId、NodeId |  |
| CommandOPCount | command操作数 | 次/秒 | InstanceId、NodeId |  |
| DeleteOPCount | delete操作数 | 次/秒 | InstanceId、NodeId |  |
| GetMoreOPCount | getmore操作数 | 次/秒 | InstanceId、NodeId |  |
| InsertOPCount | insert操作数 | 次/秒 | InstanceId、NodeId |  |
| QueryOPCount | query操作数 | 次/秒 | InstanceId、NodeId |  |
| UpdateOPCount | update操作数 | 次/秒 | InstanceId、NodeId |  |
| CurrentConnections | 实例连接数 | 个 | InstanceId、NodeId |  |
| ReplicationLag | 主从延迟 | 秒 | InstanceId、NodeId |  |
| OplogReservedTime | oplog保存时长 | 秒 | InstanceId、NodeId |  |
| MongodbProcessAlive | Mongodb进程是否存在 | 个 | InstanceId、NodeId |  |
| OplogSize | oplog大小 | 字节 | InstanceId、NodeId |  |
| CpuUsage | CPU使用率 | % | InstanceId、NodeId |  |
| MemoryUsage | 内存使用率 | % | InstanceId、NodeId |  |
| DiskUsage | 磁盘空间使用率 | % | InstanceId、NodeId |  |
| DiskUsed | 磁盘空间使用量 | MB | InstanceId、NodeId |  |
| IOWait | IO等待时间占比 | % | InstanceId、NodeId |  |
| NetInBytes | 入口流量 | 字节/秒 | InstanceId、NodeId |  |
| NetOutBytes | 出口流量 | 字节/秒 | InstanceId、NodeId |  |
| DiskIOWaitTime | 进程等待IO时间 | 毫秒 | InstanceId、NodeId |  |
| OpenCursorsCount | cursor打开数量 | 个 | InstanceId、NodeId |  |
| TimedoutCursorsCount | 最近1分钟cursor超时数量 | 个 | InstanceId、NodeId |  |
| CurrentQueueReaders | 读锁等待队列长度 | 个 | InstanceId、NodeId |  |
| CurrentQueueWriters | 写锁等待队列长度 | 个 | InstanceId、NodeId |  |
| ActiveReaders | 使用全局读锁客户端数 | 个 | InstanceId、NodeId |  |
| ActiveWriters | 使用全局写锁客户端数 | 个 | InstanceId、NodeId |  |
| WriteConcurrentTransactionsOut | 写事务并发数 | 个 | InstanceId、NodeId |  |
| ReadConcurrentTransactionsOut | 读事务并发数 | 个 | InstanceId、NodeId |  |
| WriteConcurrentTransactionsAvailable | 可用的写事务并发数 | 个 | InstanceId、NodeId |  |
| ReadConcurrentTransactionsAvailable | 可用的读事务并发数 | 个 | InstanceId、NodeId |  |
| WiredTigerCacheUsage | WiredTiger Cache使用率 | % | InstanceId、NodeId |  |
| WiredTigerDirtyCachePercent | WiredTiger Cache脏页率 | % | InstanceId、NodeId |  |
| CollscanCount | 最近1分钟profile记录的Collscan数 | 个 | InstanceId、NodeId |  |
| SlowOpCount | 最近1分钟profile的记录数 | 个 | InstanceId、NodeId |  |
| AverageSlowOpMillis | 最近1分钟profile记录的平均时间 | 毫秒 | InstanceId、NodeId |  |
| ConnectionsUsage | 实例连接使用率 | % | InstanceId、NodeId |  |
| ScannedKeys | 扫描索引数 | 个/秒 | InstanceId、NodeId |  |
| ScannedDocs | 扫描文档数 | 个/秒 | InstanceId、NodeId |  |
| ScanAndOrder | 无法使用索引排序请求数 | 次/秒 | InstanceId、NodeId |  |
| WriteConflict | 写冲突次数 | 次/秒 | InstanceId、NodeId |  |

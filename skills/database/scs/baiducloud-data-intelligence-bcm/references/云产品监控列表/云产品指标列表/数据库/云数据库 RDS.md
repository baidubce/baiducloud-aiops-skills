# 云数据库 RDS

云数据库RDS包含5种监控对象类型，分别是：MySQL-主（MysqlMaster）、MySQL-只读（MysqlReadOnly）、PostgreSQL（PG）、SQL Server（SqlServer）、MySQL-代理（MysqlProxy）各个类型包含的监控指标列表如下：

## MySQL-主（MysqlMaster）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| BinlogCacheUsePerSecond | 使用二进制缓存事物数 | 次/秒 | InstanceId |  |
| BytesReceivedPerSecond | mysql字节接受数 | Byte/秒 | InstanceId |  |
| BytesSentPerSecond | mysql字节发送数 | Byte/秒 | InstanceId |  |
| ComAlterTablePerSecond | 操作表数 | 次/秒 | InstanceId |  |
| ConnectionUsagePercent | 连接数利用率 | % | InstanceId |  |
| CPUUsagePercent | CPU使用率 | % | InstanceId |  |
| CreatedTmpDiskTablesPerSecond | 磁盘临时表数量 | 个/秒 | InstanceId |  |
| CreatedTmpFilesCountPerSecond | 临时文件数量 | 个/秒 | InstanceId |  |
| CreatedTmpTablesPerSecond | 临时表数量 | 个/秒 | InstanceId |  |
| DataDiskIops | 访问 | 次/秒 | InstanceId |  |
| DataDiskRead | 磁盘读取带宽 | KB/秒 | InstanceId |  |
| DataDiskWrite | 磁盘写入带宽 | KB/秒 | InstanceId |  |
| DeleteCountPerSecond | 每秒删除数 | 次/秒 | InstanceId |  |
| DiskUsagePercent | 磁盘利用率 | % | InstanceId |  |
| FollowerSecondsBehindLeader | 热活组主从延迟 | 秒 | InstanceId |  |
| HandlerCommitPerSecond | 内部提交数 | 次/秒 | InstanceId |  |
| HandlerReadRndNextPerSecond | 读下一行请求数 | 次/秒 | InstanceId |  |
| HandlerRollbackPerSecond | 内部回滚数 | 次/秒 | InstanceId |  |
| InnodbBufferPoolPagesFree | InnoDB空页数 | 个 | InstanceId |  |
| InnodbBufferPoolPagesRequestsPerSecond | InnoDB逻辑读 | 次/秒 | InstanceId |  |
| InnodbBufferPoolPagesTotal | InnoDB总页数 | 个 | InstanceId |  |
| InnodbBufferPoolReadsPerSecond | InnoDB物理读 | 次/秒 | InstanceId |  |
| InnodbCacheHitPercent | innodb缓存命中率 | % | InstanceId |  |
| InnodbCacheHitPercentPerSecond | InnoDBbuff命中率 | %/秒 | InstanceId |  |
| InnodbCacheUsePercent | innodb缓存使用率 | % | InstanceId |  |
| InnodbDataFsyncsPerSecond | Innodb引擎每秒调用fsync函数次数 | 次/秒 | InstanceId |  |
| InnodbDataReadPerSecond | InnoDB读取量 | Byte/秒 | InstanceId |  |
| InnodbDataReadsPerSecond | InnoDB总读取量 | 次/秒 | InstanceId |  |
| InnodbDataWritesPerSecond | InnoDB总写入量 | 次/秒 | InstanceId |  |
| InnodbDataWrittenPerSecond | InnoDB写入量 | Byte/秒 | InstanceId |  |
| InnodbLogWaits | InnoDB日志缓存区需等待刷新次数 | 次 | InstanceId |  |
| InnodbLogWaitsPercent | InnoDB等待刷新率 | % | InstanceId |  |
| InnodbLogWriteRequestsPerSecond | InnoDBredolog写入请求数 | 次/秒 | InstanceId |  |
| InnodbLogWritesPerSecond | InnoDBredolog写入数 | 次/秒 | InstanceId |  |
| InnodbNumOpenFiles | 当前Innodb打开表的数量 | 个 | InstanceId |  |
| InnodbRowLockTimeAvg | InnoDB平均获取行锁时间 | 毫秒 | InstanceId |  |
| InnodbRowLockWaitsPerSecond | InnoDB等待行锁次数 | 次/秒 | InstanceId |  |
| InnodbRowsDeletedPerSecond | InnoDB行删除量 | 次/秒 | InstanceId |  |
| InnodbRowsInsertedPerSecond | InnoDB行插入量 | 次/秒 | InstanceId |  |
| InnodbRowsReadPerSecond | InnoDB行读取量 | 次/秒 | InstanceId |  |
| InnodbRowsUpdatedPerSecond | InnoDB行更新量 | 次/秒 | InstanceId |  |
| InsertCountPerSecond | 每秒插入数 | 次/秒 | InstanceId |  |
| KeyBlocksUnused | 缓存未使用数 | 个 | InstanceId |  |
| KeyBlocksUsed | 缓存使用数 | 个 | InstanceId |  |
| KeyCacheBlockCount | 缓存块数 | 个 | InstanceId |  |
| KeyCacheBlockUsed | 缓存使用块数 | 个 | InstanceId |  |
| KeyCacheHitPercent | 缓存命中率 | % | InstanceId |  |
| KeyCacheUsePercent | 缓存使用率 | % | InstanceId |  |
| KeyReadRequestsPerSecond | 读取缓存请求数 | 个/秒 | InstanceId |  |
| KeyReadsPerSecond | 读取磁盘数 | 个/秒 | InstanceId |  |
| KeyWriteRequestsPerSecond | 写入缓存请求数 | 个/秒 | InstanceId |  |
| KeyWritesPerSecond | 写入磁盘数 | 个/秒 | InstanceId |  |
| LeaderFollowerSyncStatus | 热活组主从同步状态 | 1：正常同步中, 0：同步中断 | InstanceId |  |
| LogCapacity | 日志占用空间 | MB | InstanceId |  |
| MasterSlaveSyncDistance | 主备延迟距离 | MB | InstanceId |  |
| MaxConnectionsCount | 最大连接数 | 个 | InstanceId |  |
| MemUsagePercent | 内存使用率 | % | InstanceId |  |
| MemUsedSize | 内存使用空间 | MB | InstanceId |  |
| MysqlDataSize | 磁盘使用空间 | MB | InstanceId |  |
| MysqlDiskUsedSize | 磁盘占用空间 | MB | InstanceId |  |
| MysqlIops | 实例读写次数 | 次/秒 | InstanceId |  |
| MysqlIsAlived | mysql存活 | 状态值 | InstanceId |  |
| MysqlSlowQueriesPt | 慢查询次数 | 次/秒 | InstanceId |  |
| NetworkInBytes | 网络输入流量 | Byte/秒 | InstanceId |  |
| NetworkOutBytes | 网络输出流量 | Byte/秒 | InstanceId |  |
| OpenedTablesCount | 已经打开的表数 | 个 | InstanceId |  |
| OpenFilesPerSecond | 打开文件数 | 次/秒 | InstanceId |  |
| QcacheFreeBlocks | qcache未使用数 | 个 | InstanceId |  |
| QcacheFreeMemory | qcache可用内存 | KB | InstanceId |  |
| QcacheHitPercent | 查询缓存命中率 | % | InstanceId |  |
| QcacheHitsPerSecond | qcache命中数 | 个/秒 | InstanceId |  |
| QcacheInsertsPerSecond | qchche插入数 | 个/秒 | InstanceId |  |
| QcacheLowmemPrunesPerSecond | qcache删除数 | 个/秒 | InstanceId |  |
| QcacheNotCached | qchche未缓存数 | 万个 | InstanceId |  |
| QcacheQueriesInCachePerSecond | qcache注册数 | 个/秒 | InstanceId |  |
| QcacheTotalBlocks | qchche总块数 | 个 | InstanceId |  |
| QcacheUsePercent | 查询缓存使用率 | % | InstanceId |  |
| QueryCountPerSecond | 每秒执行操作数 | 次/秒 | InstanceId |  |
| ReadOpCountPerSecond | 查询请求次数 | 次/秒 | InstanceId |  |
| ReplaceCountPerSecond | 每秒覆盖数 | 次/秒 | InstanceId |  |
| SecondsBehindMaster | 主从延时 | 秒 | InstanceId |  |
| SelectCountPerSecond | 每秒查询数 | 次/秒 | InstanceId |  |
| SelectScanCount | 全表扫描数 | 次/秒 | InstanceId |  |
| SlaveIORunning | IO线程状态 | 状态值 | InstanceId |  |
| SlaveSQLRunning | SQL线程状态 | 状态值 | InstanceId |  |
| TableLocksImmediatePerSecond | 表锁立即生效数 | 个/秒 | InstanceId |  |
| TableLocksWaitedPerSecond | 等待表锁次数 | 次/秒 | InstanceId |  |
| ThreadConnectedCount | 当前打开连接数 | 个 | InstanceId |  |
| ThreadRunningCount | 运行的线程数 | 个 | InstanceId |  |
| ThreadsCacheHitsPercent | 线程命中率 | % | InstanceId |  |
| ThreadsCacheHitsPercentPerSecond | 线程命中率每秒 | %/秒 | InstanceId |  |
| ThreadsCreatedCount | 已创建的线程数 | 个 | InstanceId |  |
| TPS | 每秒执行事务数 | 次/秒 | InstanceId |  |
| TPS\_ALL | 每秒事务数（含隐式提交） | 次/秒 | InstanceId |  |
| TransactionCountPerSecond | 每秒提交数 | 次/秒 | InstanceId |  |
| TransactionMaxActiveSeconds | 最大事务执行时间 | 秒 | InstanceId |  |
| TransactionRollbackCountPerSecond | 每秒回滚数 | 次/秒 | InstanceId |  |
| UpdateCountPerSecond | 每秒更新数 | 次/秒 | InstanceId |  |
| VMDiskUsagePercent | 系统磁盘使用率 | % | InstanceId |  |
| WebInBytes | 外网网络输入流量 | Byte/秒 | InstanceId |  |
| WebOutBytes | 外网网络输出流量 | Byte/秒 | InstanceId |  |
| WriteOpCountPerSecond | 更新请求次数 | 次/秒 | InstanceId |  |

## MySQL-只读（MysqlReadOnly）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| BinlogCacheUsePerSecond | 使用二进制缓存事物数 | 次/秒 | InstanceId |  |
| BytesReceivedPerSecond | mysql字节接受数 | Byte/秒 | InstanceId |  |
| BytesSentPerSecond | mysql字节发送数 | Byte/秒 | InstanceId |  |
| ComAlterTablePerSecond | 操作表数 | 次/秒 | InstanceId |  |
| ConnectionUsagePercent | 连接数利用率 | % | InstanceId |  |
| CPUUsagePercent | CPU使用率 | % | InstanceId |  |
| CreatedTmpDiskTablesPerSecond | 磁盘临时表数量 | 个/秒 | InstanceId |  |
| CreatedTmpFilesCountPerSecond | 临时文件数量 | 个/秒 | InstanceId |  |
| CreatedTmpTablesPerSecond | 临时表数量 | 个/秒 | InstanceId |  |
| DataDiskIops | 访问 | 次/秒 | InstanceId |  |
| DataDiskRead | 磁盘读取带宽 | KB/秒 | InstanceId |  |
| DataDiskWrite | 磁盘写入带宽 | KB/秒 | InstanceId |  |
| DeleteCountPerSecond | 每秒删除数 | 次/秒 | InstanceId |  |
| DiskUsagePercent | 磁盘利用率 | % | InstanceId |  |
| FollowerSecondsBehindLeader | 热活组主从延迟 | 秒 | InstanceId |  |
| HandlerCommitPerSecond | 内部提交数 | 次/秒 | InstanceId |  |
| HandlerReadRndNextPerSecond | 读下一行请求数 | 次/秒 | InstanceId |  |
| HandlerRollbackPerSecond | 内部回滚数 | 次/秒 | InstanceId |  |
| InnodbBufferPoolPagesFree | InnoDB空页数 | 个 | InstanceId |  |
| InnodbBufferPoolPagesRequestsPerSecond | InnoDB逻辑读 | 次/秒 | InstanceId |  |
| InnodbBufferPoolPagesTotal | InnoDB总页数 | 个 | InstanceId |  |
| InnodbBufferPoolReadsPerSecond | InnoDB物理读 | 次/秒 | InstanceId |  |
| InnodbCacheHitPercent | innodb缓存命中率 | % | InstanceId |  |
| InnodbCacheHitPercentPerSecond | InnoDBbuff命中率 | %/秒 | InstanceId |  |
| InnodbCacheUsePercent | innodb缓存使用率 | % | InstanceId |  |
| InnodbDataFsyncsPerSecond | Innodb引擎每秒调用fsync函数次数 | 次/秒 | InstanceId |  |
| InnodbDataReadPerSecond | InnoDB读取量 | Byte/秒 | InstanceId |  |
| InnodbDataReadsPerSecond | InnoDB总读取量 | 次/秒 | InstanceId |  |
| InnodbDataWritesPerSecond | InnoDB总写入量 | 次/秒 | InstanceId |  |
| InnodbDataWrittenPerSecond | InnoDB写入量 | Byte/秒 | InstanceId |  |
| InnodbLogWaits | InnoDB日志缓存区需等待刷新次数 | 次 | InstanceId |  |
| InnodbLogWaitsPercent | InnoDB等待刷新率 | % | InstanceId |  |
| InnodbLogWriteRequestsPerSecond | InnoDBredolog写入请求数 | 次/秒 | InstanceId |  |
| InnodbLogWritesPerSecond | InnoDBredolog写入数 | 次/秒 | InstanceId |  |
| InnodbNumOpenFiles | 当前Innodb打开表的数量 | 个 | InstanceId |  |
| InnodbRowLockTimeAvg | InnoDB平均获取行锁时间 | 毫秒 | InstanceId |  |
| InnodbRowLockWaitsPerSecond | InnoDB等待行锁次数 | 次/秒 | InstanceId |  |
| InnodbRowsDeletedPerSecond | InnoDB行删除量 | 次/秒 | InstanceId |  |
| InnodbRowsInsertedPerSecond | InnoDB行插入量 | 次/秒 | InstanceId |  |
| InnodbRowsReadPerSecond | InnoDB行读取量 | 次/秒 | InstanceId |  |
| InnodbRowsUpdatedPerSecond | InnoDB行更新量 | 次/秒 | InstanceId |  |
| InsertCountPerSecond | 每秒插入数 | 次/秒 | InstanceId |  |
| KeyBlocksUnused | 缓存未使用数 | 个 | InstanceId |  |
| KeyBlocksUsed | 缓存使用数 | 个 | InstanceId |  |
| KeyCacheBlockCount | 缓存块数 | 个 | InstanceId |  |
| KeyCacheBlockUsed | 缓存使用块数 | 个 | InstanceId |  |
| KeyCacheHitPercent | 缓存命中率 | % | InstanceId |  |
| KeyCacheUsePercent | 缓存使用率 | % | InstanceId |  |
| KeyReadRequestsPerSecond | 读取缓存请求数 | 个/秒 | InstanceId |  |
| KeyReadsPerSecond | 读取磁盘数 | 个/秒 | InstanceId |  |
| KeyWriteRequestsPerSecond | 写入缓存请求数 | 个/秒 | InstanceId |  |
| KeyWritesPerSecond | 写入磁盘数 | 个/秒 | InstanceId |  |
| LeaderFollowerSyncStatus | 热活组主从同步状态 | 1：正常同步中, 0：同步中断 | InstanceId |  |
| LogCapacity | 日志占用空间 | MB | InstanceId |  |
| MasterSlaveSyncDistance | 主备延迟距离 | MB | InstanceId |  |
| MaxConnectionsCount | 最大连接数 | 个 | InstanceId |  |
| MemUsagePercent | 内存使用率 | % | InstanceId |  |
| MemUsedSize | 内存使用空间 | MB | InstanceId |  |
| MysqlDataSize | 磁盘使用空间 | MB | InstanceId |  |
| MysqlDiskUsedSize | 磁盘占用空间 | MB | InstanceId |  |
| MysqlIops | 实例读写次数 | 次/秒 | InstanceId |  |
| MysqlIsAlived | mysql存活 | 状态值 | InstanceId |  |
| MysqlSlowQueriesPt | 慢查询次数 | 次/秒 | InstanceId |  |
| NetworkInBytes | 网络输入流量 | Byte/秒 | InstanceId |  |
| NetworkOutBytes | 网络输出流量 | Byte/秒 | InstanceId |  |
| OpenedTablesCount | 已经打开的表数 | 个 | InstanceId |  |
| OpenFilesPerSecond | 打开文件数 | 次/秒 | InstanceId |  |
| QcacheFreeBlocks | qcache未使用数 | 个 | InstanceId |  |
| QcacheFreeMemory | qcache可用内存 | KB | InstanceId |  |
| QcacheHitPercent | 查询缓存命中率 | % | InstanceId |  |
| QcacheHitsPerSecond | qcache命中数 | 个/秒 | InstanceId |  |
| QcacheInsertsPerSecond | qchche插入数 | 个/秒 | InstanceId |  |
| QcacheLowmemPrunesPerSecond | qcache删除数 | 个/秒 | InstanceId |  |
| QcacheNotCached | qchche未缓存数 | 万个 | InstanceId |  |
| QcacheQueriesInCachePerSecond | qcache注册数 | 个/秒 | InstanceId |  |
| QcacheTotalBlocks | qchche总块数 | 个 | InstanceId |  |
| QcacheUsePercent | 查询缓存使用率 | % | InstanceId |  |
| QueryCountPerSecond | 每秒执行操作数 | 次/秒 | InstanceId |  |
| ReadOpCountPerSecond | 查询请求次数 | 次/秒 | InstanceId |  |
| ReplaceCountPerSecond | 每秒覆盖数 | 次/秒 | InstanceId |  |
| SecondsBehindMaster | 主从延时 | 秒 | InstanceId |  |
| SelectCountPerSecond | 每秒查询数 | 次/秒 | InstanceId |  |
| SelectScanCount | 全表扫描数 | 次/秒 | InstanceId |  |
| SlaveIORunning | IO线程状态 | 状态值 | InstanceId |  |
| SlaveSQLRunning | SQL线程状态 | 状态值 | InstanceId |  |
| TableLocksImmediatePerSecond | 表锁立即生效数 | 个/秒 | InstanceId |  |
| TableLocksWaitedPerSecond | 等待表锁次数 | 次/秒 | InstanceId |  |
| ThreadConnectedCount | 当前打开连接数 | 个 | InstanceId |  |
| ThreadRunningCount | 运行的线程数 | 个 | InstanceId |  |
| ThreadsCacheHitsPercent | 线程命中率 | % | InstanceId |  |
| ThreadsCacheHitsPercentPerSecond | 线程命中率每秒 | %/秒 | InstanceId |  |
| ThreadsCreatedCount | 已创建的线程数 | 个 | InstanceId |  |
| TPS | 每秒执行事务数 | 次/秒 | InstanceId |  |
| TPS\_ALL | 每秒事务数（含隐式提交） | 次/秒 | InstanceId |  |
| TransactionCountPerSecond | 每秒提交数 | 次/秒 | InstanceId |  |
| TransactionMaxActiveSeconds | 最大事务执行时间 | 秒 | InstanceId |  |
| TransactionRollbackCountPerSecond | 每秒回滚数 | 次/秒 | InstanceId |  |
| UpdateCountPerSecond | 每秒更新数 | 次/秒 | InstanceId |  |
| VMDiskUsagePercent | 系统磁盘使用率 | % | InstanceId |  |
| WebInBytes | 外网网络输入流量 | Byte/秒 | InstanceId |  |
| WebOutBytes | 外网网络输出流量 | Byte/秒 | InstanceId |  |
| WriteOpCountPerSecond | 更新请求次数 | 次/秒 | InstanceId |  |

## PostgreSQL（PG）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| AvgSqlRuntimeMs | 平均执行时延 | ms | InstanceId |  |
| BlksHitPercent | 缓冲区缓存命中率 | % | InstanceId |  |
| CPUUsagePercent | CPU占用率 | % | InstanceId |  |
| DiskUsagePercent | 磁盘利用率 | % | InstanceId |  |
| MaxSqlRuntimeMs | 最长TOP10执行时延 | ms | InstanceId |  |
| MemUsagePercent | 内存使用率 | % | InstanceId |  |
| MinSqlRuntimeMs | 最短TOP10执行时延 | ms | InstanceId |  |
| NetworkInBytes | 网络输入流量 | B | InstanceId |  |
| NetworkOutBytes | 网络输出流量 | B | InstanceId |  |
| OtherCalls | 其他请求数 | 次/秒 | InstanceId |  |
| QueryCountPerSecond | 每秒执行操作数 | 次/秒 | InstanceId |  |
| ReadOpCountPerSecond | 查询请求次数 | 次/秒 | InstanceId |  |
| ReadWriteCalls | 读写请求数 | 次/秒 | InstanceId |  |
| RemainingXid | 剩余XID数量 | 个 | InstanceId |  |
| ReplicationDelayTime | 从库wal回放回访延迟 | 秒 | InstanceId |  |
| SlaveXlogDiff | 只读库日志接收LSN与回放LSN差异 | Byte | InstanceId |  |
| SlowQueries | 慢查询数量 | 行/秒 | InstanceId |  |
| ThreadConnectedCount | 当前打开连接数 | 个 | InstanceId |  |
| ThreadRunningCount | 运行的线程数 | 个 | InstanceId |  |
| TransactionMaxActiveSeconds | 最大事务执行时间 | 秒 | InstanceId |  |
| WebInBytes | 外网网络输入流量 | B | InstanceId |  |
| WebOutBytes | 外网网络输出流量 | B | InstanceId |  |
| WriteOpCountPerSecond | 更新请求次数 | 次/秒 | InstanceId |  |
| XlogDiff | 主库日志发送与备库回放差异 | Byte | InstanceId |  |
| CPUWaitIO | 磁盘I/O等待率 | % | InstanceId |  |
| DBInstanceDown | 实例宕机 | 状态值 | InstanceId |  |
| BackupFailed | 备份失败 | 状态值 | InstanceId |  |
| PostgresqlIsAlived | PG存活 | 状态值 | InstanceId |  |
| WaitSession | 等待事件数 | 个 | InstanceId |  |
| LockCount | PG锁数量 | 个 | InstanceId |  |

## SQL Server（SqlServer）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU占用率 | % | InstanceId |  |
| DiskUsagePercent | 磁盘利用率 | % | InstanceId |  |
| MemUsagePercent | 内存使用率 | % | InstanceId |  |
| NetworkInBytes | 网络输入流量 | B | InstanceId |  |
| NetworkOutBytes | 网络输出流量 | B | InstanceId |  |
| QueryCountPerSecond | 每秒执行操作数 | 次/秒 | InstanceId |  |
| ReadOpCountPerSecond | 查询请求次数 | 次/秒 | InstanceId |  |
| ThreadConnectedCount | 当前打开连接数 | 个 | InstanceId |  |
| ThreadRunningCount | 运行的线程数 | 个 | InstanceId |  |
| TransactionMaxActiveSeconds | 最大事务执行时间 | 秒 | InstanceId |  |
| WebInBytes | 外网网络输入流量 | B | InstanceId |  |
| WebOutBytes | 外网网络输出流量 | B | InstanceId |  |
| WriteOpCountPerSecond | 更新请求次数 | 次/秒 | InstanceId |  |

## MySQL-代理（MysqlProxy）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPU\_IDLE | cpu空闲时间 | % | InstanceId |  |
| CPU\_SERVER\_LOADAVG\_1 | 最近一分钟CPU负载 | % | InstanceId |  |
| CPU\_WAIT\_IO | CPU等待io时间 | % | InstanceId |  |
| DISK\_ROOT\_FREE | ROOT盘空闲空间 | MB | InstanceId |  |
| DISK\_ROOT\_USAGE\_PERCENT | ROOT盘空间使用率 | % | InstanceId |  |
| DISK\_ROOT\_INODE\_FREE | ROOT盘INODE节点空闲数 | 个/秒 | InstanceId |  |
| DISK\_ROOT\_INODE\_USED\_PERCENT | ROOT盘INODE节点使用率 | % | InstanceId |  |
| MEM\_FREE | 内存空闲空间 | KB | InstanceId |  |
| MEM\_USED\_PERCENT | 内存使用率 | % | InstanceId |  |
| NET\_TOTAL\_IN\_BITPS | 虚机eth0接口入网流量 | Byte/s | InstanceId |  |
| NET\_TOTAL\_OUT\_BITPS | 虚机eth0接口出网流量 | Byte/s | InstanceId |  |
| cpu\_usage | CPU使用率 | % | InstanceId |  |

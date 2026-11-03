# 专属集群 DDC

专属集群 DDC 包含实例监控（Instance），OceanBase集群（OBCluster），OceanBase租户（OBTenant），OceanBase主机监控（OBServer）4种监控对象类型，实例监控包含的监控指标列表如下：

## 实例监控（Instance）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| BinlogCacheUsePerSecond | 使用二进制缓存事物数 | 次/秒 | InstanceId,InstanceType |  |
| BytesReceivedPerSecond | mysql字节接受数 | kb/秒 | InstanceId,InstanceType |  |
| BytesSentPerSecond | mysql字节发送数 | 次/秒 | InstanceId,InstanceType |  |
| ComAlterTablePerSecond | 操作表数 | 次/秒 | InstanceId,InstanceType |  |
| ConnectionUsagePercent | 连接数利用率 | % | InstanceId,InstanceType |  |
| CPUUsagePercent | CPU占用率 | % | InstanceId,InstanceType |  |
| CPUUsagePercentReal | CPU真实使用率 | % | InstanceId,InstanceType |  |
| CreatedTmpDiskTablesPerSecond | 磁盘临时表数量 | 个/秒 | InstanceId,InstanceType |  |
| CreatedTmpFilesCountPerSecond | 临时文件数量 | 个 | InstanceId,InstanceType |  |
| CreatedTmpTablesPerSecond | 临时表数量 | 个/秒 | InstanceId,InstanceType |  |
| Data3DiskIops | 磁盘3读写次数 | 次 | InstanceId,InstanceType |  |
| Data3DiskRead | 磁盘3读取带宽 | KB/秒 | InstanceId,InstanceType |  |
| Data3DiskWrite | 磁盘3写入带宽 | KB/秒 | InstanceId,InstanceType |  |
| DataDiskIOPS | 磁盘读写次数 | 次 | InstanceId,InstanceType |  |
| DeleteCountPerSecond | 每秒删除数 | 次/秒 | InstanceId,InstanceType |  |
| Disk3MaxIoUtil | 磁盘3最大io使用率 | % | InstanceId,InstanceType |  |
| DiskUsagePercent | 磁盘利用率 | % | InstanceId,InstanceType |  |
| HandlerCommitPerSecond | 内部提交数 | 次/秒 | InstanceId,InstanceType |  |
| HandlerReadRndNextPerSecond | 读下一行请求数 | 次/秒 | InstanceId,InstanceType |  |
| HandlerRollbackPerSecond | 内部回滚数 | 次/秒 | InstanceId,InstanceType |  |
| InnodbBufferPoolPagesFree | InnoDB空页数 | 个 | InstanceId,InstanceType |  |
| InnodbBufferPoolPagesRequestsPerSecond | InnoDB逻辑读 | 次/秒 | InstanceId,InstanceType |  |
| InnodbBufferPoolPagesTotal | InnoDB总页数 | 个 | InstanceId,InstanceType |  |
| InnodbBufferPoolReadsPerSecond | InnoDB物理读 | 次/秒 | InstanceId,InstanceType |  |
| InnodbCacheHitPercent | innodb缓存命中率 | % | InstanceId,InstanceType |  |
| InnodbCacheHitPercentPerSecond | InnoDBbuff命中率 | %/秒 | InstanceId,InstanceType |  |
| InnodbCacheUsePercent | innodb缓存使用率 | % | InstanceId,InstanceType |  |
| InnodbDataFsyncsPerSecond | Innodb引擎每秒调用fsync函数次数 | 次/秒 | InstanceId,InstanceType |  |
| InnodbDataReadPerSecond | InnoDB读取量 | Byte/秒 | InstanceId,InstanceType |  |
| InnodbDataReadsPerSecond | InnoDB总读取量 | 次/秒 | InstanceId,InstanceType |  |
| InnodbDataWritesPerSecond | InnoDB总写入量 | 次/秒 | InstanceId,InstanceType |  |
| InnodbDataWrittenPerSecond | InnoDB写入量 | Byte/秒 | InstanceId,InstanceType |  |
| InnodbLogWaits | InnoDB日志缓存区需等待刷新次数 | 次 | InstanceId,InstanceType |  |
| InnodbLogWaitsPercent | InnoDB等待刷新率 | % | InstanceId,InstanceType |  |
| InnodbLogWriteRequestsPerSecond | InnoDBredolog写入请求数 | 次/秒 | InstanceId,InstanceType |  |
| InnodbLogWritesPerSecond | InnoDBredolog写入数 | 次/秒 | InstanceId,InstanceType |  |
| InnodbNumOpenFiles | 当前Innodb打开表的数量 | 个 | InstanceId,InstanceType |  |
| InnodbRowLockTimeAvg | InnoDB平均获取行锁时间 | 毫秒 | InstanceId,InstanceType |  |
| InnodbRowLockWaitsPerSecond | InnoDB等待行锁次数 | 次/秒 | InstanceId,InstanceType |  |
| InnodbRowsDeletedPerSecond | InnoDB行删除量 | 次/秒 | InstanceId,InstanceType |  |
| InnodbRowsInsertedPerSecond | InnoDB行插入量 | 次/秒 | InstanceId,InstanceType |  |
| InnodbRowsReadPerSecond | InnoDB行读取量 | 次/秒 | InstanceId,InstanceType |  |
| InnodbRowsUpdatedPerSecond | InnoDB行更新量 | 次/秒 | InstanceId,InstanceType |  |
| InsertCountPerSecond | 每秒插入数 | 次/秒 | InstanceId,InstanceType |  |
| KeyBlocksUnused | 缓存未使用数 | 个 | InstanceId,InstanceType |  |
| KeyBlocksUsed | 缓存使用数 | 个 | InstanceId,InstanceType |  |
| KeyCacheBlockCount | 缓存块数 | 个 | InstanceId,InstanceType |  |
| KeyCacheBlockUsed | 缓存使用块数 | 个 | InstanceId,InstanceType |  |
| KeyCacheHitPercent | 缓存命中率 | % | InstanceId,InstanceType |  |
| KeyCacheUsePercent | 缓存使用率 | % | InstanceId,InstanceType |  |
| KeyReadRequestsPerSecond | 读取缓存请求数 | 个/秒 | InstanceId,InstanceType |  |
| KeyReadsPerSecond | 读取磁盘数 | 个/秒 | InstanceId,InstanceType |  |
| KeyWriteRequestsPerSecond | 写入缓存请求数 | 个/秒 | InstanceId,InstanceType |  |
| KeyWritesPerSecond | 写入磁盘数 | 个/秒 | InstanceId,InstanceType |  |
| LogCapacity | 日志占用空间 | MB | InstanceId,InstanceType |  |
| MasterSlaveSyncDistance | 主备延迟距离 | MB | InstanceId,InstanceType |  |
| MaxConnectionsCount | 最大连接数 | 个 | InstanceId,InstanceType |  |
| MemUsagePercent | 内存使用率 | % | InstanceId,InstanceType |  |
| MemUsedSize | 内存使用空间 | MB | InstanceId,InstanceType |  |
| MysqlDataSize | 磁盘使用空间 | MB | InstanceId,InstanceType |  |
| MysqlDiskUsedSize | 磁盘占用空间 | MB | InstanceId,InstanceType |  |
| MysqlSlowQueriesPt | 慢查询次数 | 次/秒 | InstanceId,InstanceType |  |
| OpenedTablesCount | 已经打开的表数 | 个 | InstanceId,InstanceType |  |
| OpenFilesPerSecond | 打开文件数 | 次/秒 | InstanceId,InstanceType |  |
| Position | 主库混部 | 状态值（1-主库在备机池，0-主库在主机池） | InstanceId,InstanceType |  |
| QcacheFreeBlocks | qcache未使用数 | 个 | InstanceId,InstanceType |  |
| QcacheFreeMemory | qcache可用内存 | MB | InstanceId,InstanceType |  |
| QcacheHitPercent | 查询缓存命中率 | % | InstanceId,InstanceType |  |
| QcacheHitsPerSecond | qcache命中数 | 个/秒 | InstanceId,InstanceType |  |
| QcacheInsertsPerSecond | qchche插入数 | 个/秒 | InstanceId,InstanceType |  |
| QcacheLowmemPrunesPerSecond | qcache删除数 | 个/秒 | InstanceId,InstanceType |  |
| QcacheNotCached | qchche未缓存数 | 万个 | InstanceId,InstanceType |  |
| QcacheQueriesInCachePerSecond | qcache注册数 | 个/秒 | InstanceId,InstanceType |  |
| QcacheTotalBlocks | qchche总块数 | 个 | InstanceId,InstanceType |  |
| QcacheUsePercent | 查询缓存使用率 | % | InstanceId,InstanceType |  |
| QueriesPerSecond | 服务执行语句数-queries | 次/秒 | InstanceId,InstanceType |  |
| QueryCountPerSecond | 每秒执行操作数 | 次/秒 | InstanceId,InstanceType |  |
| QuestionsPerSecond | 服务执行语句数-questions | 次/秒 | InstanceId,InstanceType |  |
| ReadOpCountPerSecond | 查询请求次数 | 次/秒 | InstanceId,InstanceType |  |
| ReplaceCountPerSecond | 每秒覆盖数 | 次/秒 | InstanceId,InstanceType |  |
| SelectCountPerSecond | 每秒查询数 | 次/秒 | InstanceId,InstanceType |  |
| SelectScanCount | 全表扫描数 | 次 | InstanceId,InstanceType |  |
| SlaveBehindMaster | 主备延迟时间 | 秒 | InstanceId,InstanceType |  |
| SlaveIORunning | IO线程状态 | 状态值（1-Yes，0-No） | InstanceId,InstanceType |  |
| SlaveSQLRunning | SQL线程状态 | 状态值（1-Yes，0-No） | InstanceId,InstanceType |  |
| TableLocksImmediatePerSecond | 表锁立即生效数 | 个/秒 | InstanceId,InstanceType |  |
| TableLocksWaitedPerSecond | 等待表锁次数 | 次/秒 | InstanceId,InstanceType |  |
| ThreadConnectedCount | 当前打开连接数 | 个 | InstanceId,InstanceType |  |
| ThreadRunningCount | 运行的线程数 | 个 | InstanceId,InstanceType |  |
| ThreadsCacheHitsPercent | 线程命中率 | % | InstanceId,InstanceType |  |
| ThreadsCacheHitsPercentPerSecond | 线程命中率每秒 | %/秒 | InstanceId,InstanceType |  |
| ThreadsCreatedCount | 已创建的线程数 | 个 | InstanceId,InstanceType |  |
| TPS | 每秒执行事务数 | kb/秒 | InstanceId,InstanceType |  |
| TransactionCountPerSecond | 每秒提交数 | 次/秒 | InstanceId,InstanceType |  |
| TransactionMaxActiveSeconds | 最大事务执行时间 | 秒 | InstanceId,InstanceType |  |
| TransactionRollbackCountPerSecond | 每秒回滚数 | 次/秒 | InstanceId,InstanceType |  |
| UpdateCountPerSecond | 每秒更新数 | 次/秒 | InstanceId,InstanceType |  |
| WriteOpCountPerSecond | 更新请求次数 | 次/秒 | InstanceId,InstanceType |  |

## OceanBase集群（OBCluster）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| sql\_all\_count | QPS | 次 | ClusterId |  |
| sql\_all\_rt | 响应时间 | ms | ClusterId |  |
| all\_session | 会话数 | 个 | ClusterId |  |
| request\_queue\_time | 请求等待队列耗时 | us | ClusterId |  |
| transaction\_count | TPS | 次 | ClusterId |  |
| transaction\_rt | 服务端每个事务平均处理时间 | us | ClusterId |  |
| trans\_commit\_log\_count | 每秒提交的事务日志数 | 个 | ClusterId |  |
| clog\_trans\_log\_total\_size | 每秒提交的事务日志大小 | Bytes | ClusterId |  |
| trans\_commit\_log\_sync\_rt | 每次事务日志网络同步平均耗时 | us | ClusterId |  |
| cpu\_percent | CPU使用率 | % | ClusterId |  |
| memory\_used | 内存使用量 | Bytes | ClusterId |  |
| memory\_percent | 内存使用率 | % | ClusterId |  |
| ntp\_offset\_milliseconds | ntp时钟偏移 | ms | ClusterId |  |
| net\_recv | 每秒接受数据量 | Bytes | ClusterId |  |
| net\_send | 每秒发送数据量 | Bytes | ClusterId |  |
| ob\_data\_disk\_percent | OB数据盘使用率 | % | ClusterId |  |
| ob\_data\_io\_util | OB数据盘IO使用率 | % | ClusterId |  |
| ob\_data\_io\_write\_time | OB数据盘平均每次写IO耗时 | us | ClusterId |  |
| ob\_data\_io\_read\_time | OB数据盘平均每次读IO耗时 | us | ClusterId |  |
| io\_write\_rt | 物理IO写耗时 | us | ClusterId |  |
| io\_read\_rt | 物理IO读耗时 | us | ClusterId |  |
| ob\_process\_exists | OB进程存活状态 |  | ClusterId |  |

## OceanBase租户（OBTenant）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| sql\_all\_count | 平均每秒处理 SQL 语句数 | 次 | ClusterId，TenantId |  |
| sql\_all\_rt | 响应时间 | ms | ClusterId，TenantId |  |
| all\_session | 会话数 | 个 | ClusterId，TenantId |  |
| request\_queue\_time | SQL 请求在等待队列中的等待耗时 | us | ClusterId，TenantId |  |
| active\_memstore\_percent | 租户活跃MEMStore使用率 | % | ClusterId，TenantId |  |
| ob\_tenant\_cpu\_percent | 租户CPU使用率 | % | ClusterId，TenantId |  |
| ob\_tenant\_memory\_percent | 租户内存使用率 | % | ClusterId，TenantId |  |
| memstore\_percent | 租户MEMStore使用率 | % | ClusterId，TenantId |  |
| trans\_commit\_log\_count | 租户每秒提交的事务日志数 | 个 | ClusterId，TenantId |  |
| clog\_trans\_log\_total\_size | 每秒提交的事务日志大小 | Bytes | ClusterId，TenantId |  |
| trans\_commit\_log\_sync\_rt | 每次事务日志网络同步平均耗时 | us | ClusterId，TenantId |  |
| transaction\_count | TPS | 个 | ClusterId，TenantId |  |
| transaction\_rt | 租户处理所有事务的平均耗时 | us | ClusterId，TenantId |  |
| ob\_binlog\_instance\_convert\_delay | Binlog 转换延迟 | 秒 | ClusterId，TenantId |  |
| ob\_binlog\_instance\_convert\_iops | Binlog 转换 IOPS | MiB | ClusterId，TenantId |  |
| ob\_binlog\_instance\_convert\_fetch\_rps | Binlog 转换 RPS | 次 | ClusterId，TenantId |  |
| ob\_binlog\_instance\_convert\_storage\_rps | Binlog 落盘 RPS | 次 | ClusterId，TenantId |  |
| ob\_tenant\_binlog\_disk\_used | Binlog 磁盘使用量 | GiB | ClusterId，TenantId |  |
| ob\_binlog\_instance\_dump\_delay | Binlog 发送延迟 | 秒 | ClusterId，TenantId |  |
| ob\_binlog\_instance\_dump\_iops | Binlog 发送 IOPS | MiB | ClusterId，TenantId |  |
| ob\_binlog\_instance\_dump\_rps | Binlog 发送 RPS | 次 | ClusterId，TenantId |  |

## OceanBase主机监控（OBServer）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| load1 | 过去1分钟系统平均负载 |  | ClusterId，ServerId，ZoneId |  |
| cpu\_percent | 主机CPU使用率 | % | ClusterId，ServerId，ZoneId |  |
| net\_recv | 每秒接受数据量 | Bytes | ClusterId，ServerId，ZoneId |  |
| net\_send | 每秒发送数据量 | Bytes | ClusterId，ServerId，ZoneId |  |
| ntp\_offset\_milliseconds | NTP时钟偏移 | ms | ClusterId，ServerId，ZoneId |  |
| memory\_used | 内存使用量 | Bytes | ClusterId，ServerId，ZoneId |  |
| memory\_percent | 内存使用率 | % | ClusterId，ServerId，ZoneId |  |
| ob\_data\_disk\_percent | OB 数据盘使用率 | % | ClusterId，ServerId，ZoneId |  |
| ob\_data\_io\_util | OB 数据盘IO 使用率 | % | ClusterId，ServerId，ZoneId |  |
| ob\_data\_io\_write\_time | OB 数据盘写耗时 | us | ClusterId，ServerId，ZoneId |  |
| ob\_data\_io\_read\_time | OB 数据盘读耗时 | us | ClusterId，ServerId，ZoneId |  |
| io\_write\_rt | 物理IO写耗时 | us | ClusterId，ServerId，ZoneId |  |
| io\_read\_rt | 物理IO读耗时 | us | ClusterId，ServerId，ZoneId |  |

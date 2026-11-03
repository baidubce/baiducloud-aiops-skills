# 云数据库 HBase

云数据库 HBase 包含2种监控对象类型，分别是：实例监控（Cluster）、节点监控（Instance），各个类型包含的监控指标列表如下：

## 实例监控（Cluster）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| ArchiveStorageCapacityRemainingGB | 归档存储空间剩余容量 | GB | InstanceId |  |
| ArchiveStorageCapacityTotalGB | 归档存储空间总量 | GB | InstanceId |  |
| ArchiveStorageCapacityUsedGB | 归档存储空间已使用容量 | GB | InstanceId |  |
| ArchiveStorageCapacityUsedPercent | 归档存储空间使用率 | % | InstanceId |  |
| CapacityRemainingGB | 系统剩余容量 | GB | InstanceId |  |
| CapacityTotalGB | 系统总体容量 | GB | InstanceId |  |
| CapacityUsedGB | 系统已使用容量 | GB | InstanceId |  |
| CapacityUsedPercent | 系统容量使用率 | % | InstanceId |  |
| RitCountOverThreshold | 超时RIT的Region个数 | 个 | InstanceId |  |

## 节点监控（Instance）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CompactionQueueLength | compaction队列请求数 | 个 | InstanceId,NodeId |  |
| CpuIdle | CPU空闲率 | % | InstanceId,NodeId |  |
| CpuLoadAvg | 平均负载 | % | InstanceId,NodeId |  |
| FreeStorageSize | 可用存储空间大小 | Bytes | InstanceId,NodeId |  |
| GetMean | 读请求平均延时 | ms | InstanceId,NodeId |  |
| HDDFreeStorageSize | HDD可用存储空间大小 | Bytes | InstanceId,NodeId |  |
| HDDUsedStorageRate | HDD已用存储空间比率 | % | InstanceId,NodeId |  |
| HDDUsedStorageSize | HDD已用存储空间大小 | Bytes | InstanceId,NodeId |  |
| IORead | 磁盘读速率 | Bytes/s | InstanceId,NodeId |  |
| IOWrite | 磁盘写速率 | Bytes/s | InstanceId,NodeId |  |
| L1CacheHitRatio | L1 Cache命中率 | % | InstanceId,NodeId |  |
| L2CacheHitRatio | L2 Cache命中率 | % | InstanceId,NodeId |  |
| NetInBytes | 网络流入速率 | Bytes/s | InstanceId,NodeId |  |
| NetOutBytes | 网络流出速率 | Bytes/s | InstanceId,NodeId |  |
| ProcessCpu | CPU使用率 | % | InstanceId,NodeId |  |
| ProcessMem | 内存使用率 | % | InstanceId,NodeId |  |
| PutMean | 写请求平均延时 | ms | InstanceId,NodeId |  |
| ReadQps | 读请求QPS | Query/s | InstanceId,NodeId |  |
| ReceivedBytes | 节点接收字节数 | Bytes | InstanceId,NodeId |  |
| RegionCount | Region个数 | 个 | InstanceId,NodeId |  |
| SentBytes | 节点发送字节数 | Bytes | InstanceId,NodeId |  |
| SSDFreeStorageSize | SSD可用存储空间大小 | Bytes | InstanceId,NodeId |  |
| SSDUsedStorageRate | SSD已用存储空间比率 | % | InstanceId,NodeId |  |
| SSDUsedStorageSize | SSD已用存储空间大小 | Bytes | InstanceId,NodeId |  |
| TSDBConnectionExceptions | TSDB链接异常数 | 个 | InstanceId,NodeId |  |
| TSDBConnections | TSDB链接数 | 个 | InstanceId,NodeId |  |
| TSDBHttpRequestRate | TSDB Http API请求速率 | 个/s | InstanceId,NodeId |  |
| TSDBLatency50Pct | TSDB请求平均延时 | ms | InstanceId,NodeId |  |
| TSDBRpcExceptions | TSDB 请求异常数 | 个 | InstanceId,NodeId |  |
| UsedStorageRate | 已用存储空间比率 | % | InstanceId,NodeId |  |
| UsedStorageSize | 已用存储空间大小 | Bytes | InstanceId,NodeId |  |
| WriteQps | 写请求QPS | Query/s | InstanceId,NodeId |  |

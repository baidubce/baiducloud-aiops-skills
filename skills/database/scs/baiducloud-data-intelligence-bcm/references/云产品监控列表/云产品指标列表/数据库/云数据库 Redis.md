# 云数据库 Redis

云数据库 Redis包含12种监控对象类型，分别是：Redis-社区版-实例（RD\_ST\_INSTANCE）、Redis-社区版-只读节点（RD\_ST\_NODE\_RO）、Redis-企业版-集群（RD\_CL\_CLUSTER）、Redis-企业版-代理（RD\_CL\_PROXY）、Redis-企业版-分片（RD\_CL\_SHARD）、Redis容量型(原 PegaDB)-企业版-集群（PG\_CL\_CLUSTER）、Redis容量型(原 PegaDB)-企业版-代理（PG\_CL\_PROXY）、Redis容量型(原 PegaDB)-企业版-分片（PG\_CL\_SHARD）、Memcache-集群（MC\_CLUSTER）、Memcache-分片（MC\_SHARD）、多活组-集群（RD\_CL\_SYNC\_FLOW\_CLUSTER）、多活组-分片（RD\_CL\_SYNC\_FLOW\_SHARD）。各个类型包含的监控指标列表如下：

## Redis-社区版-实例（RD\_ST\_INSTANCE）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| IOReadBytes | 磁盘读取IO | Bytes | ClusterId,NodeId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOReadBytes | 节点磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOWriteBytes | 节点磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId,NodeId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId,NodeId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |  |
| NodeMemUsedBytes | 节点内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedPercent | 数据内存使用率 | % | ClusterId,NodeId |  |
| NodeDataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkInBytes | 节点网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkOutBytes | 节点网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| NodeQueryCountPerSecond | 节点QPS | 次/秒 | ClusterId,NodeId |  |
| HitPercent | 缓存命中率 | % | ClusterId,NodeId |  |
| ExpiredKeyCount | 过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPeriod | 采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPeriod | 节点采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPerSecond | 每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPerSecond | 节点每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId,NodeId |  |
| NodeKeysNumber | 节点缓存key数量 | 个 | ClusterId,NodeId |  |
| EvictedKeyCount | 驱逐数 | 个 | ClusterId,NodeId |  |
| EvictedKeyCountPeriod | 采样周期内驱逐数 | 个 | ClusterId,NodeId |  |
| KeyspaceMisses | 读请求Miss | 次 | ClusterId,NodeId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId,NodeId |  |
| OmemRatio | 客户端缓冲区利用率 | % | ClusterId,NodeId |  |
| MemFragmentationRatio | 内存碎片率 | - | ClusterId,NodeId |  |
| SlowlogLength | 每秒慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| RedisSlowlogLengthPeriod | Redis采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| NodeSlowlogLengthPeriod | 节点采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPeriod | 节点采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPerSecond | 节点每秒处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessed | 处理命令数 | 次 | ClusterId,NodeId |  |
| LatencyRead | 读平均时延 | ms | ClusterId,NodeId |  |
| LatencyWrite | 写平均时延 | ms | ClusterId,NodeId |  |
| LatencyOther | 其他命令平均时延 | ms | ClusterId,NodeId |  |
| LatencyAvg | 平均执行时延 | ms | ClusterId,NodeId |  |
| LatencyMax | 最大执行时延 | ms | ClusterId,NodeId |  |
| CmdReadQPS | 读请求 | 次/秒 | ClusterId,NodeId |  |
| CmdWriteQPS | 写请求 | 次/秒 | ClusterId,NodeId |  |
| CmdMgetQPS | Mget请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdOtherQPS | 其他请求 | 次/秒 | ClusterId,NodeId |  |
| LatencyP99 | P99执行时延 | us | ClusterId,NodeId |  |
| CmdErr | 每秒执行错误数 | 次/秒 | ClusterId,NodeId |  |
| CmdBigValue | 每秒大Value请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdKeyCount | 每秒Key请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdMissCount | 读请求未命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| RedisMaxConnection | Redis最大连接数 | 个 | ClusterId,NodeId |  |
| NodeMaxConnection | 节点最大连接数 | 个 | ClusterId,NodeId |  |
| RejectedConns | 拒绝连接数 | 个 | ClusterId,NodeId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId,NodeId |  |
| BlockedClients | 被阻塞连接数 | 个 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| NodeConnectedClients | 节点实例连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId,NodeId |  |
| MaxSlavesOffset | 复制最大延迟 | 字节 | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网卡输入流量百分比 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网卡输出流量百分比 | % | ClusterId,NodeId |  |
| FollowerMasterLinkStatus | 热活组主从复制状态 | - | ClusterId,NodeId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId,NodeId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId,NodeId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId,NodeId |  |

  

## Redis-社区版-只读节点（RD\_ST\_NODE\_RO）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| IOReadBytes | 磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOReadBytes | 节点磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOWriteBytes | 节点磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId,NodeId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId,NodeId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |  |
| NodeMemUsedBytes | 节点内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedPercent | 数据内存使用率 | % | ClusterId,NodeId |  |
| NodeDataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkInBytes | 节点网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkOutBytes | 节点网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| NodeQueryCountPerSecond | 节点QPS | 次/秒 | ClusterId,NodeId |  |
| HitPercent | 缓存命中率 | % | ClusterId,NodeId |  |
| ExpiredKeyCount | 过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPeriod | 采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPeriod | 节点采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPerSecond | 每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPerSecond | 节点每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId,NodeId |  |
| NodeKeysNumber | 节点缓存key数量 | 个 | ClusterId,NodeId |  |
| EvictedKeyCount | 驱逐数 | 个 | ClusterId,NodeId |  |
| EvictedKeyCountPeriod | 采样周期内驱逐数 | 个 | ClusterId,NodeId |  |
| KeyspaceMisses | 读请求Miss | 次 | ClusterId,NodeId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId,NodeId |  |
| OmemRatio | 客户端缓冲区利用率 | % | ClusterId,NodeId |  |
| MemFragmentationRatio | 内存碎片率 | - | ClusterId,NodeId |  |
| SlowlogLength | 每秒慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| RedisSlowlogLengthPeriod | Redis采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| NodeSlowlogLengthPeriod | 节点采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPeriod | 节点采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPerSecond | 节点每秒处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessed | 处理命令数 | 次 | ClusterId,NodeId |  |
| LatencyRead | 读平均时延 | ms | ClusterId,NodeId |  |
| LatencyWrite | 写平均时延 | ms | ClusterId,NodeId |  |
| LatencyOther | 其他命令平均时延 | ms | ClusterId,NodeId |  |
| LatencyAvg | 平均执行时延 | ms | ClusterId,NodeId |  |
| LatencyMax | 最大执行时延 | ms | ClusterId,NodeId |  |
| CmdReadQPS | 读请求 | 次/秒 | ClusterId,NodeId |  |
| CmdWriteQPS | 写请求 | 次/秒 | ClusterId,NodeId |  |
| CmdMgetQPS | Mget请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdOtherQPS | 其他请求 | 次/秒 | ClusterId,NodeId |  |
| LatencyP99 | P99执行时延 | us | ClusterId,NodeId |  |
| CmdErr | 每秒执行错误数 | 次/秒 | ClusterId,NodeId |  |
| CmdBigValue | 每秒大Value请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdKeyCount | 每秒Key请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdMissCount | 读请求未命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| RedisMaxConnection | Redis最大连接数 | 个 | ClusterId,NodeId |  |
| NodeMaxConnection | 节点最大连接数 | 个 | ClusterId,NodeId |  |
| RejectedConns | 拒绝连接数 | 个 | ClusterId,NodeId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId,NodeId |  |
| BlockedClients | 被阻塞连接数 | 个 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| NodeConnectedClients | 节点实例连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId,NodeId |  |
| MaxSlavesOffset | 复制最大延迟 | 字节 | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网卡输入流量百分比 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网卡输出流量百分比 | % | ClusterId,NodeId |  |
| FollowerMasterLinkStatus | 热活组主从复制状态 | - | ClusterId,NodeId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId,NodeId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId,NodeId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId,NodeId |  |

  

## Redis-企业版-集群（RD\_CL\_CLUSTER）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId |  |
| IOReadBytes | 磁盘读取IO | 字节/秒 | ClusterId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId |  |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId |  |
| HitPercent | 缓存命中率 | % | ClusterId |  |
| ExpiredKeyCountPeriod | 采样周期内过期Key数量 | 个 | ClusterId |  |
| ExpiredKeyCountPerSecond | 每秒过期Key数量 | 个/秒 | ClusterId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId |  |
| SetCmdQps | SetCmdQps | 次/秒 | ClusterId |  |
| GetCmdQps | GetCmdQps | 次/秒 | ClusterId |  |
| IncrCmdQps | IncrCmdQps | 次/秒 | ClusterId |  |
| HgetCmdQps | HgetCmdQps | 次/秒 | ClusterId |  |
| HsetCmdQps | HsetCmdQps | 次/秒 | ClusterId |  |
| LpushCmdQps | LpushCmdQps | 次/秒 | ClusterId |  |
| RpushCmdQps | RpushCmdQps | 次/秒 | ClusterId |  |
| LpopCmdQps | LpopCmdQps | 次/秒 | ClusterId |  |
| RpopCmdQps | RpopCmdQps | 次/秒 | ClusterId |  |
| SaddCmdQps | SaddCmdQps | 次/秒 | ClusterId |  |
| ScardCmdQps | ScardCmdQps | 次/秒 | ClusterId |  |
| SismemberCmdQps | SismemberCmdQps | 次/秒 | ClusterId |  |
| ZaddCmdQps | ZaddCmdQps | 次/秒 | ClusterId |  |
| ZcardCmdQps | ZcardCmdQps | 次/秒 | ClusterId |  |
| ZcountCmdQps | ZcountCmdQps | 次/秒 | ClusterId |  |
| RealWriteQps | WriteQPS | 次/秒 | ClusterId |  |
| RealReadQps | ReadQPS | 次/秒 | ClusterId |  |
| SlowlogLength | 慢查询次数 | 次 | ClusterId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId |  |
| MemFragmentationRatio | 内存碎片率 | - | ClusterId |  |
| OmemRatio | 客户端缓冲区利用率 | % | ClusterId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId |  |
| EvictedKeyCount | 驱逐数 | 个 | ClusterId |  |
| EvictedKeyCountPeriod | 采样周期内驱逐数 | 个 | ClusterId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId |  |
| BlockedClients | 被阻塞连接数 | 个 | ClusterId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId |  |
| RedisLocalCli | 实例状态 | % | ClusterId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId |  |
| FollowerMasterLinkStatus | 热热活组主从复制状态 | - | ClusterId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId |  |
| LatencyMax | 最大时延 | us | ClusterId |  |
| ResponsesErr | 失败请求数 | 次 | ClusterId |  |
| ReachQpsQuota | QPS 限流次数 | 次 | ClusterId |  |
| ReachClientInputBandwidthQuota | 带宽限流次数 | 次 | ClusterId |  |

  

## Redis-企业版-代理（RD\_CL\_PROXY）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| SetCmdQps | SetCmdQps | 次/秒 | ClusterId,NodeId |  |
| GetCmdQps | GetCmdQps | 次/秒 | ClusterId,NodeId |  |
| IncrCmdQps | IncrCmdQps | 次/秒 | ClusterId,NodeId |  |
| HgetCmdQps | HgetCmdQps | 次/秒 | ClusterId,NodeId |  |
| HsetCmdQps | HsetCmdQps | 次/秒 | ClusterId,NodeId |  |
| LpushCmdQps | LpushCmdQps | 次/秒 | ClusterId,NodeId |  |
| RpushCmdQps | RpushCmdQps | 次/秒 | ClusterId,NodeId |  |
| LpopCmdQps | LpopCmdQps | 次/秒 | ClusterId,NodeId |  |
| RpopCmdQps | RpopCmdQps | 次/秒 | ClusterId,NodeId |  |
| SaddCmdQps | SaddCmdQps | 次/秒 | ClusterId,NodeId |  |
| ScardCmdQps | ScardCmdQps | 次/秒 | ClusterId,NodeId |  |
| SismemberCmdQps | SismemberCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZaddCmdQps | ZaddCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZcardCmdQps | ZcardCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZcountCmdQps | ZcountCmdQps | 次/秒 | ClusterId,NodeId |  |
| CmdReadQPS | 读请求 | 次/秒 | ClusterId,NodeId |  |
| CmdWriteQPS | 写请求 | 次/秒 | ClusterId,NodeId |  |
| ProxyQueryCountPerSecond | ProxyQPS | 次/秒 | ClusterId,NodeId |  |
| CmdOtherQPS | 其他请求 | 次/秒 | ClusterId,NodeId |  |
| RealRspTime | 后端Server平均响应时间 | us | ClusterId,NodeId |  |
| RealWriteQps | WriteQPS | 次/秒 | ClusterId,NodeId |  |
| RealReadQps | ReadQPS | 次/秒 | ClusterId,NodeId |  |
| CmdMgetQPS | Mget请求数 | 次/秒 | ClusterId,NodeId |  |
| LatencyP99 | P99执行时延 | us | ClusterId,NodeId |  |
| LatencyAvg | 平均执行时延 | us | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| SlowlogLength | 慢查询次数 | 次 | ClusterId,NodeId |  |
| ProxySlowlogLengthPeriod | Proxy采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| PVLost | PVLost | - | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| LatencyMax | 最大时延 | us | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网络输入带宽使用率 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网络输出带宽使用率 | % | ClusterId,NodeId |  |
| ResponsesErr | 失败请求数 |  | ClusterId,NodeId |  |
| ReachQpsQuota | QPS 限流次数 |  | ClusterId,NodeId |  |
| ReachClientInputBandwidthQuota | 带宽限流次数 |  | ClusterId,NodeId |  |

  

## Redis-企业版-分片（RD\_CL\_SHARD）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| IOReadBytes | 磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOReadBytes | 节点磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOWriteBytes | 节点磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId,NodeId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId,NodeId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |  |
| NodeMemUsedBytes | 节点内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedPercent | 数据内存使用率 | % | ClusterId,NodeId |  |
| NodeDataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| DataMemUsedBytes | 节点数据内存使用量 | 字节 | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkInBytes | 节点网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkOutBytes | 节点网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| NodeQueryCountPerSecond | 节点QPS | 次/秒 | ClusterId,NodeId |  |
| HitPercent | 缓存命中率 | % | ClusterId,NodeId |  |
| ExpiredKeyCount | 过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPeriod | 采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPeriod | 节点采样周期内过期Key数量 | 个 | ClusterId,NodeId |  |
| ExpiredKeyCountPerSecond | 每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| NodeExpiredKeyCountPerSecond | 节点每秒过期Key数量 | 个/秒 | ClusterId,NodeId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId,NodeId |  |
| NodeKeysNumber | 节点缓存key数量 | 个 | ClusterId,NodeId |  |
| EvictedKeyCount | 驱逐数 | 个 | ClusterId,NodeId |  |
| EvictedKeyCountPeriod | 采样周期内驱逐数 | 个 | ClusterId,NodeId |  |
| KeyspaceMisses | 读请求Miss | 次 | ClusterId,NodeId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId,NodeId |  |
| OmemRatio | 客户端缓冲区利用率 | % | ClusterId,NodeId |  |
| MemFragmentationRatio | 内存碎片率 | - | ClusterId,NodeId |  |
| SlowlogLength | 每秒慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| RedisSlowlogLengthPeriod | Redis采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| NodeSlowlogLengthPeriod | 节点采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPeriod | 节点采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId,NodeId |  |
| NodeTotalCmdProcessedPerSecond | 节点每秒处理命令数 | 次 | ClusterId,NodeId |  |
| TotalCmdProcessed | 处理命令数 | 次 | ClusterId,NodeId |  |
| LatencyRead | 读平均时延 | ms | ClusterId,NodeId |  |
| LatencyWrite | 写平均时延 | ms | ClusterId,NodeId |  |
| LatencyOther | 其他命令平均时延 | ms | ClusterId,NodeId |  |
| LatencyAvg | 平均执行时延 | ms | ClusterId,NodeId |  |
| LatencyMax | 最大执行时延 | ms | ClusterId,NodeId |  |
| CmdReadQPS | 读请求 | 次/秒 | ClusterId,NodeId |  |
| CmdWriteQPS | 写请求 | 次/秒 | ClusterId,NodeId |  |
| CmdMgetQPS | Mget请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdOtherQPS | 其他请求 | 次/秒 | ClusterId,NodeId |  |
| LatencyP99 | P99执行时延 | us | ClusterId,NodeId |  |
| CmdErr | 每秒执行错误数 | 次/秒 | ClusterId,NodeId |  |
| CmdBigValue | 每秒大Value请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdKeyCount | 每秒Key请求数 | 次/秒 | ClusterId,NodeId |  |
| CmdMissCount | 读请求未命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| RedisMaxConnection | Redis最大连接数 | 个 | ClusterId,NodeId |  |
| NodeMaxConnection | 节点最大连接数 | 个 | ClusterId,NodeId |  |
| RejectedConns | 拒绝连接数 | 个 | ClusterId,NodeId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId,NodeId |  |
| BlockedClients | 被阻塞连接数 | 个 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| NodeConnectedClients | 节点实例连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId,NodeId |  |
| MaxSlavesOffset | 复制最大延迟 | 字节 | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网卡输入流量百分比 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网卡输出流量百分比 | % | ClusterId,NodeId |  |
| FollowerMasterLinkStatus | 热热活组主从复制状态 | - | ClusterId,NodeId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId,NodeId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId,NodeId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId,NodeId |  |

  

## Redis容量型(原 PegaDB)-企业版-集群（PG\_CL\_CLUSTER）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId |  |
| IOReadBytes | 磁盘读取IO | 字节/秒 | ClusterId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId |  |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId |  |
| HitPercent | 命中率 | % | ClusterId |  |
| BlockCacheHitPercent | BlockCache命中率 | % | ClusterId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId |  |
| SetCmdQps | SetCmdQps | 次/秒 | ClusterId |  |
| GetCmdQps | GetCmdQps | 次/秒 | ClusterId |  |
| IncrCmdQps | IncrCmdQps | 次/秒 | ClusterId |  |
| HgetCmdQps | HgetCmdQps | 次/秒 | ClusterId |  |
| HsetCmdQps | HsetCmdQps | 次/秒 | ClusterId |  |
| LpushCmdQps | LpushCmdQps | 次/秒 | ClusterId |  |
| RpushCmdQps | RpushCmdQps | 次/秒 | ClusterId |  |
| LpopCmdQps | LpopCmdQps | 次/秒 | ClusterId |  |
| RpopCmdQps | RpopCmdQps | 次/秒 | ClusterId |  |
| SaddCmdQps | SaddCmdQps | 次/秒 | ClusterId |  |
| ScardCmdQps | ScardCmdQps | 次/秒 | ClusterId |  |
| SismemberCmdQps | SismemberCmdQps | 次/秒 | ClusterId |  |
| ZaddCmdQps | ZaddCmdQps | 次/秒 | ClusterId |  |
| ZcardCmdQps | ZcardCmdQps | 次/秒 | ClusterId |  |
| ZcountCmdQps | ZcountCmdQps | 次/秒 | ClusterId |  |
| RealWriteQps | WriteQPS | 次/秒 | ClusterId |  |
| RealReadQps | ReadQPS | 次/秒 | ClusterId |  |
| SlowlogLength | 慢查询次数 | 次 | ClusterId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId |  |
| RedisLocalCli | 实例状态 | % | ClusterId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId |  |
| DataDiskUsage | 数据空间使用率 | % | ClusterId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId |  |
| FollowerMasterLinkStatus | 热热活组主从复制状态 | - | ClusterId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId |  |
| DataDiskUsed | 数据文件占用空间 | MB | ClusterId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId |  |
| BlockCacheHitPercentPeriod | 采样周期内BlockCache命中率 | % | ClusterId |  |
| LatencyMax | 最大时延 | us | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网络输入带宽使用率 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网络输出带宽使用率 | % | ClusterId,NodeId |  |
| ResponsesErr | 失败请求数 | 次 | ClusterId,NodeId |  |
| ReachQpsQuota | QPS 限流次数 | 次 | ClusterId,NodeId |  |
| ReachClientInputBandwidthQuota | 带宽限流次数 | 次 | ClusterId,NodeId |  |

  

## Redis容量型(原 PegaDB)-企业版-代理（PG\_CL\_PROXY）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| SetCmdQps | SetCmdQps | 次/秒 | ClusterId,NodeId |  |
| GetCmdQps | GetCmdQps | 次/秒 | ClusterId,NodeId |  |
| IncrCmdQps | IncrCmdQps | 次/秒 | ClusterId,NodeId |  |
| HgetCmdQps | HgetCmdQps | 次/秒 | ClusterId,NodeId |  |
| HsetCmdQps | HsetCmdQps | 次/秒 | ClusterId,NodeId |  |
| LpushCmdQps | LpushCmdQps | 次/秒 | ClusterId,NodeId |  |
| RpushCmdQps | RpushCmdQps | 次/秒 | ClusterId,NodeId |  |
| LpopCmdQps | LpopCmdQps | 次/秒 | ClusterId,NodeId |  |
| RpopCmdQps | RpopCmdQps | 次/秒 | ClusterId,NodeId |  |
| SaddCmdQps | SaddCmdQps | 次/秒 | ClusterId,NodeId |  |
| ScardCmdQps | ScardCmdQps | 次/秒 | ClusterId,NodeId |  |
| SismemberCmdQps | SismemberCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZaddCmdQps | ZaddCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZcardCmdQps | ZcardCmdQps | 次/秒 | ClusterId,NodeId |  |
| ZcountCmdQps | ZcountCmdQps | 次/秒 | ClusterId,NodeId |  |
| CmdReadQPS | 读请求 | 次/秒 | ClusterId,NodeId |  |
| CmdWriteQPS | 写请求 | 次/秒 | ClusterId,NodeId |  |
| ProxyQueryCountPerSecond | ProxyQPS | 次/秒 | ClusterId,NodeId |  |
| CmdOtherQPS | 其他请求 | 次/秒 | ClusterId,NodeId |  |
| RealRspTime | 后端Server平均响应时间 | us | ClusterId,NodeId |  |
| RealWriteQps | WriteQPS | 次/秒 | ClusterId,NodeId |  |
| RealReadQps | ReadQPS | 次/秒 | ClusterId,NodeId |  |
| CmdMgetQPS | Mget请求数 | 次/秒 | ClusterId,NodeId |  |
| LatencyP99 | P99执行时延 | us | ClusterId,NodeId |  |
| LatencyAvg | 平均执行时延 | us | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| SlowlogLength | 慢查询次数 | 次 | ClusterId,NodeId |  |
| ProxySlowlogLengthPeriod | Proxy采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| PVLost | PVLost | - | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| LatencyMax | 最大时延 | us | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网络输入带宽使用率 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网络输出带宽使用率 | % | ClusterId,NodeId |  |
| ResponsesErr | 失败请求数 | 次 | ClusterId,NodeId |  |
| ReachQpsQuota | QPS 限流次数 | 次 | ClusterId,NodeId |  |
| ReachClientInputBandwidthQuota | 带宽限流次数 | 次 | ClusterId,NodeId |  |

  

## Redis容量型(原 PegaDB)-企业版-分片（PG\_CL\_SHARD）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| NodeIOWriteBytes | 节点磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| IOWriteBytes | 磁盘写入IO | 字节/秒 | ClusterId,NodeId |  |
| NodeIOReadBytes | 节点磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| IOReadBytes | 磁盘读取IO | 字节/秒 | ClusterId,NodeId |  |
| DiskUsage | 磁盘空间使用率 | % | ClusterId,NodeId |  |
| DiskUsed | 磁盘空间使用量 | 兆字节 | ClusterId,NodeId |  |
| DataDiskUsed | 数据文件占用空间 | 兆字节 | ClusterId,NodeId |  |
| DataDiskUsage | 数据空间使用率 | % | ClusterId,NodeId |  |
| DataDiskUsedBytes | 数据文件占用空间字节数 | 字节 | ClusterId,NodeId |  |
| DiskUsedPercent | 数据盘空间使用量 | % | ClusterId,NodeId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId,NodeId |  |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |  |
| NodeMemUsedBytes | 节点内存使用量 | 字节 | ClusterId,NodeId |  |
| NodeNetworkInBytes | 节点网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkOutBytes | 节点网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| TotalCmdProcessedPerSecond | 每秒处理命令数 | 次/秒 | ClusterId,NodeId |  |
| TotalCmdProcessedPeriod | 采样周期内处理命令数 | 次 | ClusterId,NodeId |  |
| SlowlogLengthPeriod | 采样周期内慢查询次数 | 次 | ClusterId,NodeId |  |
| SlowlogLength | 每秒慢查询次数 | 次 | ClusterId,NodeId |  |
| KeyspaceMissesPeriod | 采样周期内读请求Miss | 次 | ClusterId,NodeId |  |
| CmdHitsCount | 读请求命中 | 次 | ClusterId,NodeId |  |
| CmdHitsCountPeriod | 采样周期内读请求命中 | 次 | ClusterId,NodeId |  |
| ConnectionPercent | 连接使用率 | % | ClusterId,NodeId |  |
| NodeConnectedClients | 节点实例连接数 | 个 | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| RejectedConnsPeriod | 采样周期拒绝连接数 | 个 | ClusterId,NodeId |  |
| MaxConnection | 最大连接数 | 个 | ClusterId,NodeId |  |
| RedisLocalCli | 实例状态 | % | ClusterId,NodeId |  |
| MasterLinkStatus | 复制状态 | - | ClusterId,NodeId |  |
| KeysNumber | 缓存key数量 | 个 | ClusterId,NodeId |  |
| BlockCacheHitPercent | BlockCache命中率 | % | ClusterId,NodeId |  |
| HitPercent | 命中率 | % | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网卡输入流量百分比 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网卡输出流量百分比 | % | ClusterId,NodeId |  |
| FollowerMasterLinkStatus | 热热活组主从复制状态 | - | ClusterId,NodeId |  |
| FollowerMasterLastIoSecondsAgo | 热活组主从MasterLastIoSecondsAgo | 秒 | ClusterId,NodeId |  |
| FollowerReplOffset | 热活组主从复制延迟 | byte | ClusterId,NodeId |  |
| HitPercentPeriod | 采样周期内缓存命中率 | % | ClusterId,NodeId |  |
| BlockCacheHitPercentPeriod | 采样周期内BlockCache命中率 | % | ClusterId,NodeId |  |

  

## Memcache-集群（MC\_CLUSTER）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId |  |
| EliminateRate | 数据淘汰率 | % | ClusterId |  |
| HitPercent | 命中率 | % | ClusterId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId |  |

  

## Memcache-分片（MC\_SHARD）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |  |
| MemUsedBytes | 内存使用量 | 字节 | ClusterId,NodeId |  |
| NodeNetworkInBytes | 节点网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NodeNetworkOutBytes | 节点网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkInBytes | 网络输入量 | 字节/秒 | ClusterId,NodeId |  |
| NetworkOutBytes | 网络输出量 | 字节/秒 | ClusterId,NodeId |  |
| HitPercent | 缓存命中率 | % | ClusterId,NodeId |  |
| ConnectedClients | 实例连接数 | 个 | ClusterId,NodeId |  |
| NodeConnectedClients | 节点实例连接数 | 个 | ClusterId,NodeId |  |
| EliminateRate | 数据淘汰率 | % | ClusterId,NodeId |  |
| QueryCountPerSecond | QPS | 次/秒 | ClusterId,NodeId |  |
| NetworkInBandwidthPercent | 网卡输入流量百分比 | % | ClusterId,NodeId |  |
| NetworkOutBandwidthPercent | 网卡输出流量百分比 | % | ClusterId,NodeId |  |

  

## 多活组-集群（RD\_CL\_SYNC\_FLOW\_CLUSTER）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| SyncDelayOpCount | 延迟命令数 | 个 | ClusterId |  |
| SyncDelayTime | 延迟时间 | ms | ClusterId |  |

  

## 多活组-分片（RD\_CL\_SYNC\_FLOW\_SHARD）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| SyncDelayOpCount | 延迟命令数 | 个 | ClusterId,NodeId |  |
| SyncDelayTime | 延迟时间 | ms | ClusterId,NodeId |  |

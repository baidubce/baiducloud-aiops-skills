# 向量数据库 VectorDB

向量数据库 VectorDB 包含 10 种监控对象类型，分别是：VDB集群监控（Cluster）、VDB数据节点监控（DataNode）、VDB代理节点监控（Proxy）、VDB单机监控（Standalone）；Milvus代理节点（MilvusProxy）、Milvus流节点（MilvusStreaming）、Milvus查询节点（MilvusQuery）、Milvus数据节点（MilvusData）、Milvus协调节点（MilvusCoord）、Milvus集群（MilvusCluster），各个类型包含的监控指标列表如下：

## VDB集群监控（Cluster）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 |
| --- | --- | --- | --- |
| DeleteCountPerSecond | Delete每秒请求 | count/s | ClusterId |
| DeleteLatencyAvg | Delete请求平均耗时 | ms | ClusterId |
| InsertCountPerSecond | Insert每秒请求 | count/s | ClusterId |
| InsertLatencyAvg | Insert请求平均耗时 | ms | ClusterId |
| QueryCountPerSecond | Query每秒请求 | count/s | ClusterId |
| QueryLatencyAvg | Query请求平均耗时 | ms | ClusterId |
| SearchCountPerSecond | Search每秒请求 | count/s | ClusterId |
| SearchLatencyAvg | Search请求平均耗时 | ms | ClusterId |
| TotalCountPerSecond | Total每秒请求 | count/s | ClusterId |
| TotalLatencyAvg | 总请求平均时延 | ms | ClusterId |
| UpsertCountPerSecond | Upsert每秒请求 | count/s | ClusterId |
| UpsertLatencyAvg | Upsert请求平均耗时 | ms | ClusterId |

## VDB数据节点监控（DataNode）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 |
| --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |
| DeleteCountPerSecond | Delete每秒请求 | count/s | ClusterId,NodeId |
| DeleteLatencyAvg | Delete请求平均耗时 | ms | ClusterId,NodeId |
| DiskUsedMBytes | 磁盘空间使用量 | MBytes | ClusterId,NodeId |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId,NodeId |
| InsertCountPerSecond | Insert每秒请求 | count/s | ClusterId,NodeId |
| InsertLatencyAvg | Insert请求平均耗时 | ms | ClusterId,NodeId |
| MemUsedBytes | MemUsedBytes | Bytes | ClusterId,NodeId |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |
| NetworkInMBytes | 入流量 | MB/s | ClusterId,NodeId |
| NetworkOutMBytes | 出流量 | count/s | ClusterId,NodeId |
| QueryCountPerSecond | Query每秒请求 | count/s | ClusterId,NodeId |
| QueryLatencyAvg | Query请求平均耗时 | ms | ClusterId,NodeId |
| SearchCountPerSecond | Search每秒请求 | count/s | ClusterId,NodeId |
| SearchLatencyAvg | Search请求平均耗时 | ms | ClusterId,NodeId |
| TotalCountPerSecond | Total每秒请求 | count/s | ClusterId,NodeId |
| TotalLatencyAvg | 总请求平均时延 | ms | ClusterId,NodeId |
| UpsertCountPerSecond | Upsert每秒请求 | count/s | ClusterId,NodeId |
| UpsertLatencyAvg | Upsert请求平均耗时 | ms | ClusterId,NodeId |

## VDB代理节点监控（Proxy）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 |
| --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId,NodeId |
| DiskUsedMBytes | 磁盘空间使用量 | MBytes | ClusterId,NodeId |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId,NodeId |
| MemUsedBytes | MemUsedBytes | Bytes | ClusterId,NodeId |
| MemUsedPercent | 内存使用率 | % | ClusterId,NodeId |
| NetworkInMBytes | 入流量 | MB/s | ClusterId,NodeId |
| NetworkOutMBytes | 出流量 | count/s | ClusterId,NodeId |

## VDB单机监控（Standalone）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 |
| --- | --- | --- | --- |
| CPUUsagePercent | CPU使用率 | % | ClusterId |
| DeleteCountPerSecond | Delete每秒请求 | count/s | ClusterId |
| DeleteLatencyAvg | Delete请求平均耗时 | ms | ClusterId |
| DiskUsedMBytes | 磁盘空间使用量 | MBytes | ClusterId |
| DiskUsedPercent | 磁盘使用率 | % | ClusterId |
| InsertCountPerSecond | Insert每秒请求 | count/s | ClusterId |
| InsertLatencyAvg | Insert请求平均耗时 | ms | ClusterId |
| MemUsedBytes | 内存使用量 | Bytes | ClusterId |
| MemUsedPercent | 内存使用率 | % | ClusterId |
| NetworkInMBytes | 入流量 | MB/s | ClusterId |
| NetworkOutMBytes | 出流量 | MB/s | ClusterId |
| QueryCountPerSecond | Query每秒请求 | count/s | ClusterId |
| QueryLatencyAvg | Query请求平均耗时 | ms | ClusterId |
| SearchCountPerSecond | Search每秒请求 | count/s | ClusterId |
| SearchLatencyAvg | Search请求平均耗时 | ms | ClusterId |
| TotalCountPerSecond | 总请求QPS | count/s | ClusterId |
| TotalLatencyAvg | 总请求平均时延 | ms | ClusterId |
| UpsertCountPerSecond | Upsert每秒请求 | count/s | ClusterId |
| UpsertLatencyAvg | Upsert请求平均耗时 | ms | ClusterId |

## Milvus代理节点（MilvusProxy）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| ProxySearchVectorCountPerSecond | 每秒搜索向量数量 | count/s | ClusterId,NodeId |  |
| ProxyInsertVectorCountPerSecond | 每秒插入向量数量 | count/s | ClusterId,NodeId |  |
| ProxyReceivedBytesPerSecond | 每秒接收数据量 | bytes/s | ClusterId,NodeId |  |
| ProxySentBytesPerSecond | 每秒发送数据量 | bytes/s | ClusterId,NodeId |  |
| ProxyRateLimitRequestCountPerSecond | 每秒被限流请求数 | count/s | ClusterId,NodeId |  |
| ProxySearchLatencyAvg | 搜索操作平均延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyP99 | 搜索操作P99延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyAvg | 查询操作平均延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyP99 | 查询操作P99延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInWaitResultAvg | 搜索等待结果阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInWaitResultP99 | 搜索等待结果阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInReduceResultAvg | 搜索结果归约阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInReduceResultP99 | 搜索结果归约阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInDecodeResultAvg | 搜索结果解码阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxySearchLatencyInDecodeResultP99 | 搜索结果解码阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInWaitResultAvg | 查询等待结果阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInWaitResultP99 | 查询等待结果阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInReduceResultAvg | 查询结果归约阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInReduceResultP99 | 查询结果归约阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInDecodeResultAvg | 查询结果解码阶段平均延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryLatencyInDecodeResultP99 | 查询结果解码阶段P99延迟 | ms | ClusterId,NodeId |  |
| ProxyMutationLatencyAvg | 写操作平均延迟 | ms | ClusterId,NodeId |  |
| ProxyMutationLatencyP99 | 写操作P99延迟 | ms | ClusterId,NodeId |  |
| ProxyApplyPkLatencyAvg | 主键分配平均延迟 | ms | ClusterId,NodeId |  |
| ProxyApplyPkLatencyP99 | 主键分配P99延迟 | ms | ClusterId,NodeId |  |
| ProxyTotalInQueueLatencyAvg | 请求排队平均延迟 | ms | ClusterId,NodeId |  |
| ProxyTotalInQueueLatencyP99 | 请求排队P99延迟 | ms | ClusterId,NodeId |  |
| ProxyInsertInQueueLatencyAvg | 写请求排队平均延迟 | ms | ClusterId,NodeId |  |
| ProxyInsertInQueueLatencyP99 | 写请求排队P99延迟 | ms | ClusterId,NodeId |  |
| ProxySearchInQueueLatencyAvg | 搜索请求排队平均延迟 | ms | ClusterId,NodeId |  |
| ProxySearchInQueueLatencyP99 | 搜索请求排队P99延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryInQueueLatencyAvg | 查询请求排队平均延迟 | ms | ClusterId,NodeId |  |
| ProxyQueryInQueueLatencyP99 | 查询请求排队P99延迟 | ms | ClusterId,NodeId |  |
| ProxyCacheUpdateLatencyAvg | 缓存更新平均延迟 | ms | ClusterId,NodeId |  |
| ProxyCacheUpdateLatencyP99 | 缓存更新P99延迟 | ms | ClusterId,NodeId |  |
| ProxyTotalRequestLatencyAvg | 请求平均延迟 | ms | ClusterId,NodeId |  |
| ProxyTotalRequestLatencyP99 | 请求P99延迟 | ms | ClusterId,NodeId |  |
| ProxyInsertRequestLatencyAvg | 写请求平均延迟 | ms | ClusterId,NodeId |  |
| ProxyInsertRequestLatencyP99 | 写请求P99延迟 | ms | ClusterId,NodeId |  |
| ProxyApplyTimestampLatencyAvg | 时间戳分配平均延迟 | ms | ClusterId,NodeId |  |
| ProxyApplyTimestampLatencyP99 | 时间戳分配P99延迟 | ms | ClusterId,NodeId |  |
| ProxyTotalSuccessRequestPerSecond | 每秒成功请求数 | count | ClusterId,NodeId |  |
| ProxyInsertSuccessRequestPerSecond | 每秒写入成功请求数 | count | ClusterId,NodeId |  |
| ProxySearchSuccessRequestPerSecond | 每秒搜索成功请求数 | count | ClusterId,NodeId |  |
| ProxyQuerySuccessRequestPerSecond | 每秒查询成功请求数 | count | ClusterId,NodeId |  |
| ProxyTotalFailRequestPerSecond | 每秒失败请求数 | count | ClusterId,NodeId |  |
| ProxyInsertFailRequestPerSecond | 每秒写入失败请求数 | count | ClusterId,NodeId |  |
| ProxySearchFailRequestPerSecond | 每秒搜索失败请求数 | count | ClusterId,NodeId |  |
| ProxyQueryFailRequestPerSecond | 每秒查询失败请求数 | count | ClusterId,NodeId |  |
| SuccessRequestCount1m | 最近1分钟成功请求总数 | count | ClusterId,NodeId |  |
| FailRequestCount1m | 最近1分钟失败请求总数 | count | ClusterId,NodeId |  |
| ProxySlowQueryCount1m | 最近1分钟慢查询次数 | count | ClusterId,NodeId |  |
| ProxySearchCountPerSecond | 搜索操作QPS | count/s | ClusterId,NodeId |  |
| ProxyInsertCountPerSecond | 写入操作QPS | count/s | ClusterId,NodeId |  |
| ProxyDeleteCountPerSecond | 删除操作QPS | count/s | ClusterId,NodeId |  |
| CPUUsage | CPU 使用率 | % | ClusterId,NodeId |  |
| CPUCoresUsed | CPU 使用核数 | cores | ClusterId,NodeId |  |
| GoroutinesCount | Goroutine 数量 | count | ClusterId,NodeId |  |
| OSThreadsCount | OS 线程数量 | count | ClusterId,NodeId |  |
| ProcessOpenedFds | 进程打开文件描述符数量 | count | ClusterId,NodeId |  |
| MemoryUsage | 内存使用率 | % | ClusterId,NodeId |  |
| MemoryUsedBytes | 内存使用量 | bytes | ClusterId,NodeId |  |
| HeapAllocatedMemoryBytes | Go 堆已分配内存 | bytes | ClusterId,NodeId |  |
| GCMaxDurationSeconds | GC 最大暂停时间 | ms | ClusterId,NodeId |  |
| NextGCBytes | 下次 GC 触发内存阈值 | bytes | ClusterId,NodeId |  |
| AllocatedHeapObjects | 已分配堆对象数量 | count | ClusterId,NodeId |  |
| MemoryFreePerSecond | 内存释放速率 | count/s | ClusterId,NodeId |  |
| MemoryMallocsPerSecond | 内存分配速率 | count/s | ClusterId,NodeId |  |
| HeapIdleBytes | Go 堆空闲内存 | bytes | ClusterId,NodeId |  |
| MemoryAllocatedBytesPerSecond | 内存分配速率（字节） | bytes/s | ClusterId,NodeId |  |
| HeapReleasedBytes | Go 堆已释放内存 | bytes | ClusterId,NodeId |  |
| HeapInUseBytes | Go 堆使用内存 | bytes | ClusterId,NodeId |  |

## Milvus流节点（MilvusStreaming）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| DataNodeFlushOperateCountPerSecond | 每秒 Flush 操作次数 | count | ClusterId,NodeId |  |
| DataNodeConsumedMessageInsert | 每秒消费插入消息数 | count/s | ClusterId,NodeId |  |
| DataNodeConsumedMessageAll | 秒消费全部消息数 | count/s | ClusterId,NodeId |  |
| DataNodeTimetickLagBehindNowMin | TimeTick 落后当前时间最小值 | ms | ClusterId,NodeId |  |
| DataNodeTimetickLagBehindNowMax | TimeTick 落后当前时间最大值 | ms | ClusterId,NodeId |  |
| DataNodeTimetickLagBehindNowAvg | TimeTick 落后当前时间平均值 | ms | ClusterId,NodeId |  |
| DataNodeMsgRowsConsumedInsertRate | 每秒消费插入消息行数 | count/s | ClusterId,NodeId |  |
| DataNodeAutoFlushCountPerSecond | 每秒 AutoFlush 操作次数 | count/s | ClusterId,NodeId |  |
| DataNodeFlushDataBytesPerSecond | 每秒 Flush 数据量 | bytes/s | ClusterId,NodeId |  |
| DataNodeSaveDataLatencyAvg | 数据保存平均延迟 | ms | ClusterId,NodeId |  |
| DataNodeSaveDataLatencyP99 | 数据保存 P99 延迟 | ms | ClusterId,NodeId |  |
| DataNodeTotalOfInflightConsumeBody | Inflight Consume Body 总数 | count | ClusterId,NodeId |  |
| DataNodeMsgQueueConsumerNum | 消息队列消费者数量 | count | ClusterId,NodeId |  |
| DataNodeConsumeBytesLatencyAvg | 消费字节平均延迟 | ms | ClusterId,NodeId |  |
| DataNodeConsumeBytesLatencyP99 | 消费字节 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryCollectionLoadedNum | 已加载 Collection 数量 | count | ClusterId,NodeId |  |
| QuerySegmentLoadedNum | 已加载 Segment 数量 | count | ClusterId,NodeId |  |
| QuerySearchRequestSuccess | 搜索成功请求数 | count | ClusterId,NodeId |  |
| QuerySearchRequestFail | 搜索失败请求数 | count | ClusterId,NodeId |  |
| QueryQueryRequestSuccess | 查询成功请求数 | count | ClusterId,NodeId |  |
| QueryQueryRequestFail | 查询失败请求数 | count | ClusterId,NodeId |  |
| QuerySearchLatencyAvg | 搜索请求平均延迟 | ms | ClusterId,NodeId |  |
| QuerySearchLatencyP99 | 搜索请求 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryQueryLatencyAvg | 查询请求平均延迟 | ms | ClusterId,NodeId |  |
| QueryQueryLatencyP99 | 查询请求 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryNodeSearchReduceLatencyAvg | 搜索归约平均延迟 | ms | ClusterId,NodeId |  |
| QueryNodeSearchReduceLatencyP99 | 搜索归约 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryQueryReduceLatencyAvg | 查询归约平均延迟 | ms | ClusterId,NodeId |  |
| QueryQueryReduceLatencyP99 | 查询归约 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryReadyReadTaskLength | 就绪读任务长度 | count | ClusterId,NodeId |  |
| QueryFlowgraphNum | Flowgraph 数量 | count | ClusterId,NodeId |  |
| QueryWaitTsafeLatencyAvg | 等待 tSafe 平均延迟 | ms | ClusterId,NodeId |  |
| QueryWaitTsafeLatencyP99 | 等待 tSafe P99 延迟 | ms | ClusterId,NodeId |  |
| QuerySearchNqAvg | 搜索 NQ 平均值 | count | ClusterId,NodeId |  |
| QuerySearchNqP99 | 搜索 NQ P99 值 | count | ClusterId,NodeId |  |
| QueryTimetickLagBehindNow | TimeTick 落后当前时间延迟 | ms | ClusterId,NodeId |  |
| QueryDmlVirtualChannelNum | DML 虚拟通道数量 | count | ClusterId,NodeId |  |
| QueryConsumedMessageCountPerSecond | 每秒消费消息数量 | count | ClusterId,NodeId |  |
| QueryProcessingInsertLatencyAvg | 插入处理平均延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingInsertLatencyP99 | 插入处理 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingDeleteLatencyAvg | 删除处理平均延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingDeleteLatencyP99 | 删除处理 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereSearchLatencyAvg | 搜索平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereSearchLatencyP99 | 搜索 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereRangeSearchLatencyAvg | Range Search 平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereRangeSearchLatencyP99 | Range Search P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereAnnIteratorInitLatencyAvg | ANN Iterator 初始化平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereAnnIteratorInitLatencyP99 | ANN Iterator 初始化 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereSearchCountPerSecond | 每秒搜索次数 | count/s | ClusterId,NodeId |  |
| KnowhereRangeSearchCountPerSecond | 每秒 Range Search 次数 | count/s | ClusterId,NodeId |  |
| KnowhereSearchTopkAvg | 搜索 TopK 平均值 | count | ClusterId,NodeId |  |
| KnowhereSearchTopkP99 | 搜索 TopK P99 值 | count | ClusterId,NodeId |  |
| SearchResourceUtil | 搜索资源水位(QueryNode/StreamingNode) | % | ClusterId,NodeId |  |
| MutationResourceUtil | 写入资源水位(DataNode/StreamingNode) | % | ClusterId,NodeId |  |
| CPUUsage | CPU 使用率 | % | ClusterId,NodeId |  |
| CPUCoresUsed | CPU 使用核数 | cores | ClusterId,NodeId |  |
| GoroutinesCount | Goroutine 数量 | count | ClusterId,NodeId |  |
| OSThreadsCount | OS 线程数量 | count | ClusterId,NodeId |  |
| ProcessOpenedFds | 进程打开文件描述符数量 | count | ClusterId,NodeId |  |
| MemoryUsage | 内存使用率 | % | ClusterId,NodeId |  |
| MemoryUsedBytes | 内存使用量 | bytes | ClusterId,NodeId |  |
| HeapAllocatedMemoryBytes | Go 堆已分配内存 | bytes | ClusterId,NodeId |  |
| GCMaxDurationSeconds | GC 最大暂停时间 | ms | ClusterId,NodeId |  |
| NextGCBytes | 下次 GC 触发内存阈值 | bytes | ClusterId,NodeId |  |
| AllocatedHeapObjects | 已分配堆对象数量 | count | ClusterId,NodeId |  |
| MemoryFreePerSecond | 内存释放速率 | count/s | ClusterId,NodeId |  |
| MemoryMallocsPerSecond | 内存分配速率 | count/s | ClusterId,NodeId |  |
| HeapIdleBytes | Go 堆空闲内存 | bytes | ClusterId,NodeId |  |
| MemoryAllocatedBytesPerSecond | 内存分配速率（字节） | bytes/s | ClusterId,NodeId |  |
| HeapReleasedBytes | Go 堆已释放内存 | bytes | ClusterId,NodeId |  |
| HeapInUseBytes | Go 堆使用内存 | bytes | ClusterId,NodeId |  |

## Milvus查询节点（MilvusQuery）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| QueryCollectionLoadedNum | 已加载 Collection 数量 | count | ClusterId,NodeId |  |
| QueryPartitionLoadedNum | 已加载 Partition 数量 | count | ClusterId,NodeId |  |
| QuerySegmentLoadedNum | 已加载 Segment 数量 | count | ClusterId,NodeId |  |
| QueryTimetickLagBehindNow | TimeTick 落后当前时间延迟 | ms | ClusterId,NodeId |  |
| QueryDmlVirtualChannelNum | DML 虚拟通道数量 | count | ClusterId,NodeId |  |
| QueryConsumedMessageCountPerSecond | 每秒消费消息数量 | ms | ClusterId,NodeId |  |
| QueryProcessingInsertLatencyAvg | 插入处理平均延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingInsertLatencyP99 | 插入处理 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingDeleteLatencyAvg | 删除处理平均延迟 | ms | ClusterId,NodeId |  |
| QueryProcessingDeleteLatencyP99 | 删除处理 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryableEntitySealedNum | 可查询 Sealed Entity 数量 | count | ClusterId,NodeId |  |
| QuerySearchRequestSuccess | 搜索成功请求数 | count | ClusterId,NodeId |  |
| QuerySearchRequestFail | 搜索失败请求数 | count | ClusterId,NodeId |  |
| QueryQueryRequestSuccess | 查询成功请求数 | count | ClusterId,NodeId |  |
| QueryQueryRequestFail | 查询失败请求数 | count | ClusterId,NodeId |  |
| QuerySearchSegmentLatencyAvg | Segment 搜索平均延迟 | ms | ClusterId,NodeId |  |
| QuerySearchSegmentLatencyP99 | Segment 搜索 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryNodeQuerySegmentLatencyAvg | Segment 查询平均延迟 | ms | ClusterId,NodeId |  |
| QueryNodeQuerySegmentLatencyP99 | Segment 查询 P99 延迟 | ms | ClusterId,NodeId |  |
| QuerySearchLatencyAvg | 搜索请求平均延迟 | ms | ClusterId,NodeId |  |
| QuerySearchLatencyP99 | 搜索请求 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryQueryLatencyAvg | 查询请求平均延迟 | ms | ClusterId,NodeId |  |
| QueryQueryLatencyP99 | 查询请求 P99 延迟 | ms | ClusterId,NodeId |  |
| QuerySearchInQueueLatencyAvg | 搜索排队平均延迟 | ms | ClusterId,NodeId |  |
| QuerySearchInQueueLatencyP99 | 搜索排队 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryQueryInQueueLatencyAvg | 查询排队平均延迟 | ms | ClusterId,NodeId |  |
| QueryQueryInQueueLatencyP99 | 查询排队 P99 延迟 | ms | ClusterId,NodeId |  |
| QuerySegcoreRequestLatencyAvg | Segcore 请求平均延迟 | ms | ClusterId,NodeId |  |
| QuerySegcoreRequestLatencyP99 | Segcore 请求 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryNodeLoadSegmentLatencyAvg | Segment 加载平均延迟 | ms | ClusterId,NodeId |  |
| QueryNodeLoadSegmentLatencyP99 | Segment 加载 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryNodeSearchReduceLatencyAvg | 搜索归约平均延迟 | ms | ClusterId,NodeId |  |
| QueryNodeSearchReduceLatencyP99 | 搜索归约 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryQueryReduceLatencyAvg | 查询归约平均延迟 | ms | ClusterId,NodeId |  |
| QueryQueryReduceLatencyP99 | 查询归约 P99 延迟 | ms | ClusterId,NodeId |  |
| QueryReadyReadTaskLength | 就绪读任务长度 | count | ClusterId,NodeId |  |
| QueryNodeUnsolvedReadTaskLength | 未完成读任务长度 | count | ClusterId,NodeId |  |
| QueryWaitTsafeLatencyAvg | 等待 tSafe 平均延迟 | ms | ClusterId,NodeId |  |
| QueryWaitTsafeLatencyP99 | 等待 tSafe P99 延迟 | ms | ClusterId,NodeId |  |
| QueryFlowgraphNum | Flowgraph 数量 | count | ClusterId,NodeId |  |
| QueryParallelReadTaskNum | 并行读任务数量 | count | ClusterId,NodeId |  |
| QuerySearchNqAvg | 搜索 NQ 平均值 | count | ClusterId,NodeId |  |
| QuerySearchNqP99 | 搜索 NQ P99 值 | count | ClusterId,NodeId |  |
| QuerySearchGroupNqAvg | 搜索分组 NQ 平均值 | count | ClusterId,NodeId |  |
| QuerySearchGroupNqP99 | 搜索分组 NQ P99 值 | count | ClusterId,NodeId |  |
| QuerySearchGroupSizeAvg | 搜索分组大小平均值 | count | ClusterId,NodeId |  |
| QuerySearchGroupSizeP99 | 搜索分组大小 P99 值 | count | ClusterId,NodeId |  |
| QueryEvictedReadRequestsCountPerSecond | 每秒淘汰读请求数 | count/s | ClusterId,NodeId |  |
| QuerySearchTopkAvg | 搜索 TopK 平均值 | count | ClusterId,NodeId |  |
| QuerySearchTopkP99 | 搜索 TopK P99 值 | count | ClusterId,NodeId |  |
| KnowhereSearchLatencyAvg | 搜索平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereSearchLatencyP99 | 搜索 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereRangeSearchLatencyAvg | Range Search 平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereRangeSearchLatencyP99 | Range Search P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereLoadLatencyAvg | 索引加载平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereLoadLatencyP99 | 索引加载 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereAnnIteratorInitLatencyAvg | ANN Iterator 初始化平均延迟 | ms | ClusterId,NodeId |  |
| KnowhereAnnIteratorInitLatencyP99 | ANN Iterator 初始化 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereSearchCountPerSecond | 每秒搜索次数 | count/s | ClusterId,NodeId |  |
| KnowhereRangeSearchCountPerSecond | 每秒 Range Search 次数 | count/s | ClusterId,NodeId |  |
| KnowhereSearchTopkAvg | 搜索 TopK 平均值 | count | ClusterId,NodeId |  |
| KnowhereSearchTopkP99 | 搜索 TopK P99 值 | count | ClusterId,NodeId |  |
| SearchResourceUtil | 搜索资源水位(QueryNode/StreamingNode) | % | ClusterId,NodeId |  |
| CPUUsage | CPU 使用率 | % | ClusterId,NodeId |  |
| CPUCoresUsed | CPU 使用核数 | cores | ClusterId,NodeId |  |
| GoroutinesCount | Goroutine 数量 | count | ClusterId,NodeId |  |
| OSThreadsCount | OS 线程数量 | count | ClusterId,NodeId |  |
| ProcessOpenedFds | 进程打开文件描述符数量 | count | ClusterId,NodeId |  |
| MemoryUsage | 内存使用率 | % | ClusterId,NodeId |  |
| MemoryUsedBytes | 内存使用量 | bytes | ClusterId,NodeId |  |
| HeapAllocatedMemoryBytes | Go 堆已分配内存 | bytes | ClusterId,NodeId |  |
| GCMaxDurationSeconds | GC 最大暂停时间 | ms | ClusterId,NodeId |  |
| NextGCBytes | 下次 GC 触发内存阈值 | bytes | ClusterId,NodeId |  |
| AllocatedHeapObjects | 已分配堆对象数量 | count | ClusterId,NodeId |  |
| MemoryFreePerSecond | 内存释放速率 | count/s | ClusterId,NodeId |  |
| MemoryMallocsPerSecond | 内存分配速率 | count/s | ClusterId,NodeId |  |
| HeapIdleBytes | Go 堆空闲内存 | bytes | ClusterId,NodeId |  |
| MemoryAllocatedBytesPerSecond | 内存分配速率（字节） | bytes/s | ClusterId,NodeId |  |
| HeapReleasedBytes | Go 堆已释放内存 | bytes | ClusterId,NodeId |  |
| HeapInUseBytes | Go 堆使用内存 | bytes | ClusterId,NodeId |  |

## Milvus数据节点（MilvusData）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| DataFlushOperateCountPerSecond | 每秒 Flush 操作次数 | count/s | ClusterId,NodeId |  |
| DataFlowgraphSuccessNum | Flowgraph 数量 | count | ClusterId,NodeId |  |
| DataConsumedMessageInsert | 每秒消费插入消息数 | count/s | ClusterId,NodeId |  |
| DataConsumedMessageAll | 每秒消费全部消息数 | count/s | ClusterId,NodeId |  |
| DataTimetickLagBehindNowMin | TimeTick 落后当前时间最小值 | ms | ClusterId,NodeId |  |
| DataTimetickLagBehindNowMax | TimeTick 落后当前时间最大值 | ms | ClusterId,NodeId |  |
| DataTimetickLagBehindNowAvg | TimeTick 落后当前时间平均值 | ms | ClusterId,NodeId |  |
| DataMsgRowsConsumedInsertRate | 每秒消费插入消息行数 | count/s | ClusterId,NodeId |  |
| DataCompactionLatencyAvg | Compaction 平均延迟 | ms | ClusterId,NodeId |  |
| DataCompactionLatencyP99 | Compaction P99 延迟 | ms | ClusterId,NodeId |  |
| DataNodeAutoFlushCountPerSecond | 每秒 AutoFlush 操作次数 | count/s | ClusterId,NodeId |  |
| DataNodeFlushDataBytesPerSecond | 每秒 Flush 数据量 | bytes/s | ClusterId,NodeId |  |
| DataNodeSaveDataLatencyAvg | 数据保存平均延迟 | ms | ClusterId,NodeId |  |
| DataNodeSaveDataLatencyP99 | 数据保存 P99 延迟 | ms | ClusterId,NodeId |  |
| DataTotalOfInflightConsumeBody | Inflight Consume Body 总数 | count | ClusterId,NodeId |  |
| DataMsgQueueConsumerNum | 消息队列消费者数量 | count | ClusterId,NodeId |  |
| DataConsumeBytesLatencyMsAvg | 消费字节平均延迟 | ms | ClusterId,NodeId |  |
| DataConsumeBytesLatencyMsP99 | 消费字节 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereBuildIndexLatencyP99 | 构建索引 P99 延迟 | ms | ClusterId,NodeId |  |
| KnowhereBuildIndexCountPerSecond | 每秒构建索引次数 | count/s | ClusterId,NodeId |  |
| MutationResourceUtil | 写入资源水位(DataNode/StreamingNode) | % | ClusterId,NodeId |  |
| CPUUsage | CPU 使用率 | % | ClusterId,NodeId |  |
| CPUCoresUsed | CPU 使用核数 | cores | ClusterId,NodeId |  |
| GoroutinesCount | Goroutine 数量 | count | ClusterId,NodeId |  |
| OSThreadsCount | OS 线程数量 | count | ClusterId,NodeId |  |
| ProcessOpenedFds | 进程打开文件描述符数量 | count | ClusterId,NodeId |  |
| MemoryUsage | 内存使用率 | % | ClusterId,NodeId |  |
| MemoryUsedBytes | 内存使用量 | bytes | ClusterId,NodeId |  |
| HeapAllocatedMemoryBytes | Go 堆已分配内存 | bytes | ClusterId,NodeId |  |
| GCMaxDurationSeconds | GC 最大暂停时间 | ms | ClusterId,NodeId |  |
| NextGCBytes | 下次 GC 触发内存阈值 | bytes | ClusterId,NodeId |  |
| AllocatedHeapObjects | 已分配堆对象数量 | count | ClusterId,NodeId |  |
| MemoryFreePerSecond | 内存释放速率 | count/s | ClusterId,NodeId |  |
| MemoryMallocsPerSecond | 内存分配速率 | count/s | ClusterId,NodeId |  |
| HeapIdleBytes | Go 堆空闲内存 | bytes | ClusterId,NodeId |  |
| MemoryAllocatedBytesPerSecond | 内存分配速率（字节） | bytes/s | ClusterId,NodeId |  |
| HeapReleasedBytes | Go 堆已释放内存 | bytes | ClusterId,NodeId |  |
| HeapInUseBytes | Go 堆使用内存 | bytes | ClusterId,NodeId |  |

## Milvus协调节点（MilvusCoord）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsage | CPU 使用率 | % | ClusterId,NodeId |  |
| CPUCoresUsed | CPU 使用核数 | cores | ClusterId,NodeId |  |
| GoroutinesCount | Goroutine 数量 | count | ClusterId,NodeId |  |
| OSThreadsCount | OS 线程数量 | count | ClusterId,NodeId |  |
| ProcessOpenedFds | 进程打开文件描述符数量 | count | ClusterId,NodeId |  |
| MemoryUsage | 内存使用率 | % | ClusterId,NodeId |  |
| MemoryUsedBytes | 内存使用量 | bytes | ClusterId,NodeId |  |
| HeapAllocatedMemoryBytes | Go 堆已分配内存 | bytes | ClusterId,NodeId |  |
| GCMaxDurationSeconds | GC 最大暂停时间 | ms | ClusterId,NodeId |  |
| NextGCBytes | 下次 GC 触发内存阈值 | bytes | ClusterId,NodeId |  |
| AllocatedHeapObjects | 已分配堆对象数量 | count | ClusterId,NodeId |  |
| MemoryFreePerSecond | 内存释放速率 | count/s | ClusterId,NodeId |  |
| MemoryMallocsPerSecond | 内存分配速率 | count/s | ClusterId,NodeId |  |
| HeapIdleBytes | Go 堆空闲内存 | bytes | ClusterId,NodeId |  |
| MemoryAllocatedBytesPerSecond | 内存分配速率（字节） | bytes/s | ClusterId,NodeId |  |
| HeapReleasedBytes | Go 堆已释放内存 | bytes | ClusterId,NodeId |  |
| HeapInUseBytes | Go 堆使用内存 | bytes | ClusterId,NodeId |  |

## Milvus集群（MilvusCluster）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| QueryCoordCollectionLoadedNum | 已加载 Collection 数量 | count | ClusterId |  |
| QuerycoordTaskNum | QueryCoord 任务数量 | count | ClusterId |  |
| QuerycoordQueryNodeNum | QueryNode 节点数量 | count | ClusterId |  |
| QuerycoordSegmentNumOnStoppingNode | 停止节点上的 Segment 数量 | count | ClusterId |  |
| QuerycoordChannelNumOnStoppingNode | 停止节点上的 Channel 数量 | count | ClusterId |  |
| DataCoordStoredRowsCount | 已存储行数 | count | ClusterId |  |
| DataCoordStoredRowsCountPerSecond | 每秒存储行数 | count/s | ClusterId |  |
| DataCoordSegmentFlushedCount | Flushed Segment 数量 | count | ClusterId |  |
| DataCoordSegmentDroppedCount | Dropped Segment 数量 | count | ClusterId |  |
| DataCoordSegmentGrowingCount | Growing Segment 数量 | count | ClusterId |  |
| DataCoordStoredBinlogSize | 已存储 Binlog 大小 | bytes | ClusterId |  |
| RootCoordTimestampSaved | 已保存时间戳 | 无 | ClusterId |  |
| RootcoordTimestamp | 当前时间戳 | 无 | ClusterId |  |
| RootCoordDmlChannelNum | DML Channel 数量 | count | ClusterId |  |
| RootCoordIdAllocPerSecond | 每秒 ID 分配数 | count | ClusterId |  |
| RootCoordPartitionNum | Partition 数量 | count | ClusterId |  |
| RootcoordTimeTickDelay | TimeTick 延迟 | ms | ClusterId |  |
| RootcoordCredentialNum | Credential 数量 | count | ClusterId |  |
| RootcoordMsgstreamNum | Msgstream 数量 | count | ClusterId |  |
| CollectionCount | Collection数量 | count | ClusterId |  |
| EntityCount | Entity数量 | count | ClusterId |  |
| QuerycoordLoadFailRequestCountPerSecond | 每秒 Load 失败请求数 | count/s | ClusterId |  |
| QuerycoordLoadSuccessRequestCountPerSecond | 每秒 Load 成功请求数 | count/s | ClusterId |  |
| QuerycoordLoadTotalRequestCountPerSecond | 每秒 Load 请求总数 | count/s | ClusterId |  |
| DataCoordIndexRequestCountPerSecond | 每秒索引请求数 | count/s | ClusterId |  |
| DataCoordIndexTaskCountPerSecond | 每秒索引任务数 | count/s | ClusterId |  |
| RootCoordProducedTimetickTimeTakenAvg | 产生 TimeTick 平均耗时 | ms | ClusterId |  |
| RootCoordProducedTimetickTimeTakenP99 | 产生 TimeTick P99 耗时 | ms | ClusterId |  |
| RootcoordDdlRequestLatencyAvg | DDL 请求平均延迟 | ms | ClusterId |  |
| RootcoordDdlRequestLatencyP99 | DDL 请求 P99 延迟 | ms | ClusterId |  |
| RootcoordDdlRequestCountPerSecond | 每秒 DDL 请求数 | count/s | ClusterId |  |
| CPUCoresUsedTotal | CPU 使用核数总计 | count | ClusterId |  |
| MemoryUsedBytesTotal | 内存使用总量 | bytes | ClusterId |  |
| GoroutinesCountTotal | Goroutine 总数 | count | ClusterId |  |
| SuccessRequestCountTotal1m | 最近1分钟请求成功数 | count | ClusterId |  |
| FailRequestCountTotal1m | 最近1分钟请求失败数 | count | ClusterId |  |

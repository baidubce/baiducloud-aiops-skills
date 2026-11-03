# 云原生数据库 GaiaDB

云原生数据库 GaiaDB 包含3种监控对象类型，分别是：集群监控（Cluster）、节点监控（Instance）、代理监控（Interface），各个类型包含的监控指标列表如下：

## 集群监控（Cluster）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| BinlogUsage | 本地Binlog使用量 | MB | ClusterId |  |
| DataSpaceUsage | 数据空间使用量 | MB | ClusterId |  |
| ErrlogUsage | 错误日志使用量 | MB | ClusterId |  |
| RedologUsage | 本地Redolog使用量 | MB | ClusterId |  |
| SlowlogUsage | 慢日志使用量 | MB | ClusterId |  |
| TempSpaceUsage | 临时空间使用量 | MB | ClusterId |  |

## 节点监控（Instance）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| AfterMasterMs | 主从延迟(毫秒) | ms | ClusterId,InstanceShortId |  |
| CPUUsagePercent | CPU占用率 | % | ClusterId,InstanceShortId |  |
| DeleteCountPerSecond | 每秒DELETE数 | 次 | ClusterId,InstanceShortId |  |
| InsertCountPerSecond | 每秒INSERT数 | 次 | ClusterId,InstanceShortId |  |
| InstanceNetWorkIn | 每秒输入流量 | KB | ClusterId,InstanceShortId |  |
| InstanceNetWorkOut | 每秒输出流量 | KB | ClusterId,InstanceShortId |  |
| MemUsagePercent | 内存使用率 | % | ClusterId,InstanceShortId |  |
| MysqlSlowQueriesPt | 慢查询次数 | 次/秒 | ClusterId,InstanceShortId |  |
| ReadOpCountPerSecond | 每秒读请求数 | 次 | ClusterId,InstanceShortId |  |
| ThreadConnectedCount | 总连接数 | 个 | ClusterId,InstanceShortId |  |
| ThreadRunningCount | 活跃连接数 | 个 | ClusterId,InstanceShortId |  |
| TPS | 每秒事务数 | 次 | ClusterId,InstanceShortId |  |
| TPS\_ALL | 每秒事务数(含隐式提交) | 次 | ClusterId,InstanceShortId |  |
| UpdateCountPerSecond | 每秒UPDATE数 | 次 | ClusterId,InstanceShortId |  |
| WriteOpCountPerSecond | 每秒写请求数 | 次 | ClusterId,InstanceShortId |  |

## 代理监控（Interface）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| CPUUsagePercent\_I | CPU利用率 | % | ClusterId,InterfaceId |  |
| ProxyBandwidth\_I | 每秒吞吐流量 | Byte/秒 | ClusterId,InterfaceId |  |
| ProxyDmlAvgtime\_I | 每秒吞吐流量 | ms | ClusterId,InterfaceId |  |
| ProxyDmlPerSecond\_I | SQL访问次数 | 次 | ClusterId,InterfaceId |  |
| QPS\_I | 每秒请求数 | 个 | ClusterId,InterfaceId |  |
| ThreadsConnected\_I | 当前连接数 | 个 | ClusterId,InterfaceId |  |

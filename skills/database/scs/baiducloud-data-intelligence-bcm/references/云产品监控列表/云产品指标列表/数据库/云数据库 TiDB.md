# 云数据库 TiDB

云数据库 TiDB 包含TIDB节点（TIDBNode）、TiKV节点（TiKVNode）、PD节点（PDNode））3种监控对象类型，各监控对象类型包含的监控指标列表如下：

## TIDB节点（TIDBNode）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| TiDBCPUUsagePercent | TiDB CPU使用率 | % | NodeId, InstanceId |  |
| TiDBMemoryUsage | TiDB内存使用 | Bytes | NodeId, InstanceId |  |
| TiDBInsertRow | INSERT 影响行数 | 个 | NodeId, InstanceId |  |
| TiDBUpdateRow | UPDATE 影响行数 | 个 | NodeId, InstanceId |  |
| TiDBReplaceRow | REPLACE 影响行数 | 个 | NodeId, InstanceId |  |
| TiDBInsertCom | INSERT 命令执行次数 | 个 | NodeId, InstanceId |  |
| TiDBUpdateCom | UPDATE 命令执行次数 | 个 | NodeId, InstanceId |  |
| TiDBSelectCom | SELECT 命令执行次数 | 个 | NodeId, InstanceId |  |
| TiDBSlowQuery | 慢查询数量 | 个 | NodeId, InstanceId |  |

## TiKV节点（TiKVNode）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| TiKVCPUUsagePercent | TiKV CPU使用率 | % | NodeId, InstanceId |  |
| TiKVMemoryUsage | TiKV 内存使用 | Bytes | NodeId, InstanceId |  |
| TiKVStoreSize | TiKV 已用存储 | Bytes | NodeId, InstanceId |  |
| TiKVAvailableSize | TiKV 可用存储 | Bytes | NodeId, InstanceId |  |
| TiKVCapacitySize | TiKV 总存储 | Bytes | NodeId, InstanceId |  |

## PD节点（PDNode）

| 指标英文名称（metric name） | 指标中文名称 | 单位 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| PDCPUUsagePercent | PD CPU使用率 | % | NodeId, InstanceId |  |
| PDMemoryUsage | PD内存使用 | Bytes | NodeId, InstanceId |  |

# 数据传输服务 DTS

数据传输服务（DTS）只包含实例监控（Instance）1种监控对象类型，实例监控包含的监控指标列表如下：

## 实例监控（Instance）

| 指标英文名称（Metric name） | 指标中文名称 | 单位 | 维度 |
| --- | --- | --- | --- |
| dtsDelay | 增量同步延迟 | s | InstanceId |
| dtsFlow | 每秒传输数据量 | Bytes/s | InstanceId |
| dtsStatus | 任务状态 | 0表示正常，1表示非正常 | InstanceId |
| dtsTps | 每秒传输行数 | 行/s | InstanceId |

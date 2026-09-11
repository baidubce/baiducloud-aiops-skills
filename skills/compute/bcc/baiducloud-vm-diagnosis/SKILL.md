---
name: baiducloud-vm-diagnosis
description: 从虚机内部诊断 Linux 虚拟机的性能、稳定性与操作系统健康问题。适用于排查内存占用过高或 OOM、Java/JVM 内存、socket 或 TCP 内存压力、丢包、网络抖动、磁盘 IO 打满或 IO 缓慢、负载过高、CPU 调度延迟、文件系统或 fstab 异常、fd 耗尽、大页内存压力、SSH/cloud-init/NTP 健康状况，以及需要搭建类似 SysOM 的虚机诊断流程等场景。输出结构化的 agent envelope，不会自动执行修复操作。
---

# 虚机诊断

## 概述

排查 Linux 虚机症状时，优先使用本 skill 内置的只读采集器作为第一诊断来源。它会输出 SysOM 风格的 JSON envelope，包含 `ok`、`command`、`agent.summary`、`agent.findings[]` 和 `agent.next_steps[]` 字段。

该脚本面向被诊断的目标 Linux 虚机设计。如果当前机器不是待诊断的虚机，请通过可用的远程 shell、SSH 或 devbox 通道，把 `scripts/vm_diagnose.py` 拷贝到目标机上执行；不要把本地 macOS 主机误当作目标机。

## 快速选路

按用户描述的症状，选择最小可用的命令执行：

```bash
python3 scripts/vm_diagnose.py classify
python3 scripts/vm_diagnose.py memory
python3 scripts/vm_diagnose.py java
python3 scripts/vm_diagnose.py network --target <host-or-ip>
python3 scripts/vm_diagnose.py io --interval 2
python3 scripts/vm_diagnose.py load --interval 2
python3 scripts/vm_diagnose.py health
```

当症状描述模糊、跨多个领域，或用户只说"慢/卡住/不稳定"时，使用 `classify`。当用户已明确指出内存、Java、网络、IO 或负载问题时，直接使用对应的专项命令。

## 工作流程

1. 将症状归类到内存、Java 内存、网络、IO、负载/调度或操作系统健康这几类中。
2. 在目标 Linux 虚机上执行匹配的采集命令。
3. 默认只读取 envelope 中的这几个字段：`ok`、`error`、`command` 和 `agent`。
4. 依据 `agent.summary`、`agent.findings[].detail/category` 和 `agent.next_steps[]` 作答。
5. 只有当关键实体信息缺失、且 envelope 推荐了能补齐该信息的命令时，才追加执行一次专项命令。

诊断过程中不要执行修复操作。除非用户在看到诊断结果后明确要求修复，否则应避免执行杀进程、清理缓存、写入 sysctl 参数、修改 cgroup、变更 fstab、重启服务或改动网络状态等命令。

## 输出约定

面向用户的回答应以 `agent` 字段为准：

```json
{
  "ok": true,
  "command": "vm-diagnose memory",
  "agent": {
    "status": "warning",
    "summary": "Concise diagnosis summary.",
    "findings": [
      {
        "severity": "high",
        "title": "Short finding title",
        "detail": "Root cause, key entities, and evidence summary.",
        "category": "root_cause"
      }
    ],
    "next_steps": [
      {
        "kind": "command",
        "label": "Run focused follow-up",
        "command": "python3 scripts/vm_diagnose.py io --interval 2",
        "reason": "The missing entity this command can fill."
      }
    ]
  }
}
```

一条 finding 需要同时给出问题对象、归属方或作用范围、证据，以及安全的处置目标，才算信息完整、可用于作答。例如：内存问题需给出 PID/服务/cgroup，网络问题需给出网卡/路径或流量范围，IO 问题需给出块设备与时延，负载问题需给出 runnable/blocked 任务压力，JVM 类症状需给出 Java PID 与堆内存/RSS 上下文。

## 参考文档

- 需要选择后续排查命令，或判断当前结论是否完整时，阅读 `references/domain-routing.md`。
- 虚机出现 GPU/RDMA 相关症状，或需要复用可选的 GPU/RDMA 诊断工具链时，阅读 `references/gpu-rdma-resources.md`。

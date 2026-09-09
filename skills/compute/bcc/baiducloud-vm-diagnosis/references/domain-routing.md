# Domain Routing

Use this reference after the skill triggers and before running follow-up commands.

## First Command

| User symptom | First command |
| --- | --- |
| Vague slow, stuck, unstable, "not sure what happened" | `python3 scripts/vm_diagnose.py classify` |
| High memory, low available memory, cache, slab, socket memory, OOM, oom-killer | `python3 scripts/vm_diagnose.py memory` |
| Java heap, JVM RSS, GC, Java OOM | `python3 scripts/vm_diagnose.py java` |
| Packet loss, retransmits, dropped packets, timeout | `python3 scripts/vm_diagnose.py network --target <host-or-ip>` when a peer is known; otherwise `python3 scripts/vm_diagnose.py network` |
| Latency jitter or intermittent connectivity | `python3 scripts/vm_diagnose.py network --target <host-or-ip>` |
| Slow disk, high iowait, IO hang, blocked writes, disk full | `python3 scripts/vm_diagnose.py io --interval 2` |
| High load, runqueue, scheduling delay, tasks stuck but not clearly IO | `python3 scripts/vm_diagnose.py load --interval 2` |
| OS health, fstab, fd exhaustion, nofile, hugepages, SSH, cloud-init, NTP | `python3 scripts/vm_diagnose.py health` |

## Completion Signals

A result is answer-ready when a root-cause finding names the relevant entity and evidence:

| Domain | Required visible entities |
| --- | --- |
| Memory | pressure source, current magnitude, top holder or cgroup when visible, OOM evidence if historical |
| Java | Java PID, RSS, visible heap limit or missing limit, relation to VM memory pressure |
| Network | interface/path or target, drop/retrans/jitter evidence, scope of counter or live ping |
| IO | block device or filesystem, utilization or await, disk/full/inode or kernel error evidence |
| Load | load-to-CPU ratio, CPU/iowait/steal split, PSI or blocked task evidence, top CPU holder when visible |
| Health | config object, exact file/service/sysctl, and why it is unsafe or degraded |

Run only one focused follow-up when the current envelope explicitly lacks one of these entities and `agent.next_steps[]` names a command that can fill it.

## Answer Discipline

- Prefer `category=root_cause`, then highest severity, then best match to the user symptom.
- Preserve evidence qualifiers such as cumulative counters, since-boot counters, live sampling interval, or last-24-hour logs.
- Do not turn a closed diagnosis into a generic command checklist.
- Do not run repair commands during diagnosis.
- If running on a non-Linux local machine, ask for or use access to the target VM rather than diagnosing the local host.

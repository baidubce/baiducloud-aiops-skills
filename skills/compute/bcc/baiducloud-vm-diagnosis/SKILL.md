---
name: baiducloud-vm-diagnosis
description: Diagnose Linux virtual machine performance, stability, and OS health issues from inside the guest. Use when troubleshooting high memory usage or OOM, Java/JVM memory, socket or TCP memory pressure, packet loss, network jitter, disk IO saturation or slow IO, high load, CPU scheduling delay, filesystem or fstab problems, fd exhaustion, hugepage pressure, SSH/cloud-init/NTP health, or when building a SysOM-like VM diagnosis workflow. Produces structured agent envelopes and does not apply fixes automatically.
---

# VM Diagnosis

## Overview

Use the bundled read-only collector as the first diagnostic source for Linux VM symptoms. It emits a SysOM-style JSON envelope with `ok`, `command`, `agent.summary`, `agent.findings[]`, and `agent.next_steps[]`.

The script is designed for the target Linux guest. If the current machine is not the VM being diagnosed, copy or run `scripts/vm_diagnose.py` on the target through the available remote shell, SSH, or devbox path; do not interpret the local macOS host as the target.

## Quick Route

Run the smallest command that matches the user's symptom:

```bash
python3 scripts/vm_diagnose.py classify
python3 scripts/vm_diagnose.py memory
python3 scripts/vm_diagnose.py java
python3 scripts/vm_diagnose.py network --target <host-or-ip>
python3 scripts/vm_diagnose.py io --interval 2
python3 scripts/vm_diagnose.py load --interval 2
python3 scripts/vm_diagnose.py health
```

Use `classify` when the symptom is vague, cross-domain, or just "slow/stuck/unstable". Use a focused command when the user already names memory, Java, network, IO, or load.

## Workflow

1. Classify the symptom into memory, Java memory, network, IO, load/scheduling, or OS health.
2. Run the matching collector command on the Linux guest.
3. Read only the envelope fields by default: `ok`, `error`, `command`, and `agent`.
4. Answer from `agent.summary`, `agent.findings[].detail/category`, and `agent.next_steps[]`.
5. Run one focused follow-up only when a required entity is missing and the envelope recommends a command that can fill it.

Do not run remediation during diagnosis. Avoid commands that kill processes, clear cache, write sysctl values, edit cgroups, change fstab, restart services, or modify network state unless the user explicitly asks for repair after seeing the diagnosis.

## Output Contract

Treat `agent` as the source of truth for the user-facing answer:

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

A finding is complete enough to answer when it names the material object, owner or scope, evidence, and safe action target. Examples: PID/service/cgroup for memory, interface/path or flow scope for network, block device and latency for IO, runnable/blocked task pressure for load, Java PID and heap/RSS context for JVM symptoms.

## References

- Read `references/domain-routing.md` when choosing follow-up commands or checking whether an answer is complete.
- Read `references/gpu-rdma-resources.md` when the VM has GPU/RDMA symptoms or when reusing an optional GPU/RDMA diagnostic toolchain.

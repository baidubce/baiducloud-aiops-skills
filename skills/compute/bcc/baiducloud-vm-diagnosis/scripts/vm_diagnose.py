#!/usr/bin/env python3
"""Read-only Linux VM diagnostics with a SysOM-style agent envelope."""

from __future__ import annotations

import argparse
import glob
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def read_text(path: str, max_bytes: Optional[int] = None) -> str:
    """Read a file as UTF-8 text."""
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes or 10_000_000)
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def read_first_line(path: str) -> str:
    """Read and return the first line."""
    text = read_text(path, 4096)
    return text.splitlines()[0].strip() if text else ""


def run_cmd(cmd: List[str], timeout: float = 5.0) -> Dict[str, Any]:
    """Run a command and capture its result."""
    if not shutil.which(cmd[0]):
        return {"ok": False, "rc": 127, "stdout": "", "stderr": f"{cmd[0]} not found"}
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "rc": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "rc": 124,
            "stdout": exc.stdout or "",
            "stderr": f"timeout after {timeout}s",
        }
    except Exception as exc:
        return {"ok": False, "rc": 1, "stdout": "", "stderr": str(exc)}


def now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def host_context() -> Dict[str, Any]:
    """Build a host metadata payload."""
    os_release = {}
    for line in read_text("/etc/os-release").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            os_release[k] = v.strip().strip('"')
    return {
        "hostname": socket.gethostname(),
        "timestamp": now_iso(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "os": os_release.get("PRETTY_NAME") or platform.platform(),
        "python": platform.python_version(),
    }


def has_procfs() -> bool:
    """Return whether the current host exposes procfs."""
    return os.path.isdir("/proc") and os.path.isfile("/proc/stat")


def procfs_required(command: str) -> Optional[Dict[str, Any]]:
    """Return an envelope when procfs is unavailable."""
    if has_procfs():
        return None
    return envelope(
        command,
        [
            finding(
                "high",
                "Target is not a Linux procfs environment",
                (
                    "This collector must run inside the target Linux VM. "
                    "/proc/stat is not available on the current host, so no VM diagnosis was performed."
                ),
                "root_cause",
            )
        ],
        [],
        {"platform": platform.platform()},
        ok=False,
        error={
            "code": "VmDiagnosis.ProcfsUnavailable",
            "message": "Run scripts/vm_diagnose.py on the target Linux guest.",
        },
    )


def finding(severity: str, title: str, detail: str, category: str = "observation") -> Dict[str, str]:
    """Build a finding record."""
    return {
        "severity": severity,
        "title": title,
        "detail": detail,
        "category": category,
    }


def next_step(label: str, command: str, reason: str) -> Dict[str, str]:
    """Build a follow-up step record."""
    return {"kind": "command", "label": label, "command": command, "reason": reason}


def status_from_findings(findings: List[Dict[str, str]]) -> str:
    """Derive the agent status from findings."""
    max_rank = max((SEVERITY_RANK.get(f.get("severity", "info"), 0) for f in findings), default=0)
    if max_rank >= 4:
        return "critical"
    if max_rank >= 3:
        return "error"
    if max_rank >= 1:
        return "warning"
    return "normal"


def summarize(command: str, findings: List[Dict[str, str]]) -> str:
    """Summarize findings for the report envelope."""
    if not findings:
        return f"{command} did not find an obvious issue in the collected signals."
    roots = [f for f in findings if f.get("category") == "root_cause"]
    selected = sorted(roots or findings, key=lambda f: SEVERITY_RANK.get(f.get("severity", "info"), 0), reverse=True)[0]
    return f"{selected['title']}: {selected['detail']}"


def envelope(
    command: str,
    findings: List[Dict[str, str]],
    steps: Optional[List[Dict[str, str]]] = None,
    evidence: Optional[Dict[str, Any]] = None,
    ok: bool = True,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the final report envelope."""
    if not findings:
        findings = [finding("info", "No obvious issue found",
                            "Collected signals are within simple threshold checks.", "summary")]
    doc = {
        "ok": ok,
        "command": command,
        "target": host_context(),
        "agent": {
            "status": status_from_findings(findings),
            "summary": summarize(command, findings),
            "findings": findings,
            "next_steps": steps or [],
        },
    }
    if evidence is not None:
        doc["evidence"] = evidence
    if error is not None:
        doc["error"] = error
    return doc


def parse_meminfo() -> Dict[str, int]:
    """Parse /proc/meminfo into a dictionary."""
    out: Dict[str, int] = {}
    for line in read_text("/proc/meminfo").splitlines():
        parts = line.replace(":", "").split()
        if len(parts) >= 2 and parts[1].isdigit():
            out[parts[0]] = int(parts[1])
    return out


def human_kb(kb: float) -> str:
    """Format kilobytes using binary units."""
    units = ["KiB", "MiB", "GiB", "TiB"]
    value = float(kb)
    unit = units[0]
    for unit in units:
        if abs(value) < 1024 or unit == units[-1]:
            break
        value /= 1024
    return f"{value:.1f} {unit}"


def parse_proc_status(pid: str) -> Dict[str, str]:
    """Parse /proc/<pid>/status into a dictionary."""
    result: Dict[str, str] = {}
    for line in read_text(f"/proc/{pid}/status").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k] = v.strip()
    return result


def proc_cmdline(pid: str) -> str:
    """Read a process command line from /proc."""
    raw = read_text(f"/proc/{pid}/cmdline", 65536)
    cmd = raw.replace("\x00", " ").strip()
    return cmd or read_first_line(f"/proc/{pid}/comm") or pid


def proc_cgroup(pid: str) -> str:
    """Read a process cgroup from /proc."""
    lines = read_text(f"/proc/{pid}/cgroup").splitlines()
    if not lines:
        return ""
    return ";".join(line.split(":", 2)[-1] for line in lines[:3])


def top_processes_by_rss(limit: int = 8) -> List[Dict[str, Any]]:
    """Return processes sorted by RSS."""
    rows = []
    if not os.path.isdir("/proc"):
        return rows
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        st = parse_proc_status(pid)
        rss = parse_status_kb(st.get("VmRSS", "0 kB"))
        swap = parse_status_kb(st.get("VmSwap", "0 kB"))
        if rss <= 0 and swap <= 0:
            continue
        rows.append(
            {
                "pid": int(pid),
                "name": st.get("Name", ""),
                "rss_kb": rss,
                "swap_kb": swap,
                "cmdline": proc_cmdline(pid)[:220],
                "cgroup": proc_cgroup(pid)[:220],
            }
        )
    return sorted(rows, key=lambda x: x["rss_kb"], reverse=True)[:limit]


def parse_status_kb(value: str) -> int:
    """Parse a status value and convert it to KiB."""
    match = re.search(r"(\d+)", value or "")
    return int(match.group(1)) if match else 0


def parse_sockstat(path: str) -> Dict[str, Dict[str, int]]:
    """Parse a sockstat file into protocol counters."""
    result: Dict[str, Dict[str, int]] = {}
    for line in read_text(path).splitlines():
        if ":" not in line:
            continue
        proto, rest = line.split(":", 1)
        values: Dict[str, int] = {}
        parts = rest.split()
        for i in range(0, len(parts) - 1, 2):
            if re.fullmatch(r"-?\d+", parts[i + 1]):
                values[parts[i]] = int(parts[i + 1])
        result[proto.strip()] = values
    return result


def oom_log_lines() -> List[str]:
    """Collect recent OOM-related kernel log lines."""
    patterns = re.compile(r"(oom-killer|out of memory|memory cgroup out of memory|killed process)", re.I)
    lines: List[str] = []
    journal = run_cmd(["journalctl", "-k", "--since", "24 hours ago", "--no-pager", "-n", "2000"], timeout=6)
    if journal["stdout"]:
        lines.extend([x.strip() for x in journal["stdout"].splitlines() if patterns.search(x)])
    dmesg = run_cmd(["dmesg", "-T"], timeout=4)
    if dmesg["stdout"]:
        lines.extend([x.strip() for x in dmesg["stdout"].splitlines() if patterns.search(x)])
    dedup: List[str] = []
    seen = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            dedup.append(line)
    return dedup[-20:]


def cgroup_memory() -> Dict[str, Any]:
    """Collect cgroup memory metrics."""
    data: Dict[str, Any] = {}
    current = read_first_line("/sys/fs/cgroup/memory.current")
    maximum = read_first_line("/sys/fs/cgroup/memory.max")
    events = read_text("/sys/fs/cgroup/memory.events")
    if current:
        data["memory_current_bytes"] = int(current) if current.isdigit() else current
    if maximum:
        data["memory_max_bytes"] = int(maximum) if maximum.isdigit() else maximum
    if events:
        parsed = {}
        for line in events.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].isdigit():
                parsed[parts[0]] = int(parts[1])
        data["memory_events"] = parsed
    v1_usage = read_first_line("/sys/fs/cgroup/memory/memory.usage_in_bytes")
    v1_limit = read_first_line("/sys/fs/cgroup/memory/memory.limit_in_bytes")
    if v1_usage:
        data["memory_usage_bytes"] = int(v1_usage) if v1_usage.isdigit() else v1_usage
    if v1_limit:
        data["memory_limit_bytes"] = int(v1_limit) if v1_limit.isdigit() else v1_limit
    return data


def diagnose_memory(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the memory diagnosis."""
    unavailable = procfs_required("vm-diagnose memory")
    if unavailable:
        return unavailable
    mem = parse_meminfo()
    findings: List[Dict[str, str]] = []
    steps: List[Dict[str, str]] = []
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", mem.get("MemFree", 0))
    evidence: Dict[str, Any] = {
        "meminfo": {
            k: mem.get(k)
            for k in [
                "MemTotal",
                "MemAvailable",
                "MemFree",
                "Buffers",
                "Cached",
                "SwapTotal",
                "SwapFree",
                "Slab",
                "SReclaimable",
                "SUnreclaim",
            ]
            if k in mem
        },
        "top_rss": top_processes_by_rss(),
        "sockstat": parse_sockstat("/proc/net/sockstat"),
        "sockstat6": parse_sockstat("/proc/net/sockstat6"),
        "cgroup_memory": cgroup_memory(),
    }
    if total:
        available_pct = available * 100 / total
        used_pct = 100 - available_pct
        memory_summary = (
            f"MemAvailable is {human_kb(available)} of {human_kb(total)} "
            f"({available_pct:.1f}% available, {used_pct:.1f}% used)."
        )
        memory_headroom = (
            f"MemAvailable is {human_kb(available)} of {human_kb(total)} "
            f"({available_pct:.1f}% available)."
        )
        if available_pct < 5:
            findings.append(
                finding(
                    "critical",
                    "Available memory is critically low",
                    memory_summary,
                    "root_cause",
                )
            )
        elif available_pct < 10:
            findings.append(
                finding(
                    "high",
                    "Available memory is low",
                    memory_summary,
                    "root_cause",
                )
            )
        elif available_pct < 20:
            findings.append(
                finding(
                    "medium",
                    "Memory headroom is limited",
                    memory_headroom,
                )
            )
    swap_total = mem.get("SwapTotal", 0)
    if swap_total:
        swap_used = swap_total - mem.get("SwapFree", 0)
        swap_pct = swap_used * 100 / swap_total
        if swap_pct > 70:
            swap_message = (
                f"Swap usage is {human_kb(swap_used)} of {human_kb(swap_total)} "
                f"({swap_pct:.1f}%)."
            )
            findings.append(finding("high", "Swap usage is high", swap_message, "root_cause"))
        elif swap_pct > 20:
            swap_message = (
                f"Swap usage is {human_kb(swap_used)} of {human_kb(swap_total)} "
                f"({swap_pct:.1f}%)."
            )
            findings.append(finding("medium", "Swap is in use", swap_message))
    oom_lines = oom_log_lines()
    evidence["oom_log_matches"] = oom_lines
    if oom_lines:
        oom_message = (
            f"Kernel logs from the last 24 hours contain {len(oom_lines)} "
            f"OOM-related line(s); last evidence: {oom_lines[-1][:260]}"
        )
        findings.append(
            finding(
                "high",
                "Recent OOM evidence found",
                oom_message,
                "root_cause",
            )
        )
    top = evidence["top_rss"]
    if total and top:
        leader = top[0]
        rss_pct = leader["rss_kb"] * 100 / total
        if rss_pct > 40:
            leader_message = (
                f"PID {leader['pid']} ({leader['name']}) holds "
                f"{human_kb(leader['rss_kb'])} RSS ({rss_pct:.1f}% of memory); "
                f"command: {leader['cmdline']}"
            )
            findings.append(
                finding(
                    "high",
                    "One process dominates RSS",
                    leader_message,
                    "root_cause",
                )
            )
        elif rss_pct > 20:
            leader_message = (
                f"PID {leader['pid']} ({leader['name']}) holds "
                f"{human_kb(leader['rss_kb'])} RSS ({rss_pct:.1f}% of memory)."
            )
            findings.append(
                finding(
                    "medium",
                    "Largest RSS holder is significant",
                    leader_message,
                )
            )
        java_leaders = [p for p in top if "java" in (p.get("cmdline", "").lower() + p.get("name", "").lower())]
        if java_leaders:
            steps.append(
                next_step(
                    "Inspect Java memory",
                    "python3 scripts/vm_diagnose.py java",
                    "A Java process is among the largest RSS holders.",
                )
            )
    sock_tcp = evidence["sockstat"].get("TCP", {})
    tcp_mem_pages = sock_tcp.get("mem", 0)
    if total and tcp_mem_pages:
        tcp_mem_kb = tcp_mem_pages * (os.sysconf("SC_PAGE_SIZE") // 1024)
        tcp_pct = tcp_mem_kb * 100 / total
        if tcp_pct > 10:
            tcp_message = (
                f"TCP socket memory is about {human_kb(tcp_mem_kb)} "
                f"({tcp_pct:.1f}% of memory)."
            )
            findings.append(finding("high", "TCP socket memory is high", tcp_message, "root_cause"))
        elif tcp_pct > 5:
            tcp_message = (
                f"TCP socket memory is about {human_kb(tcp_mem_kb)} "
                f"({tcp_pct:.1f}% of memory)."
            )
            findings.append(finding("medium", "TCP socket memory is elevated", tcp_message))
            steps.append(
                next_step(
                    "Inspect network socket pressure",
                    "python3 scripts/vm_diagnose.py network",
                    "Socket memory is visible in the memory overview.",
                )
            )
    cg = evidence["cgroup_memory"]
    events = cg.get("memory_events", {})
    if isinstance(events, dict) and (events.get("oom_kill", 0) or events.get("oom", 0)):
        cgroup_message = (
            f"memory.events reports oom={events.get('oom', 0)} and "
            f"oom_kill={events.get('oom_kill', 0)}."
        )
        findings.append(finding("high", "Memory cgroup has OOM events", cgroup_message, "root_cause"))
    current = cg.get("memory_current_bytes") or cg.get("memory_usage_bytes")
    maximum = cg.get("memory_max_bytes") or cg.get("memory_limit_bytes")
    if isinstance(current, int) and isinstance(maximum, int) and maximum > 0 and maximum < 1 << 60:
        pct = current * 100 / maximum
        if pct > 90:
            limit_message = f"Cgroup memory is {current} of {maximum} bytes ({pct:.1f}%)."
            findings.append(finding("high", "Memory cgroup is near its limit", limit_message, "root_cause"))
    if not steps:
        steps.append(next_step("Run broad classifier", "python3 scripts/vm_diagnose.py classify",
                     "Check whether another domain better explains the symptom."))
    return envelope("vm-diagnose memory", findings, steps, evidence)


def parse_proc_net_protocols(path: str) -> Dict[str, Dict[str, int]]:
    """Parse proc net protocol counters."""
    result: Dict[str, Dict[str, int]] = {}
    last_header: Dict[str, List[str]] = {}
    for line in read_text(path).splitlines():
        if ":" not in line:
            continue
        proto, rest = line.split(":", 1)
        fields = rest.split()
        if not fields:
            continue
        if all(not re.fullmatch(r"-?\d+", x) for x in fields):
            last_header[proto] = fields
            continue
        header = last_header.get(proto)
        if header and len(header) == len(fields):
            result[proto] = {k: int(v) for k, v in zip(header, fields) if re.fullmatch(r"-?\d+", v)}
    return result


def interface_stats() -> List[Dict[str, Any]]:
    """Collect network interface statistics."""
    rows = []
    for path in glob.glob("/sys/class/net/*"):
        name = os.path.basename(path)
        if name == "lo":
            continue
        stats = {}
        for key in ["rx_dropped", "tx_dropped", "rx_errors", "tx_errors", "rx_packets", "tx_packets"]:
            value = read_first_line(os.path.join(path, "statistics", key))
            stats[key] = int(value) if value.isdigit() else 0
        speed = read_first_line(os.path.join(path, "speed"))
        rows.append(
            {
                "name": name,
                "operstate": read_first_line(os.path.join(path, "operstate")),
                "carrier": read_first_line(os.path.join(path, "carrier")),
                "speed_mbps": int(speed) if speed.isdigit() else None,
                **stats,
            }
        )
    return rows


def softnet_drops() -> int:
    """Return cumulative softnet drops."""
    total = 0
    for line in read_text("/proc/net/softnet_stat").splitlines():
        parts = line.split()
        if len(parts) > 1:
            try:
                total += int(parts[1], 16)
            except ValueError:
                pass
    return total


def qdisc_drops() -> Optional[int]:
    """Return cumulative qdisc drops."""
    tc = run_cmd(["tc", "-s", "qdisc", "show"], timeout=5)
    if not tc["stdout"]:
        return None
    total = 0
    for match in re.finditer(r"dropped\s+(\d+)", tc["stdout"]):
        total += int(match.group(1))
    return total


def ping_target(target: str, samples: int) -> Dict[str, Any]:
    """Run ping and summarize loss and latency."""
    samples = max(3, min(samples, 20))
    out = run_cmd(["ping", "-c", str(samples), "-i", "0.2", "-W", "2", target], timeout=samples * 2 + 3)
    text = out["stdout"] + out["stderr"]
    data: Dict[str, Any] = {"target": target, "raw_tail": "\n".join(text.splitlines()[-5:]), "rc": out["rc"]}
    loss = re.search(r"([\d.]+)%\s+packet loss", text)
    if loss:
        data["packet_loss_pct"] = float(loss.group(1))
    rtt = re.search(r"(?:rtt|round-trip).*?=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", text)
    if rtt:
        data["rtt_min_ms"] = float(rtt.group(1))
        data["rtt_avg_ms"] = float(rtt.group(2))
        data["rtt_max_ms"] = float(rtt.group(3))
        data["rtt_mdev_ms"] = float(rtt.group(4))
    return data


def diagnose_network(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the network diagnosis."""
    unavailable = procfs_required("vm-diagnose network")
    if unavailable:
        return unavailable
    findings: List[Dict[str, str]] = []
    steps: List[Dict[str, str]] = []
    snmp = parse_proc_net_protocols("/proc/net/snmp")
    netstat = parse_proc_net_protocols("/proc/net/netstat")
    interval = max(0.0, min(float(args.interval), 10.0))
    if interval:
        time.sleep(interval)
    snmp_after = parse_proc_net_protocols("/proc/net/snmp")
    ifaces = interface_stats()
    tcp_before = snmp.get("Tcp", {})
    tcp_after = snmp_after.get("Tcp", {})
    out_delta = tcp_after.get("OutSegs", 0) - tcp_before.get("OutSegs", 0)
    retrans_delta = tcp_after.get("RetransSegs", 0) - tcp_before.get("RetransSegs", 0)
    evidence: Dict[str, Any] = {
        "interfaces": ifaces,
        "snmp": {k: v for k, v in snmp.items() if k in ("Tcp", "Udp", "Ip")},
        "snmp_delta": {"Tcp": {"OutSegs": out_delta, "RetransSegs": retrans_delta, "interval_s": interval}},
        "netstat_tcp_ext": netstat.get("TcpExt", {}),
        "softnet_drops": softnet_drops(),
        "qdisc_drops": qdisc_drops(),
        "sockstat": parse_sockstat("/proc/net/sockstat"),
    }
    for iface in ifaces:
        drops = iface["rx_dropped"] + iface["tx_dropped"]
        errors = iface["rx_errors"] + iface["tx_errors"]
        packets = iface["rx_packets"] + iface["tx_packets"]
        if iface["operstate"] == "down" and packets > 0:
            message = (
                f"{iface['name']} is down but has {packets} cumulative packets; "
                f"carrier={iface['carrier']}."
            )
            findings.append(finding("medium", "Interface is down after traffic", message, "root_cause"))
        if drops > 0 or errors > 0:
            severity = "high" if drops + errors > 1000 else "medium"
            message = (
                f"{iface['name']} has rx/tx drops={drops} and "
                f"rx/tx errors={errors} since boot."
            )
            findings.append(finding(severity, "Interface has drops or errors", message, "root_cause"))
    tcp = snmp.get("Tcp", {})
    out_segs = tcp.get("OutSegs", 0)
    retrans = tcp.get("RetransSegs", 0)
    if out_delta > 100 and retrans_delta > 0:
        pct = retrans_delta * 100 / out_delta
        if pct > 1:
            message = (
                f"RetransSegs delta={retrans_delta}, OutSegs delta={out_delta}, "
                f"ratio={pct:.2f}% over {interval:.1f}s."
            )
            findings.append(finding("high", "Live TCP retransmission ratio is high", message, "root_cause"))
        elif pct > 0.2:
            message = (
                f"RetransSegs delta={retrans_delta}, OutSegs delta={out_delta}, "
                f"ratio={pct:.2f}% over {interval:.1f}s."
            )
            findings.append(finding("medium", "Live TCP retransmissions are visible", message))
    elif out_segs and retrans:
        pct = retrans * 100 / out_segs
        if pct > 1:
            message = (
                f"Cumulative since-boot counters show RetransSegs={retrans}, "
                f"OutSegs={out_segs}, ratio={pct:.2f}%, but the live sample did "
                "not have enough outgoing segments to confirm current loss."
            )
            findings.append(finding("medium", "Historical TCP retransmission ratio is high", message))
        elif pct > 0.2:
            message = (
                f"Cumulative since-boot counters show RetransSegs={retrans}, "
                f"OutSegs={out_segs}, ratio={pct:.2f}%."
            )
            findings.append(finding("low", "Historical TCP retransmissions are visible", message))
    tcp_ext = netstat.get("TcpExt", {})
    listen_drops = tcp_ext.get("ListenDrops", 0) + tcp_ext.get("ListenOverflows", 0)
    if listen_drops:
        message = f"ListenDrops+ListenOverflows={listen_drops} since boot."
        findings.append(finding("high", "TCP listen queue overflow/drop detected", message, "root_cause"))
    if evidence["softnet_drops"]:
        message = f"/proc/net/softnet_stat reports {evidence['softnet_drops']} cumulative dropped packets."
        findings.append(finding("medium", "Kernel softnet drops are present", message))
    if evidence["qdisc_drops"]:
        message = f"tc qdisc counters report {evidence['qdisc_drops']} cumulative drops."
        findings.append(finding("medium", "Qdisc drops are present", message))
    if args.target:
        ping = ping_target(args.target, args.samples)
        evidence["ping"] = ping
        loss = ping.get("packet_loss_pct")
        mdev = ping.get("rtt_mdev_ms")
        avg = ping.get("rtt_avg_ms")
        if loss is not None and loss > 0:
            message = f"Ping to {args.target} reported {loss:.1f}% packet loss."
            findings.append(finding("high", "Ping packet loss detected", message, "root_cause"))
        if mdev is not None and mdev > 30:
            message = f"Ping to {args.target} avg={avg:.1f} ms, mdev={mdev:.1f} ms."
            findings.append(finding("medium", "Ping jitter is elevated", message))
    else:
        steps.append(
            next_step(
                "Measure path jitter",
                "python3 scripts/vm_diagnose.py network --target <host-or-ip>",
                "A remote target is required to measure live packet loss and latency jitter.",
            )
        )
    steps.append(
        next_step(
            "Check load if drops coincide with CPU pressure",
            "python3 scripts/vm_diagnose.py load --interval 2",
            "Softnet or qdisc drops can be caused by CPU scheduling pressure.",
        )
    )
    return envelope("vm-diagnose network", findings, steps, evidence)


def diskstats_snapshot() -> Dict[str, Dict[str, int]]:
    """Collect disk statistics snapshots."""
    rows: Dict[str, Dict[str, int]] = {}
    for line in read_text("/proc/diskstats").splitlines():
        parts = line.split()
        if len(parts) < 14:
            continue
        name = parts[2]
        if not re.match(r"^(sd[a-z]+|vd[a-z]+|xvd[a-z]+|nvme\d+n\d+|dm-\d+|md\d+)$", name):
            continue
        nums = [int(x) for x in parts[3:14]]
        rows[name] = {
            "reads": nums[0],
            "read_sectors": nums[2],
            "read_ms": nums[3],
            "writes": nums[4],
            "write_sectors": nums[6],
            "write_ms": nums[7],
            "in_progress": nums[8],
            "io_ms": nums[9],
            "weighted_io_ms": nums[10],
        }
    return rows


def df_table(args: List[str]) -> List[Dict[str, Any]]:
    """Collect df output for the requested paths."""
    out = run_cmd(["df", *args], timeout=5)
    rows = []
    for line in out["stdout"].splitlines()[1:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        rows.append({"filesystem": parts[0], "size": parts[1], "used": parts[2],
                    "available": parts[3], "use_pct": parts[4], "mount": parts[5]})
    return rows


def dmesg_io_errors() -> List[str]:
    """Collect recent IO-related kernel log lines."""
    regex = re.compile(
        r"(I/O error|blk_update_request|Buffer I/O|EXT4-fs error|xfs.*error|nvme.*timeout|reset controller)", re.I)
    dmesg = run_cmd(["dmesg", "-T"], timeout=4)
    return [line.strip() for line in dmesg["stdout"].splitlines() if regex.search(line)][-20:]


def diagnose_io(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the IO diagnosis."""
    unavailable = procfs_required("vm-diagnose io")
    if unavailable:
        return unavailable
    before = diskstats_snapshot()
    time.sleep(max(0.5, min(float(args.interval), 10.0)))
    after = diskstats_snapshot()
    findings: List[Dict[str, str]] = []
    rows = []
    interval = max(0.5, min(float(args.interval), 10.0))
    for name, b in before.items():
        a = after.get(name)
        if not a:
            continue
        rios = a["reads"] - b["reads"]
        wios = a["writes"] - b["writes"]
        ios = rios + wios
        read_ms = a["read_ms"] - b["read_ms"]
        write_ms = a["write_ms"] - b["write_ms"]
        io_ms = a["io_ms"] - b["io_ms"]
        util = io_ms * 100 / (interval * 1000)
        await_ms = (read_ms + write_ms) / ios if ios else 0.0
        row = {
            "device": name,
            "ios": ios,
            "read_ios": rios,
            "write_ios": wios,
            "util_pct": round(util, 1),
            "await_ms": round(await_ms, 1),
            "in_progress": a["in_progress"],
        }
        rows.append(row)
        if util > 90:
            message = f"{name} util is {util:.1f}% over {interval:.1f}s; await={await_ms:.1f} ms, ios={ios}."
            findings.append(finding("high", "Block device is saturated", message, "root_cause"))
        elif util > 70:
            message = f"{name} util is {util:.1f}% over {interval:.1f}s; await={await_ms:.1f} ms."
            findings.append(finding("medium", "Block device utilization is high", message))
        if await_ms > 100:
            message = f"{name} await is {await_ms:.1f} ms over {interval:.1f}s."
            findings.append(finding("high", "Block device latency is high", message, "root_cause"))
        elif await_ms > 50:
            message = f"{name} await is {await_ms:.1f} ms over {interval:.1f}s."
            findings.append(finding("medium", "Block device latency is elevated", message))
    filesystems = df_table(["-P"])
    inodes = df_table(["-Pi"])
    for fs in filesystems:
        pct = int(fs["use_pct"].rstrip("%")) if fs["use_pct"].rstrip("%").isdigit() else 0
        if pct >= 95:
            message = f"{fs['mount']} on {fs['filesystem']} is {fs['use_pct']} used."
            findings.append(finding("high", "Filesystem space is nearly full", message, "root_cause"))
        elif pct >= 85:
            message = f"{fs['mount']} on {fs['filesystem']} is {fs['use_pct']} used."
            findings.append(finding("medium", "Filesystem space is high", message))
    for fs in inodes:
        pct = int(fs["use_pct"].rstrip("%")) if fs["use_pct"].rstrip("%").isdigit() else 0
        if pct >= 95:
            message = f"{fs['mount']} on {fs['filesystem']} inode usage is {fs['use_pct']}."
            findings.append(finding("high", "Filesystem inode usage is nearly full", message, "root_cause"))
    errors = dmesg_io_errors()
    if errors:
        message = (
            f"Found {len(errors)} recent matching kernel log line(s); "
            f"last evidence: {errors[-1][:240]}"
        )
        findings.append(finding("high", "Kernel logs contain IO/filesystem errors", message, "root_cause"))
    evidence = {
        "diskstats_delta": rows,
        "filesystems": filesystems,
        "inodes": inodes,
        "io_log_matches": errors,
    }
    steps = [
        next_step(
            "Check load and iowait context",
            "python3 scripts/vm_diagnose.py load --interval 2",
            "Slow IO often presents as blocked tasks or high iowait.",
        )
    ]
    return envelope("vm-diagnose io", findings, steps, evidence)


def read_cpu_times() -> List[int]:
    """Read CPU time counters from /proc/stat."""
    lines = read_text("/proc/stat").splitlines()
    if not lines:
        return []
    first = lines[0].split()
    return [int(x) for x in first[1:]]


def cpu_delta_percent(before: List[int], after: List[int]) -> Dict[str, float]:
    """Convert CPU deltas into percentages."""
    if not before or not after:
        return {}
    names = ["user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice"]
    delta = [a - b for a, b in zip(after, before)]
    total = sum(delta) or 1
    return {name: round(value * 100 / total, 1) for name, value in zip(names, delta)}


def proc_stat_counts() -> Dict[str, int]:
    """Parse aggregate counts from /proc/stat."""
    out = {}
    for line in read_text("/proc/stat").splitlines():
        if line.startswith("procs_running") or line.startswith("procs_blocked"):
            k, v = line.split()
            out[k] = int(v)
    return out


def parse_loadavg() -> Dict[str, Any]:
    """Parse /proc/loadavg into structured fields."""
    parts = read_text("/proc/loadavg").split()
    if len(parts) < 5:
        return {}
    running, total = parts[3].split("/", 1)
    return {
        "load1": float(parts[0]),
        "load5": float(parts[1]),
        "load15": float(parts[2]),
        "running": int(running),
        "tasks": int(total),
        "last_pid": int(parts[4]),
    }


def pressure(path: str) -> Dict[str, Dict[str, float]]:
    """Parse a PSI pressure file."""
    result: Dict[str, Dict[str, float]] = {}
    for line in read_text(path).splitlines():
        parts = line.split()
        if not parts:
            continue
        kind = parts[0]
        values: Dict[str, float] = {}
        for item in parts[1:]:
            if "=" in item:
                k, v = item.split("=", 1)
                try:
                    values[k] = float(v)
                except ValueError:
                    pass
        result[kind] = values
    return result


def proc_cpu_snapshot() -> Dict[int, int]:
    """Capture per-process CPU time snapshots."""
    rows = {}
    if not os.path.isdir("/proc"):
        return rows
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        stat = read_text(f"/proc/{pid}/stat", 4096)
        if not stat:
            continue
        try:
            after_comm = stat.rsplit(")", 1)[1].split()
            utime = int(after_comm[11])
            stime = int(after_comm[12])
            rows[int(pid)] = utime + stime
        except Exception:
            continue
    return rows


def top_cpu_processes(interval: float) -> List[Dict[str, Any]]:
    """Sample the top CPU-consuming processes."""
    before = proc_cpu_snapshot()
    time.sleep(interval)
    after = proc_cpu_snapshot()
    hz = os.sysconf(os.sysconf_names.get("SC_CLK_TCK", "SC_CLK_TCK"))
    rows = []
    for pid, end in after.items():
        start = before.get(pid)
        if start is None:
            continue
        pct = (end - start) / hz / interval * 100
        if pct > 0.5:
            rows.append({"pid": pid, "cpu_pct_one_core": round(pct, 1), "cmdline": proc_cmdline(str(pid))[:220]})
    return sorted(rows, key=lambda x: x["cpu_pct_one_core"], reverse=True)[:8]


def diagnose_load(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the load diagnosis."""
    unavailable = procfs_required("vm-diagnose load")
    if unavailable:
        return unavailable
    interval = max(0.5, min(float(args.interval), 10.0))
    cpu_before = read_cpu_times()
    cpu_top = top_cpu_processes(interval)
    cpu_after = read_cpu_times()
    cpu_pct = cpu_delta_percent(cpu_before, cpu_after)
    load = parse_loadavg()
    stat_counts = proc_stat_counts()
    cpus = os.cpu_count() or 1
    findings: List[Dict[str, str]] = []
    if load:
        load_signal_valid = True
        sanity_cap = max(load["tasks"] * 2, cpus * 100, 1000)
        if load["load1"] > sanity_cap:
            load_signal_valid = False
            message = (
                f"/proc/loadavg reports load1={load['load1']:.2f}, but "
                f"tasks={load['tasks']}, procs_running={stat_counts.get('procs_running', 0)}, "
                f"and the sanity cap is {sanity_cap}. Treat loadavg as unavailable and use "
                "CPU split, PSI, and runnable/blocked counts instead."
            )
            findings.append(
                finding(
                    "medium",
                    "Load average signal appears corrupt",
                    message,
                )
            )
        ratio = load["load1"] / cpus
        if load_signal_valid and ratio > 2:
            message = f"load1={load['load1']:.2f}, CPUs={cpus}, ratio={ratio:.2f}."
            findings.append(finding("critical", "Load average is far above CPU count", message, "root_cause"))
        elif load_signal_valid and ratio > 1:
            message = f"load1={load['load1']:.2f}, CPUs={cpus}, ratio={ratio:.2f}."
            findings.append(finding("high", "Load average exceeds CPU count", message, "root_cause"))
    if cpu_pct.get("iowait", 0) > 20:
        message = f"iowait={cpu_pct['iowait']:.1f}% over {interval:.1f}s."
        findings.append(finding("high", "CPU time is waiting on IO", message, "root_cause"))
    elif cpu_pct.get("iowait", 0) > 10:
        message = f"iowait={cpu_pct['iowait']:.1f}% over {interval:.1f}s."
        findings.append(finding("medium", "IO wait is elevated", message))
    if cpu_pct.get("steal", 0) > 10:
        message = (
            f"steal={cpu_pct['steal']:.1f}% over {interval:.1f}s; this "
            "points to hypervisor contention or throttling."
        )
        findings.append(finding("medium", "CPU steal time is elevated", message))
    if stat_counts.get("procs_blocked", 0) > 0:
        message = f"procs_blocked={stat_counts['procs_blocked']} in /proc/stat."
        findings.append(finding("medium", "Blocked tasks are present", message))
    psi_cpu = pressure("/proc/pressure/cpu")
    psi_io = pressure("/proc/pressure/io")
    psi_mem = pressure("/proc/pressure/memory")
    for name, data in [("CPU", psi_cpu), ("IO", psi_io), ("memory", psi_mem)]:
        some10 = data.get("some", {}).get("avg10", 0.0)
        full10 = data.get("full", {}).get("avg10", 0.0)
        if full10 > 10 or some10 > 30:
            message = f"{name} PSI some.avg10={some10:.2f}, full.avg10={full10:.2f}."
            findings.append(finding("high", f"{name} pressure stall is high", message, "root_cause"))
        elif full10 > 3 or some10 > 10:
            message = f"{name} PSI some.avg10={some10:.2f}, full.avg10={full10:.2f}."
            findings.append(finding("medium", f"{name} pressure stall is elevated", message))
    if cpu_top and cpu_top[0]["cpu_pct_one_core"] > 80:
        p = cpu_top[0]
        message = (
            f"PID {p['pid']} used {p['cpu_pct_one_core']:.1f}% of one CPU "
            f"over {interval:.1f}s; command: {p['cmdline']}"
        )
        findings.append(finding("medium", "A process is consuming a CPU core", message))
    evidence = {
        "loadavg": load,
        "cpu_percent": cpu_pct,
        "proc_stat": stat_counts,
        "pressure": {"cpu": psi_cpu, "io": psi_io, "memory": psi_mem},
        "top_cpu": cpu_top,
    }
    steps = [
        next_step(
            "Check IO when iowait or blocked tasks are present",
            "python3 scripts/vm_diagnose.py io --interval 2",
            "High load may be caused by slow block IO.",
        ),
        next_step(
            "Check memory pressure",
            "python3 scripts/vm_diagnose.py memory",
            "Memory pressure can create CPU stalls and high load.",
        ),
    ]
    return envelope("vm-diagnose load", findings, steps, evidence)


def parse_size_to_kb(value: str) -> Optional[int]:
    """Parse a size string into KiB."""
    m = re.fullmatch(r"(\d+)([kKmMgGtT]?)", value.strip())
    if not m:
        return None
    num = int(m.group(1))
    unit = m.group(2).lower()
    mult = {"": 1 / 1024, "k": 1, "m": 1024, "g": 1024 * 1024, "t": 1024 * 1024 * 1024}[unit]
    return int(num * mult)


def java_processes() -> List[Dict[str, Any]]:
    """Collect visible Java processes."""
    rows = []
    for p in top_processes_by_rss(1000):
        haystack = (p["cmdline"] + " " + p["name"]).lower()
        if "java" not in haystack:
            continue
        cmd = p["cmdline"]
        xmx = None
        xms = None
        m = re.search(r"(?:^|\s)-Xmx(\S+)", cmd)
        if m:
            xmx = parse_size_to_kb(m.group(1))
        m = re.search(r"(?:^|\s)-Xms(\S+)", cmd)
        if m:
            xms = parse_size_to_kb(m.group(1))
        max_ram_pct = None
        m = re.search(r"-XX:MaxRAMPercentage=([\d.]+)", cmd)
        if m:
            max_ram_pct = float(m.group(1))
        p.update({"xmx_kb": xmx, "xms_kb": xms, "max_ram_percentage": max_ram_pct})
        rows.append(p)
    return sorted(rows, key=lambda x: x["rss_kb"], reverse=True)


def jcmd_info(pid: int) -> Dict[str, Any]:
    """Collect jcmd metadata for a Java process."""
    if not shutil.which("jcmd"):
        return {"available": False, "reason": "jcmd not found"}
    info: Dict[str, Any] = {"available": True}
    for name, cmd in {
        "vm_flags": ["jcmd", str(pid), "VM.flags"],
        "heap_info": ["jcmd", str(pid), "GC.heap_info"],
    }.items():
        out = run_cmd(cmd, timeout=4)
        info[name] = {"ok": out["ok"], "tail": "\n".join((out["stdout"] + out["stderr"]).splitlines()[-20:])}
    return info


def diagnose_java(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the Java diagnosis."""
    unavailable = procfs_required("vm-diagnose java")
    if unavailable:
        return unavailable
    mem = parse_meminfo()
    total = mem.get("MemTotal", 0)
    procs = java_processes()
    findings: List[Dict[str, str]] = []
    evidence: Dict[str, Any] = {"java_processes": procs}
    if not procs:
        findings.append(
            finding(
                "info",
                "No Java process found",
                "No process with java in its command line was visible under /proc.",
                "summary",
            )
        )
        return envelope(
            "vm-diagnose java",
            findings,
            [
                next_step(
                    "Run generic memory diagnosis",
                    "python3 scripts/vm_diagnose.py memory",
                    "The symptom may be non-Java memory pressure.",
                )
            ],
            evidence,
        )
    leader = procs[0]
    if total:
        pct = leader["rss_kb"] * 100 / total
        if pct > 50:
            message = (
                f"PID {leader['pid']} holds {human_kb(leader['rss_kb'])} RSS "
                f"({pct:.1f}% of memory); Xmx="
                f"{human_kb(leader['xmx_kb']) if leader.get('xmx_kb') else 'not visible'}."
            )
            findings.append(finding("high", "Java process dominates memory", message, "root_cause"))
        elif pct > 25:
            message = f"PID {leader['pid']} holds {human_kb(leader['rss_kb'])} RSS ({pct:.1f}% of memory)."
            findings.append(finding("medium", "Java process RSS is significant", message))
    for proc in procs[:5]:
        if not proc.get("xmx_kb") and not proc.get("max_ram_percentage"):
            message = (
                f"PID {proc['pid']} has no -Xmx or -XX:MaxRAMPercentage in "
                f"the visible command line; RSS={human_kb(proc['rss_kb'])}."
            )
            findings.append(finding("medium", "Java heap limit is not visible in command line", message))
            break
    if args.jcmd and procs:
        evidence["jcmd"] = {str(procs[0]["pid"]): jcmd_info(procs[0]["pid"])}
    steps = [
        next_step(
            "Run generic memory overview",
            "python3 scripts/vm_diagnose.py memory",
            "Correlate Java RSS with VM memory pressure, swap, and OOM evidence.",
        ),
    ]
    if not args.jcmd:
        steps.append(
            next_step(
                "Collect JVM heap details",
                "python3 scripts/vm_diagnose.py java --jcmd",
                "Use jcmd for the largest visible Java process when attach is acceptable.",
            )
        )
    return envelope("vm-diagnose java", findings, steps, evidence)


def service_state(name: str) -> str:
    """Return the systemd state for a service."""
    out = run_cmd(["systemctl", "is-active", name], timeout=3)
    if out["stdout"].strip():
        return out["stdout"].strip()
    return "unknown"


def diagnose_health(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the OS health diagnosis."""
    unavailable = procfs_required("vm-diagnose health")
    if unavailable:
        return unavailable
    findings: List[Dict[str, str]] = []
    evidence: Dict[str, Any] = {}
    fstab = read_text("/etc/fstab")
    if not fstab:
        findings.append(finding("high", "fstab is missing or unreadable",
                        "/etc/fstab could not be read.", "root_cause"))
    else:
        devices = []
        mounts = []
        uuids = []
        bad_lines = []
        missing = []
        for idx, line in enumerate(fstab.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 6:
                bad_lines.append(idx)
                continue
            dev, mount = parts[0], parts[1]
            devices.append(dev)
            mounts.append(mount)
            if dev.startswith("UUID="):
                uuids.append(dev[5:])
                if run_cmd(["blkid", "-U", dev[5:]], timeout=3)["rc"] != 0:
                    missing.append(dev)
            elif dev.startswith("/dev/") and not os.path.exists(dev):
                missing.append(dev)
        dup_devices = sorted({x for x in devices if devices.count(x) > 1})
        dup_mounts = sorted({x for x in mounts if mounts.count(x) > 1})
        dup_uuids = sorted({x for x in uuids if uuids.count(x) > 1})
        evidence["fstab"] = {
            "bad_lines": bad_lines,
            "duplicate_devices": dup_devices,
            "duplicate_mounts": dup_mounts,
            "duplicate_uuids": dup_uuids,
            "missing_devices": missing,
        }
        if bad_lines:
            message = f"/etc/fstab lines {bad_lines} have fewer than 6 fields."
            findings.append(finding("high", "fstab has malformed lines", message, "root_cause"))
        if dup_devices or dup_mounts or dup_uuids:
            message = (
                f"duplicate_devices={dup_devices}, duplicate_mounts={dup_mounts}, "
                f"duplicate_uuids={dup_uuids}."
            )
            findings.append(finding("high", "fstab has duplicate entries", message, "root_cause"))
        if missing:
            message = f"Missing devices or UUIDs: {missing}."
            findings.append(finding("high", "fstab references missing devices", message, "root_cause"))
    file_nr = read_first_line("/proc/sys/fs/file-nr").split()
    file_max = read_first_line("/proc/sys/fs/file-max")
    if len(file_nr) >= 1 and file_nr[0].isdigit() and file_max.isdigit() and int(file_max) > 0:
        pct = int(file_nr[0]) * 100 / int(file_max)
        evidence["file_handles"] = {
            "allocated": int(file_nr[0]),
            "max": int(file_max),
            "usage_pct": round(pct, 1),
        }
        if pct > 80:
            message = f"allocated={file_nr[0]}, max={file_max}, usage={pct:.1f}%."
            findings.append(finding("high", "System file handle table is near exhaustion", message, "root_cause"))
    mem = parse_meminfo()
    hp_total = mem.get("HugePages_Total", 0)
    hp_size = mem.get("Hugepagesize", 0)
    if hp_total and hp_size and mem.get("MemTotal"):
        hp_kb = hp_total * hp_size
        pct = hp_kb * 100 / mem["MemTotal"]
        evidence["hugepages"] = {
            "hugepage_mem_kb": hp_kb,
            "mem_total_kb": mem["MemTotal"],
            "usage_pct": round(pct, 1),
        }
        if pct > 50:
            message = f"HugePages_Total reserves {human_kb(hp_kb)} ({pct:.1f}% of memory)."
            findings.append(finding("medium", "Hugepage reservation is large", message))
    ip_forward = read_first_line("/proc/sys/net/ipv4/ip_forward")
    tcp_sack = read_first_line("/proc/sys/net/ipv4/tcp_sack")
    evidence["sysctl"] = {"ip_forward": ip_forward, "tcp_sack": tcp_sack}
    if ip_forward.isdigit() and int(ip_forward) != 0 and service_state("docker") != "active":
        message = f"net.ipv4.ip_forward={ip_forward} while docker is not active."
        findings.append(finding("medium", "NAT forwarding is enabled", message))
    if tcp_sack == "0":
        findings.append(finding("medium", "TCP SACK is disabled", "net.ipv4.tcp_sack=0 can hurt TCP loss recovery."))
    services = {}
    for name in ["sshd", "ssh", "cloud-init", "chronyd", "chrony", "ntpd"]:
        services[name] = service_state(name)
    evidence["services"] = services
    if services.get("sshd") not in ("active", "unknown") and services.get("ssh") not in ("active", "unknown"):
        message = f"sshd={services.get('sshd')}, ssh={services.get('ssh')}."
        findings.append(finding("medium", "SSH service is not active", message))
    steps = [
        next_step(
            "Check memory symptoms",
            "python3 scripts/vm_diagnose.py memory",
            "Health issues often surface alongside memory pressure.",
        ),
        next_step(
            "Check IO symptoms",
            "python3 scripts/vm_diagnose.py io --interval 2",
            "fstab, filesystem, and disk issues may manifest as slow IO.",
        ),
    ]
    return envelope("vm-diagnose health", findings, steps, evidence)


def diagnose_classify(args: argparse.Namespace) -> Dict[str, Any]:
    """Run the cross-domain classifier."""
    unavailable = procfs_required("vm-diagnose classify")
    if unavailable:
        return unavailable
    sub_args = argparse.Namespace(interval=args.interval, target=None, samples=5, jcmd=False)
    domains = [
        diagnose_memory(sub_args),
        diagnose_load(sub_args),
        diagnose_io(sub_args),
        diagnose_network(sub_args),
        diagnose_health(sub_args),
    ]
    findings: List[Dict[str, str]] = []
    steps: List[Dict[str, str]] = []
    evidence: Dict[str, Any] = {"domains": {}}
    for doc in domains:
        domain_name = doc["command"].split()[-1]
        evidence["domains"][domain_name] = {"status": doc["agent"]["status"], "summary": doc["agent"]["summary"]}
        for f in doc["agent"]["findings"]:
            if f.get("severity") != "info":
                findings.append(finding(f["severity"], f"{domain_name}: {f['title']}",
                                f["detail"], f.get("category", "observation")))
        if doc["agent"]["status"] in ("warning", "error", "critical") and doc["agent"]["next_steps"]:
            steps.extend(doc["agent"]["next_steps"][:1])
    if not findings:
        message = (
            "Memory, load, IO, network, and OS health checks did not cross "
            "simple alert thresholds."
        )
        findings.append(finding("info", "No obvious cross-domain issue found", message, "summary"))
    return envelope("vm-diagnose classify", findings, steps[:5], evidence)


def main(argv: Optional[List[str]] = None) -> int:
    """Parse CLI arguments and run the requested diagnosis."""
    parser = argparse.ArgumentParser(description="Read-only Linux VM diagnostics.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("classify")
    p.add_argument("--interval", type=float, default=1.0)
    sub.add_parser("memory")
    p = sub.add_parser("network")
    p.add_argument("--target")
    p.add_argument("--samples", type=int, default=5)
    p.add_argument("--interval", type=float, default=1.0)
    p = sub.add_parser("io")
    p.add_argument("--interval", type=float, default=1.0)
    p = sub.add_parser("load")
    p.add_argument("--interval", type=float, default=1.0)
    p = sub.add_parser("java")
    p.add_argument("--jcmd", action="store_true")
    sub.add_parser("health")
    args = parser.parse_args(argv)
    if args.command == "classify":
        doc = diagnose_classify(args)
    elif args.command == "memory":
        doc = diagnose_memory(args)
    elif args.command == "network":
        doc = diagnose_network(args)
    elif args.command == "io":
        doc = diagnose_io(args)
    elif args.command == "load":
        doc = diagnose_load(args)
    elif args.command == "java":
        doc = diagnose_java(args)
    elif args.command == "health":
        doc = diagnose_health(args)
    else:
        parser.error("unknown command")
    print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if doc.get("ok", False) else 1


if __name__ == "__main__":
    sys.exit(main())

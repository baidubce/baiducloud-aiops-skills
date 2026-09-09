# GPU and RDMA Resources

Use this reference only for GPU, RDMA, GPU passthrough, or accelerated VM symptoms.

## Optional GPU/RDMA Toolchain

When a target environment already has the GPU/RDMA diagnostic toolchain
available, the most reusable subdirectory is:

`gpu/deploy/diag/gpu_diag/`

Key files:

| File | Use |
| --- | --- |
| `gpu_diag.sh` | Main read-only self-check script for GPU, RDMA, and VM health events |
| `gpu_unit_test.sh` | Mock test harness for GPU/RDMA checks |
| `fake_cmd.sh` | Fake command provider for no-hardware testing |
| `RULE.md` | Compatibility and validation notes across Ubuntu, CentOS, Debian, AlmaLinux, Rocky, BaiduLinux, Fedora, OpenSUSE |
| `CLAUDE.md` | Existing developer notes and output contract |

## Existing Check Groups

`gpu_diag.sh` emits JSON event records with `event_type`, `event_level`, `event_object`, `event_code`, and `event_debug_msg`.

Check groups observed in the script:

- GPU: lspci accessibility/count, `pci=realloc`, nouveau, PCIe link speed/width, NVLink count/bandwidth, fabricmanager, Xid errors, ECC modes and thresholds, temperature, nvidia-smi errors, topology, nvidia-peermem, NVSwitch, HAS health.
- RDMA: PCIe link speed/width, ethtool speed, interface status, link-down logs, MAC case, GID index order, IB NIC order, inner-machine RoCE connection.
- VM health: OOM, low memory, disk/CPU pressure, NTP, SSH, cloud-init, network config, fstab duplicate/missing/malformed entries, fd exhaustion, NAT sysctl, TCP SACK, DHCP, nofile, hugepages.

## How to Reuse

For GPU/RDMA user symptoms, run the existing script on the target Linux guest or GPU host when available:

```bash
bash gpu_diag.sh check <gpu_count> GPU all
bash gpu_diag.sh check <gpu_count> RDMA all
bash gpu_diag.sh check <gpu_count> VM all
```

For no-hardware validation:

```bash
bash gpu_unit_test.sh init
bash gpu_diag.sh test 8 GPU all 20f3
bash gpu_diag.sh test 8 RDMA all 101d
bash gpu_unit_test.sh deinit
```

Do not copy the full GPU toolchain into the generic VM diagnosis path. Treat it as a specialized optional backend and translate its event JSON into the same root-cause/evidence/next-step answer shape used by this skill.

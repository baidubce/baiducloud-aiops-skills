# RAM Policies

## Required Permissions

This Skill signs every request with the caller's AK/SK. The cloud-side CCE Agent then performs
**read-only** queries on that account's behalf (clusters, nodes, in-cluster workloads, network
and metrics), so the AK/SK only needs read permissions — no `*_OPERATE` permission is required.

### CCE Permissions

| Permission | Service | Resource | Description |
|------------|---------|----------|-------------|
| `CCE_READ` | `bce:cce` | `*` | Read CCE clusters, node groups, in-cluster workloads and events |

### BCC Permissions

| Permission | Service | Resource | Description |
|------------|---------|----------|-------------|
| `BCC_READ` | `bce:bcc` | `*` | Read the instances backing cluster nodes (spec, status, availability zone) |

### Network Permissions

| Permission | Service | Resource | Description |
|------------|---------|----------|-------------|
| `VPC_READ` | `bce:network` | `*` | Read VPC, route table and security group configuration for connectivity checks |
| `SUBNET_READ` | `bce:network` | `*` | Read subnet configuration and remaining IP capacity (Pod Pending diagnosis) |

## Recommended RAM Policy

```json
{
  "version": "v1",
  "accessControlList": [
    {
      "service": "bce:cce",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "CCE_READ"
      ]
    },
    {
      "service": "bce:bcc",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "BCC_READ"
      ]
    },
    {
      "service": "bce:network",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "VPC_READ",
        "SUBNET_READ"
      ]
    }
  ]
}
```

## Notes

- Read-only by design: the cloud-side Agent never mutates cloud resources, so granting any
  `*_OPERATE` permission to this Skill's AK/SK is unnecessary and not recommended.
- `region` is kept as `*` because a single session can query across all nine regions
  (`bd bj cd fwh gz hkg nj su yq`). Narrow it to the regions you actually operate in, and pair
  that with the CLI's `--regions` flag to tighten the blast radius further.
- `BCC_READ` and the network permissions are only needed for node-level and connectivity
  diagnosis. If you only list clusters and read their status, `CCE_READ` alone is enough.
- CProm (monitoring) metrics require the monitoring read permission of your deployment
  (`bce:bcm` / CProm service). Confirm the exact permission name in the IAM console before
  adding it — omit it if the Skill is not used for metric queries.
- Keep the `resource` scope as small as possible: if the Skill only touches a subset of
  clusters, list those cluster resources instead of `*`.

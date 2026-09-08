# Audit Rules

## Severity model

- `high`: Direct allow from an unrestricted public source to all traffic or a sensitive destination port.
- `medium`: Broad public ingress, conflicting priority behavior, or an earlier ACL rule that makes a later opposite-action rule ineffective.
- `low`: Unrestricted outbound access, exact duplicate rules, or same-action ACL redundancy.
- `info`: Empty policy groups or coverage/field limitations requiring context.

## Rule catalog

| Rule ID | Applies to | Condition | Interpretation |
|---|---|---|---|
| `SG-001` | Ordinary SG | Public ingress allows all protocols and all ports | Maximum ordinary-SG ingress exposure |
| `SG-002` | Ordinary SG | Public ingress includes a sensitive destination port | Administrative or data service exposure |
| `SG-003` | Ordinary SG | Other public ingress allow | Broad source scope requires justification |
| `SG-004` | Ordinary SG | Unrestricted all-protocol/all-port egress | Low-risk governance item; often a default rule |
| `SG-005` | Ordinary SG | No rules | Both directions deny by default; confirm intent |
| `SG-006` | Ordinary SG | Exact duplicate match | Redundant policy maintenance burden |
| `ESG-001`–`ESG-006` | Enterprise SG | Equivalent exposure, egress, empty and duplicate checks | Honor `action` and priority semantics |
| `ESG-007` | Enterprise SG | Same priority and same match have allow and deny | Deny wins; configuration intent may be unclear |
| `ACL-001` | ACL | Public ingress allow covers all protocols and ports | Maximum subnet-level ingress exposure |
| `ACL-002` | ACL | Public ingress allow includes a sensitive port | Sensitive service exposure at subnet boundary |
| `ACL-003` | ACL | Other public ingress allow | Broad source scope requires justification |
| `ACL-004` | ACL | Unrestricted all-protocol/all-port egress allow | Low-risk governance item |
| `ACL-005` | ACL | Exact duplicate match and action | Redundant policy maintenance burden |
| `ACL-006` | ACL | Higher-priority rule fully covers a lower rule with the same action | Lower rule is redundant |
| `ACL-007` | ACL | Higher-priority rule fully covers a lower rule with the opposite action | Lower rule may never take effect |

## Sensitive destination ports

The built-in set is intentionally conservative: `22`, `23`, `3389`, `1433`, `1521`, `2049`, `2375`, `2376`, `3306`, `5432`, `5900`, `6379`, `6443`, `9200`, `11211`, and `27017`.

When a rule contains a range, trigger the sensitive-port rule if the range includes any listed port. Protocol `all` is treated as covering TCP and UDP.

## Evidence and false-positive controls

- Report the actual direction, action, protocol, remote address, port range and priority/position.
- Do not label a parameter template, IP address group, address family or nested security group as public without resolving its members.
- Do not infer that a security group is associated with a publicly reachable instance from the group list alone.
- Do not recommend deletion based solely on duplication or shadowing; propose manual validation of traffic intent and association scope.
- If a field is missing or unparsable, skip coverage-based shadow analysis and record only findings supported by returned values.

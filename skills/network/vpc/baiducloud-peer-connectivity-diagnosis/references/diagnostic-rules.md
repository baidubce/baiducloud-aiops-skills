# Diagnostic Rules

## Confidence

- `confirmed`: direct returned fields establish the condition.
- `candidate`: configuration evidence suggests a likely blocker, but another layer or undocumented behavior may affect the outcome.
- `unknown`: the required endpoint, permission, mapping, or field is unavailable.

## Connection and coverage

| Rule | Severity | Confidence | Condition |
|---|---:|---|---|
| `COV-001` | high | unknown | A required local query fails for a non-permission reason |
| `COV-002` | high | unknown | A local query returns `401` or `403` |
| `COV-003` | info | unknown | Peer endpoint is inaccessible, commonly in cross-account peering |
| `COV-004` | info | unknown | A query returns `404`; verify region, ID and account scope |
| `CONN-001` | high | confirmed | Connection status is `down`, `error`, `expired` or `consult_failed` |
| `CONN-002` | medium | confirmed | Connection status is not `active` and is not one of the terminal failures above |
| `CONN-003` | high | confirmed | Opposite endpoint view returns a different local VPC than advertised |

## Addressing and route

| Rule | Severity | Confidence | Condition |
|---|---:|---|---|
| `ADDR-001` | high | confirmed | Supplied source or destination IP is not contained in any successfully queried subnet on its expected endpoint |
| `ADDR-002` | high | confirmed | Located source and destination subnet CIDRs overlap |
| `ADDR-003` | info | candidate | Topology mode finds overlapping subnet pairs; these may be valid when other non-overlapping subnets are routed |
| `ROUTE-001` | high | confirmed | No local forward peering route covers the precise source/destination flow with the expected local interface ID |
| `ROUTE-002` | high | confirmed | No peer-side reverse peering route covers the reversed precise flow with the peer endpoint interface ID |
| `ROUTE-003` | medium | candidate | Topology mode finds one or more opposite subnets without a peering route through the expected interface |
| `ROUTE-004` | high | candidate | A more-specific matching route points to a different next hop than the selected peering route |
| `ROUTE-005` | medium | confirmed | A `peerConn` route references the connection ID or another interface instead of the endpoint `localIfId` |
| `ROUTE-006` | info | unknown | Interface ID or route fields are unavailable, so exact next-hop validation cannot be completed |

## Security policy

| Rule | Severity | Confidence | Condition |
|---|---:|---|---|
| `SG-001` | high | candidate | Complete source ENI/group evidence has no matching egress allow for the precise flow |
| `SG-002` | high | candidate | Complete destination ENI/group evidence has no matching ingress allow for the precise flow |
| `SG-003` | info | unknown | IP-to-ENI mapping, referenced groups, protocol/port, or rule fields are incomplete |
| `ACL-001` | high | confirmed | First matching source-subnet egress ACL rule explicitly denies the flow |
| `ACL-002` | high | confirmed | First matching destination-subnet ingress ACL rule explicitly denies the flow |
| `ACL-003` | info | unknown | No deterministic ACL verdict can be produced from the returned ordered rules |
| `POLICY-001` | info | unknown | Enterprise security-group or unsupported policy references are present |

## Interpretation order

Review findings in this order:

1. coverage and endpoint orientation;
2. connection lifecycle state;
3. source/destination subnet placement and overlap;
4. forward and reverse route next hops;
5. ordinary security-group evidence;
6. subnet ACL evidence;
7. host firewall, listener, application and data-plane checks outside this Skill.

Do not proceed to mutation automatically. Present the smallest likely correction and require a separate reviewed change workflow.

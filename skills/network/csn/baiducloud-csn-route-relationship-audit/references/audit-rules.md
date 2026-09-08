# Audit Rules

## Interpretation Principles

- Findings describe a control-plane snapshot, not route reachability or traffic success.
- Association and learning relationships serve different directions; one cannot substitute for the other.
- VPC/BEC instances without explicit association may fall back to the default table, while a dedicated-line channel requires association for learned routes to be published to it. Missing relationships still require intent review.
- A route conflict is explicit control-plane evidence. A black-hole route or isolation between tables can be intentional and must not be auto-remediated.
- Cross-references are checked only where both source queries succeeded.

## Coverage Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `COV-001` | high | A list GET fails, pagination cannot finish, or a selected CSN ID is unmatched | The affected route scope is not fully audited |
| `COV-002` | high | HTTP 401 or 403 | Authentication or read-only authorization is insufficient |
| `COV-004` | info | HTTP 404 | Endpoint, API version, CSN ID, or route-table ID needs review |

## Route Table Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `CSNRT-001` | high | Route table lacks `csnRtId`, or the ID repeats within a CSN | Route-table identity is missing or duplicated |
| `CSNRT-002` | info | Route-table type is missing or not `default`/`custom` | Preserve an undocumented type for review |
| `CSNRT-003` | high | A successfully queried CSN has zero or multiple `default` route tables | Product guidance says a CSN automatically has one default table |
| `CSNRT-004` | info | A custom table has zero associations, zero propagations and zero rules, with all three queries successful | The table appears unused or staged; isolation may be intentional |

## Association and Learning Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `CSNREL-001` | high | Relationship lacks `attachId` or references an attachment absent from a successfully queried network-instance list | The relationship cannot be tied to a loaded instance |
| `CSNREL-002` | high/info | Status contains `fail`/`error`, or is outside accepted normal examples | Failure-like status is high; other unknown states are informational |
| `CSNREL-003` | medium | Same `attachId` is associated with multiple route tables | Forwarding-table selection is ambiguous and needs review |
| `CSNREL-004` | medium | A loaded instance appears in no learning relationship, with all route-table learning queries successful | CSN may not learn routes from the instance; deliberate isolation is possible |
| `CSNREL-005` | high/info | A loaded `channel` has no association, or another loaded type has no association | Dedicated-line association absence is high; other types are informational because default-table fallback may apply |
| `CSNREL-006` | medium | A relationship appears more than once in the same table | Duplicate relationship evidence needs review |
| `CSNREL-007` | info | Relationship type/region/instance ID differs from the loaded-instance record | Metadata may have changed between GETs or be inconsistent |

## Route Entry Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `CSNRULE-001` | high | Route status is `conflicted` | Official model reports the route as conflicting and not effective |
| `CSNRULE-002` | medium | `blackHole` is true | Traffic matching this route is discarded; this may be intentional |
| `CSNRULE-003` | high | `ruleId` or `destAddress` is missing, or `ruleId` repeats in one table | Route identity or destination evidence is incomplete/duplicated |
| `CSNRULE-004` | medium | `destAddress` is not a valid IPv4/IPv6 network | Destination syntax needs review; host bits are accepted only when the API returns them intentionally |
| `CSNRULE-005` | high | Route `csnId` or `csnRtId` conflicts with its containing CSN/table | Parent identity evidence is inconsistent |
| `CSNRULE-006` | high/medium | A propagated route lacks `fromAttachId`, or references a non-learning attachment when propagation coverage succeeded | Source is missing or not represented by current learning relations |
| `CSNRULE-007` | medium | A custom route lacks `nextHopId` | The returned forwarding target is incomplete |
| `CSNRULE-008` | info | Route status/type is missing or undocumented | Preserve unknown control-plane state for review |

Do not flag duplicate destinations by themselves: ECMP and deliberate alternatives can be valid. Do not infer longest-prefix selection, BGP best path, bandwidth availability, or data-plane reachability.

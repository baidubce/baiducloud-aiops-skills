# Audit Rules

## Interpretation Principles

- Findings describe control-plane configuration, not authoritative DNS answers or end-user reachability.
- Only `running` records participate in coexistence and default-line coverage checks. Paused or failed records remain reported separately.
- Exact duplicate records are suspicious; multiple distinct A, AAAA, MX, TXT, NS, or SRV values can be intentional.
- Line-specific records are evaluated within the same normalized line. Different lines are independent DNS views.
- Unknown product versions, record types, statuses, and line names are retained as information findings rather than guessed.

## Coverage Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `COV-001` | high | A list request fails or pagination cannot complete | The affected scope is not fully audited |
| `COV-002` | high | HTTP 401 or 403 | Authentication or authorization prevents complete coverage |
| `COV-004` | info | HTTP 404 | Endpoint, API version, or zone identity needs review |
| `ZONE-001` | high/medium | Zone status is `failed`, `unregister`, `nsunchange`, or `torenew` | The service reports a non-running zone state |
| `ZONE-002` | high/medium | `expireTime` is past or within 30 days | Manual renewal/ownership review is needed; no renewal is performed |
| `ZONE-003` | info | A successful record query returns zero records | Empty configuration fact, not a query failure |

## Record Quality Rules

| Rule | Severity | Condition | Meaning |
|---|---|---|---|
| `DNS-001` | high | A record value is not a single IPv4 address | Value conflicts with the documented A format |
| `DNS-002` | high | AAAA record value is not a single IPv6 address | Value conflicts with the documented AAAA format |
| `DNS-003` | high | CNAME, NS, or MX target is not a valid DNS hostname | Target format needs correction or review |
| `DNS-004` | high | A running CNAME coexists with a running non-CNAME at the same owner and line | CNAME exclusivity conflict within one DNS view |
| `DNS-005` | medium | More than one running CNAME target exists at the same owner and line | One alias has multiple canonical targets |
| `DNS-006` | low | Exact duplicate active records share owner, type, value, line, and MX priority | Likely redundant configuration; distinct multi-value records are not flagged |
| `DNS-007` | high | TTL is missing, non-integer, non-positive, or below the zone version minimum | TTL conflicts with API/product constraints |
| `DNS-008` | medium | MX priority is missing, non-integer, or outside 0–50 | MX configuration conflicts with the documented range |
| `DNS-009` | high/low | Record status is `failed` or `stopped` | Failed is an error; stopped is a review item and may be intentional |
| `DNS-010` | low | RR is a valid wildcard such as `*` or `*.api` | Broad matching is reported for governance review, not called a fault |
| `DNS-011` | high | `*` appears in an invalid RR position | Wildcard syntax needs review |
| `DNS-012` | low | An owner has running line-specific records but no running `default` record | Users outside configured lines may lack an intended fallback; verify design |
| `DNS-013` | info | A/AAAA points to a non-global address | Public publication of private, loopback, link-local, reserved, or multicast space may be intentional |
| `DNS-014` | info | Zone/record status, product version, or record type is missing or outside current documented enums | Service evolution or incomplete data needs human interpretation |
| `DNS-015` | medium | SRV value is not `priority weight port target` with numeric fields and a valid target | Value conflicts with the documented SRV format |

Hostname syntax checks accept an optional trailing dot and IDNA labels. Underscores are allowed in RR owner labels for service records, but not in CNAME/NS/MX/SRV target hostnames. This Skill does not query target existence, follow CNAME chains, inspect DNSSEC, or decide whether a public record should expose a private address.

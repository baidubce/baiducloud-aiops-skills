# API Reference

## Service Boundary

- Product: 百度智能云云智能网（Cloud Smart Network, CSN）.
- Endpoint: `https://csn.baidubce.com`.
- Scope: global; route objects contain their own region/instance metadata.
- Authentication: BCE Signature v1 with AK/SK and optional STS security token.
- This Skill permits only the GET operations below.

## Allowed Operations

| Purpose | Method and path | Pagination | Main list field |
|---|---|---|---|
| List CSNs | `GET /v1/csn` | `marker`, `maxKeys` | `csns` |
| List loaded network instances | `GET /v1/csn/{csnId}/instance` | `marker`, `maxKeys` | `instances` |
| List CSN route tables | `GET /v1/csn/{csnId}/routeTable` | `marker`, `maxKeys` | `csnRts` |
| List associations | `GET /v1/csn/routeTable/{csnRtId}/association` | none documented | `associations` |
| List propagations/learning relations | `GET /v1/csn/routeTable/{csnRtId}/propagation` | none documented | `propagations` |
| List route entries | `GET /v1/csn/routeTable/{csnRtId}/rule` | `marker`, `maxKeys` | `csnRtRules` |

For paginated APIs, `maxKeys` defaults to 1000 and the documented maximum is 1000. Do not invent pagination for association or propagation endpoints.

## Models Used

### Route table

`csnRtId`, `name`, `description`, `type`. Documented types are `default` and `custom`. Current product guidance says creation of a CSN automatically creates a default route table; default and custom route tables are isolated from one another.

### Association and propagation

Both models expose `attachId`, `instanceId`, `instanceName`, `instanceRegion`, `instanceType`, `description`, and `status`. Documented examples use association status `active` and propagation status `enable`; the appendix does not publish complete status enums. Preserve unknown values.

Association selects which CSN route table an attached network instance queries for forwarding. Propagation/learning lets a route table learn routes published by an attached network instance.

### Route rule

Fields include `ruleId`, `routeType`, `csnId`, `csnRtId`, `fromAttachId`, `status`, `sourceAddress`, `destAddress`, next-hop fields, `asPath`, `community`, and `blackHole`.

- Documented route statuses: `active`, `conflicted`.
- A conflict means a later learned duplicate prefix is not effective; the first learned route remains active.
- `blackHole=true` records a route that drops traffic. It can be intentional, so report it without automatic remediation.
- Route types can evolve; preserve unknown values. Current examples show `propagated`, while the create API uses `custom`.

## Coverage Rules

- Continue paginated APIs while `isTruncated` is true; stop with an explicit coverage error if `nextMarker` is missing or repeats.
- Query network instances and route tables for every selected CSN.
- For every route table, independently query associations, propagations and all route entries.
- A failed child query is not equivalent to an empty result.
- Cross-reference `attachId` only when the network-instance query for that CSN succeeded.

## Deliberately Excluded

- No route table, association, propagation, route or network-instance mutation.
- No TGW route endpoint, VPC route table, VPC/TGW binding, route-policy, bandwidth-package or regional-bandwidth query.
- No BGP best-path simulation and no data-plane connectivity test.

## Official Documentation

- CSN list: https://cloud.baidu.com/doc/CSN/s/Ll0ucpv6y
- Network-instance list: https://cloud.baidu.com/doc/CSN/s/nl0unomuo
- Route-table list: https://cloud.baidu.com/doc/CSN/s/hl13gm7x2
- Association list: https://cloud.baidu.com/doc/CSN/s/zl13gcrny
- Propagation list: https://cloud.baidu.com/doc/CSN/s/8l14cgbsf
- Route-rule list: https://cloud.baidu.com/doc/CSN/s/sl14d3at6
- Models: https://cloud.baidu.com/doc/CSN/s/Xl511tehn
- Default/custom route tables: https://cloud.baidu.com/doc/CSN/s/1m9sijc0b
- IAM scope: https://cloud.baidu.com/doc/CSN/s/Bl9e6oq2t

Official pages also link write APIs. Their presence does not authorize use; runtime rejects every method other than GET.

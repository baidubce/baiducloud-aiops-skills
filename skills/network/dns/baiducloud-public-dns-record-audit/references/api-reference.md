# API Reference

## Service Boundary

- Product: 百度智能云智能云解析公网 DNS.
- Endpoint: `https://dns.baidubce.com`.
- Scope: global; no region parameter is required.
- Authentication: BCE Signature v1 with AK/SK and optional STS security token.
- This Skill permits only the two GET operations below.

## Allowed Operations

| Purpose | Method and path | Pagination | Response collection |
|---|---|---|---|
| List public zones | `GET /v1/dns/zone` | `marker`, `maxKeys` (default 1000) | `zones` |
| List records in one zone | `GET /v1/dns/zone/{zoneName}/record` | `marker`, `maxKeys` (default 1000) | `records` |

`name` on the zone-list API is a fuzzy-search parameter. The script lists zones and applies an exact, case-insensitive local filter when `--zones` is used. `rr` and `id` on the record-list API are optional and are intentionally omitted so that audit coverage includes all records.

## PublicZone Fields Used

| Field | Meaning |
|---|---|
| `id` | Zone ID |
| `name` | Domain name |
| `status` | `running`, `unregister`, `nsunchange`, `failed`, or `torenew` |
| `productVersion` | `free`, `discount`, or `flagship` |
| `createTime`, `expireTime` | Beijing-time timestamps returned by the service |
| `tags` | Tag key/value pairs |

## PublicRecord Fields Used

| Field | Meaning |
|---|---|
| `id` | Record ID |
| `rr` | Host record, such as `@`, `www`, or `*` |
| `status` | `running`, `stopped`, or `failed` |
| `type` | `A`, `CNAME`, `MX`, `TXT`, `NS`, `AAAA`, or `SRV` |
| `value` | Record value |
| `ttl` | Positive integer in seconds |
| `line` | Resolution line or line-group name; default line is `default` |
| `description` | Record description |
| `priority` | MX priority, documented range 0 through 50 |

The documented minimum TTL is 300 seconds for `free`, 120 seconds for `discount`, and 1 second for `flagship`. Enterprise zones may use documented detailed line names or custom line-group names, so an unknown non-empty `line` value is not automatically an error.

## Pagination and Coverage

- Continue while `isTruncated` is true and pass `nextMarker` to the same GET request.
- Stop with a coverage error if `nextMarker` is missing or repeats.
- A successful empty `zones` list means the queried credential can see zero public zones.
- A successful empty `records` list means that zone returned zero records.
- A failed list request is not equivalent to an empty list.
- Record queries are tracked per zone; partial success remains visible in the output.

## Official Documentation

- API service domain: https://cloud.baidu.com/doc/DNS/s/3l7q5k5i3
- Zone APIs: https://cloud.baidu.com/doc/DNS/s/kl4s7g11z
- Record APIs: https://cloud.baidu.com/doc/DNS/s/El4s7lssr
- PublicZone/PublicRecord models: https://intl.cloud.baidu.com/zh/doc/DNS/s/Ukk6c64q3-intl
- Product versions and minimum TTL: https://cloud.baidu.com/doc/DNS/s/ojwvyx3em
- IAM policy scope: https://intl.cloud.baidu.com/en/doc/DNS/s/njwvywyto-intl-en

Official pages also document write APIs on the same service. Their presence in the references does not authorize their use; the runtime rejects every method other than GET.

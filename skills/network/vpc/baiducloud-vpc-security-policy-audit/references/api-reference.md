# API and Field Reference

## Endpoint

Use `https://bcc.{region}.baidubce.com`. The script rejects non-HTTPS endpoints, paths embedded in the endpoint, and hosts outside `*.baidubce.com`.

## Read-only calls

| Resource | Method and path | Purpose |
|---|---|---|
| VPC | `GET /v1/vpc` | List VPC IDs for ACL scope |
| Ordinary security group | `GET /v2/securityGroup` | List ordinary groups and nested `rules` |
| Enterprise security group | `GET /v1/enterprise/security` | List enterprise groups and nested `rules` |
| ACL | `GET /v1/acl?vpcId=...` | Read VPC ACL entries and nested `aclRules` |

All list endpoints that expose `isTruncated` and `nextMarker` are paginated with loop protection. No write endpoint is present in the script.

## Rule fields

### Ordinary security group

- Group fields: `id`, `name`, `vpcId`, `rules`.
- Rule fields: `securityGroupRuleId`, `direction`, `ethertype`, `protocol`, `portRange`, `sourceIp`, `destIp`, `sourceGroupId`, `destGroupId`.
- Ordinary security groups are allow-list based. A returned rule is treated as allow unless the API explicitly returns another action.

### Enterprise security group

- Group fields: `id`, `name`, `rules`.
- Rule fields: `enterpriseSecurityGroupRuleId`, `direction`, `ethertype`, `protocol`, `portRange`, `sourcePortRange`, `sourceIp`, `destIp`, `localIp`, `remoteIpSet`, `remoteIpGroup`, `action`, `priority`.
- Priority ranges from 1 to 1000; a smaller number has higher priority. At the same priority, deny takes precedence over allow.

### ACL

- `GET /v1/acl` returns VPC metadata and `aclEntrys` grouped by subnet.
- ACL rule fields: `id`, `subnetId`, `protocol`, `sourceIpAddress`, `destinationIpAddress`, `sourcePort`, `destinationPort`, `position`, `direction`, `ipVersion`, `action`.
- A smaller `position` has higher priority. The script analyzes shadowing only when both rules have parseable protocol, address and port fields.

## Interpretation limits

- `all`, `0.0.0.0/0`, and `::/0` are treated as public/unrestricted addresses.
- Address groups, address families, parameter templates and nested security groups are not expanded by these four APIs. Rules using them are retained in the snapshot but are not declared public without expansion evidence.
- Rule permission does not prove end-to-end reachability. Public IP attachment, route paths, listeners, host firewalls and all security policies affecting the target remain outside this Skill.

## Official references

- Ordinary security group list: https://cloud.baidu.com/doc/VPC/s/Okmd24kom
- Enterprise security group list: https://cloud.baidu.com/doc/VPC/s/Cl5jbuluf
- ACL query: https://cloud.baidu.com/doc/VPC/s/Qjwvyu6w3
- Security group behavior: https://cloud.baidu.com/doc/VPC/s/5mizrmlh4
- VPC API appendix: https://cloud.baidu.com/doc/VPC/s/9jwvyubqq

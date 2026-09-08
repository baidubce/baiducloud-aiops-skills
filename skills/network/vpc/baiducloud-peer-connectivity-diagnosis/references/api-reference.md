# API and Diagnostic Model

## Read-only APIs

All calls use `https://bcc.<region>.baidubce.com` and HTTP GET.

| Resource | Method and path | Purpose |
|---|---|---|
| Peering list | `GET /v1/peerconn` | Discover connections in the requested local region |
| Peering detail | `GET /v1/peerconn/{peerConnId}?role=...` | Obtain status, both VPCs and the endpoint `localIfId` |
| VPC detail | `GET /v1/vpc/{vpcId}` | Confirm endpoint accessibility and VPC CIDRs |
| Subnet list | `GET /v1/subnet?vpcId=...` | Locate flow IPs and build route-coverage targets |
| Route table | `GET /v1/route?vpcId=...` | Read `sourceAddress`, `destinationAddress`, `nexthopType`, `nexthopId` and `nextHopList` |
| ENI list | `GET /v1/eni?vpcId=...` | Map a private IP to ENI and security-group references |
| Ordinary security groups | `GET /v2/securityGroup?vpcId=...` | Read group rules |
| ACL | `GET /v1/acl?vpcId=...` | Read subnet ACL entries and ordered rules |

The client rejects non-GET methods before network I/O, rejects non-HTTPS endpoints, and rejects hosts outside `*.baidubce.com`.

## Endpoint orientation

The list API returns a `role`, `localVpcId`, `localRegion`, `peerVpcId`, `peerRegion`, and `localIfId`. For same-region details, omitting `role` may return either endpoint. Always pass the discovered local role.

To obtain the opposite endpoint view, query the peer region with the opposite role. Treat the returned data as verified only when its `localVpcId` equals the original `peerVpcId`. A cross-account endpoint may return `403` or `404`; preserve the local evidence and mark the remote endpoint unavailable.

## Route matching

Official route fields are:

- `sourceAddress`: source IP or CIDR scope;
- `destinationAddress`: destination IP or CIDR scope;
- `nexthopType`: `peerConn` for a peering route;
- `nexthopId`: the endpoint's local interface ID such as `qpif-...`, not `peerConnId`;
- `nextHopList`: optional multi-path next hops.

For a precise flow, a usable forward route must cover the source IP and destination IP, select `peerConn`, and reference the local endpoint `localIfId`. The reverse endpoint must independently contain a route covering the reversed IP pair and its own local interface ID.

When several rules match, a more-specific destination route to another next hop is a conflict candidate. The script reports the matching set and does not claim to model undocumented tie-breaking behavior.

## Subnets and overlapping CIDRs

百度智能云 supports peering between VPCs whose overall CIDRs overlap. The documented constraint is narrower: the two subnets selected for routed communication must not overlap. Therefore:

- do not flag VPC-level overlap alone;
- in precise mode, flag overlap between the located source and destination subnets;
- in topology mode, list overlapping subnet pairs as planning risks, not proven outages.

## Security policy model

Ordinary security groups are evaluated only when:

1. source/destination IPs, protocol and applicable port are supplied;
2. the IP is found on an ENI;
3. all security-group IDs referenced by that ENI are present in the successful group query;
4. rule address/protocol/port fields are parseable.

The script searches source ENI egress and destination ENI ingress allow rules. A matching allow is evidence in favor of the path. No matching rule is a blocking candidate only under the complete conditions above.

ACL rules are evaluated for source-subnet egress and destination-subnet ingress. Rules are ordered by numeric `position`; the first fully matching rule determines the reported action. Missing or unparseable rules yield `unknown` rather than an allow/deny assertion.

Enterprise security groups, security-group nesting, IP sets/groups, host firewalls, application listeners and return-traffic state are not fully resolved by these APIs. If such references are detected, lower the conclusion confidence.

## Coverage states

- `success`: query succeeded, including a legitimate empty result;
- `partial`: some records or nested fields were unavailable;
- `failed`: the query was attempted but failed;
- `blocked`: a prerequisite failed, so the query was not attempted;
- `notApplicable`: the endpoint or precision input does not apply;
- `unknown`: imported offline data does not prove collection status.

Never translate `failed`, `blocked`, or `unknown` into “resource absent”.

## Official references

- 对等连接列表: https://cloud.baidu.com/doc/VPC/s/Fjwvyuemr
- 对等连接详情: https://cloud.baidu.com/doc/VPC/s/Sjwvyudwm
- 对等连接操作指导（两端路由）: https://cloud.baidu.com/doc/VPC/s/8jwvyu0me
- 对等连接典型实践（重叠 CIDR 与路由）: https://intl.cloud.baidu.com/zh/doc/VPC/s/hjwvyu3s0-intl
- 查询路由表: https://cloud.baidu.com/doc/VPC/s/jjwvyuh0v-en
- 路由规则字段与对等连接下一跳: https://cloud.baidu.com/doc/VPC/s/Ljwvyugpl
- 查询子网列表: https://cloud.baidu.com/doc/VPC/s/xjwvyu8zu
- 查询指定 VPC: https://cloud.baidu.com/doc/VPC/s/yjwvyuaeo
- 查询普通安全组: https://cloud.baidu.com/doc/VPC/s/Okmd24kom
- 查询 ACL: https://cloud.baidu.com/doc/VPC/s/Qjwvyu6w3
- VPC 数据模型: https://cloud.baidu.com/doc/VPC/s/9jwvyubqq

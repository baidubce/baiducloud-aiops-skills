# RAM Policies

## Required Permissions

Use a dedicated IAM sub-user or STS credential. Attach only the official read-only system policies required by the selected diagnosis depth.

| Resource | Official read-only system policy | Purpose |
|---|---|---|
| Peering connection | `PEERCONNReadPolicy` | List connections and read both endpoint views when the account can access them |
| VPC | `VpcReadOnlyAccessPolicy` | Confirm local and peer VPC metadata |
| Subnet | `SubnetReadOnlyAccessPolicy` | Locate source/destination IPs and derive route-coverage targets |
| Route table | `RouteReadOnlyAccessPolicy` | Read source, destination, next-hop type and next-hop ID |
| Elastic network interface | `ENICReadOnlyAccessPolicy` | Map a private IP to its ENI and attached ordinary security-group IDs |
| Standard security group | `SecurityGroupReadOnlyAccessPolicy` | Read ordinary security-group rules for a precisely mapped ENI |
| ACL | `AclReadPolicy` | Read subnet ACL rules and their priority order |

`PEERCONNReadPolicy`, `VpcReadOnlyAccessPolicy`, `SubnetReadOnlyAccessPolicy`, and `RouteReadOnlyAccessPolicy` are the minimum useful set for topology and route diagnosis. ENI, security-group, and ACL policies are needed only for precise flow-policy evidence.

## Recommended RAM Policy

Prefer the official system policies above because 百度智能云 maintains their action sets as APIs evolve.

If a custom policy is mandatory, start with this read-only template and verify permission identifiers in the target IAM console. If an identifier is rejected, use the corresponding official read-only policy rather than granting operate or full-control access.

```json
{
  "version": "v1",
  "accessControlList": [
    {
      "service": "bce:network",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "PEERCONN_READ",
        "VPC_READ",
        "SUBNET_READ",
        "ROUTE_READ",
        "ENIC_READ",
        "SECURITY_GROUP_READ",
        "ACL_READ"
      ]
    }
  ]
}
```

## Notes

- Do not grant `PEERCONNOperatePolicy`, `PEERCONNFullControlPolicy`, or any VPC sub-product operate/full-control policy for this Skill.
- Do not grant create, accept, reject, update, delete, bind, unbind, attach, detach, authorize, revoke, resize, renew or DNS-change permissions.
- Cross-account peer VPC resources normally cannot be read with the local account credential. Mark that endpoint unverified; do not request the other account's long-lived key merely to complete one report.
- A `403` is a permission gap, not evidence that a route, subnet, ENI, security group or ACL does not exist.
- Keep credentials outside the Skill package. A local JSON credential file must be owner-only and permission `600`.

## Official Reference

- 百度智能云 VPC 多用户访问控制: https://cloud.baidu.com/doc/VPC/s/2jwvytwrr

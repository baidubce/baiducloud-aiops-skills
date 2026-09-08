# RAM Policies

## Required Permissions

Use a dedicated IAM sub-user or STS credential. Grant only the official read-only system policies required for the selected audit scope.

| Resource | Official read-only system policy | Purpose |
|---|---|---|
| VPC | `VpcReadOnlyAccessPolicy` | List VPC IDs so ACL queries can be scoped correctly |
| Standard security group | `SecurityGroupReadOnlyAccessPolicy` | List ordinary security groups and their rules |
| Enterprise security group | `ESGReadAccessPolicy` | List enterprise security groups and their rules |
| ACL | `AclReadPolicy` | Read subnet-level ACL entries and rules |

The official system policies are preferred because 百度智能云 maintains their action sets as APIs evolve. Do not attach operate or full-control policies for this Skill.

## Recommended RAM Policy

When a custom policy is mandatory, use the following minimum read-only template. Validate permission identifiers in the target IAM console before assignment; if an identifier is rejected, use the official system policies above instead of substituting an operate permission.

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
        "VPC_READ",
        "SECURITY_GROUP_READ",
        "ESG_READ",
        "ACL_READ"
      ]
    }
  ]
}
```

## Notes

- Do not grant permissions containing `OPERATE`, `FULL_CONTROL`, create, update, delete, authorize, revoke, bind, unbind, attach, or detach semantics.
- Replace the wildcard region with the audited region when the IAM policy editor supports regional scoping.
- Narrow the resource scope when the audit covers named VPCs only and instance-level authorization is supported.
- A successful ordinary security group query does not imply permission to query enterprise security groups or ACLs; attach each read-only system policy explicitly.
- A `403` produces partial coverage. Do not describe a partial report as a complete account audit.
- Keep credentials outside the Skill package. If a local JSON file is used, restrict it with `chmod 600` and delete it when no longer required.

## Official Reference

- 百度智能云 VPC 多用户访问控制: https://cloud.baidu.com/doc/VPC/s/2jwvytwrr

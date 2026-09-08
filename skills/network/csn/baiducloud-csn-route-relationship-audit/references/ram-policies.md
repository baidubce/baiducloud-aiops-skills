# RAM Policies

## Required Permissions

Use a dedicated IAM sub-user or STS credential. Grant only the official read-only system policy required by this Skill.

| Resource | Official read-only system policy | Purpose |
|---|---|---|
| Cloud Smart Network | `CSNReadOnlyAccessPolicy` | List CSNs and read network-instance and route-control-plane configuration |

This Skill does not require operate/full-control, attach/detach, route-change, bandwidth-package, regional-bandwidth, VPC or TGW mutation permissions.

## Recommended RAM Policy

Prefer the official `CSNReadOnlyAccessPolicy`, because 百度智能云 maintains its exact action set as APIs evolve. If a custom policy is mandatory, start with this minimum read-only template:

```json
{
  "version": "v1",
  "accessControlList": [
    {
      "service": "bce:csn",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "CSN_READ"
      ]
    }
  ]
}
```

The public guide names the system policy and visual policy generator but does not publish raw custom-policy identifiers. Validate `service` and `permission` in the target IAM console before assignment. If rejected, use `CSNReadOnlyAccessPolicy`; do not substitute `CSNOperateAccessPolicy` or `CSNFullControlPolicy`.

## Notes

- Never grant create, update, delete, attach, detach, associate, propagate, route-change, bandwidth-change, `OPERATE`, or `FULL_CONTROL` semantics for this Skill.
- The public IAM table summarizes read-only CSN access but does not enumerate every route-query action. Verify route-table, association, propagation and route-list GET coverage with the restricted identity before production use.
- A `403` is a coverage gap, not proof that a relationship or route does not exist.
- Keep credentials outside the Skill package. Prefer temporary STS credentials. If a JSON credential file is required, restrict it with `chmod 600` and pass only its path through `--credentials-file`.

## Official Reference

- 百度智能云 CSN 多用户访问控制: https://cloud.baidu.com/doc/CSN/s/Bl9e6oq2t

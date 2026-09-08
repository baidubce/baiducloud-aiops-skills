# RAM Policies

## Required Permissions

Use a dedicated IAM sub-user or STS credential. Grant only the official read-only policy required by this Skill.

| Resource | Official read-only system policy | Purpose |
|---|---|---|
| Intelligent Cloud public DNS | `DNSReadPolicy` | Query the public-domain list and view resolution records |

This Skill does not require `DNSOperatePolicy`, `DNSFullControlPolicy`, `LDReadPolicy`, or resolver permissions.

## Recommended RAM Policy

Prefer the official `DNSReadPolicy`, because 百度智能云 maintains its exact action set as the service evolves. The following JSON is a minimum read-only custom-policy template for environments that require a custom policy:

```json
{
  "version": "v1",
  "accessControlList": [
    {
      "service": "bce:dns",
      "region": "*",
      "resource": [
        "*"
      ],
      "effect": "Allow",
      "permission": [
        "DNS_READ"
      ]
    }
  ]
}
```

Custom-policy identifiers are not enumerated in the public DNS guide. Validate `service` and `permission` in the target IAM visual editor before assignment. If the editor rejects either identifier, attach the official `DNSReadPolicy`; do not replace it with an operate or full-control policy.

## Notes

- Do not grant `DNSOperatePolicy` or `DNSFullControlPolicy` for this Skill.
- Do not grant permissions with create, update, enable, disable, renew, upgrade, delete, `OPERATE`, or `FULL_CONTROL` semantics.
- Public DNS is a global service, so the script has no region selector. Keep `region: "*"` unless the IAM editor documents a narrower applicable scope.
- If instance-level authorization is required, select only the intended public DNS zones in the IAM visual editor and confirm both zone-list and record-list access.
- A successful zone-list query does not prove every record-list query succeeded. Review per-zone coverage.
- A `403` is a coverage gap, not proof that a zone or record does not exist.
- Keep credentials outside the Skill package. Prefer short-lived STS credentials. If a JSON credential file is required, restrict it with `chmod 600` and pass only its path through `--credentials-file`.

## Official Reference

- 百度智能云 DNS Identity and access management: https://intl.cloud.baidu.com/en/doc/DNS/s/njwvywyto-intl-en

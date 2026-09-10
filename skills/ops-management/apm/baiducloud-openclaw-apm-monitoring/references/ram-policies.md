# RAM Policies

## Required Permissions

This skill modifies the current user's local OpenClaw configuration and writes telemetry to the APM trace receiver selected by the user. It does not call Baidu Cloud resource management APIs or create applications, cloud instances, or IAM/RAM policies.

| Permission | Service | Resource | Description |
| --- | --- | --- | --- |
| Trace ingestion access granted by the receiver | APM trace receiver | User-provided endpoint | The complete user-provided auth authorizes telemetry writes; this is not a RAM action created by the skill. |
| Additional RAM permissions: none | N/A | N/A | Local configuration, plugin installation, Gateway restart, and native request verification do not require additional cloud resource management permissions. |

## Recommended RAM Policy

No new RAM policy is required. Do not invent actions, supply empty authorization JSON, or recommend administrator access.

If the user also requests verification in the console, use their existing APM application viewing permissions. Missing query access does not block endpoint/auth configuration, but APM receipt must remain unverified.

## Notes

- The local account must be able to write the active configuration, install the official plugin, and restart the corresponding Gateway.
- Auth must belong to the target receiver, account, and region. The skill does not generate, decode, or expand its permissions.
- Configuration and backups contain auth. Keep them in the current user's private directories and out of the skill ZIP.

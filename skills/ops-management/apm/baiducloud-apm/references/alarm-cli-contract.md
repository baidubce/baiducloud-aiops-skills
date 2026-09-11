# APM and LLM alarm CLI contract

Use the existing `bce apm` operations and re-read operation help at runtime.

## Operations

| Intent | CLI operation |
|---|---|
| create policy | `ApmCreateAlarmPolicy` |
| list policies | `ApmDescribeAlarmPolicies` |
| policy detail | `ApmDescribeAlarmPolicy` |
| update policy | `ApmUpdateAlarmPolicy` |
| enable/disable policies | `ApmUpdateAlarmPolicyState` |
| update notification actions | `ApmUpdateAlarmPolicyAction` |
| delete policies | `ApmDeleteAlarmPolicy` |
| list alarm events | `ApmDescribeAlarms` |
| alarm event detail | `ApmDescribeAlarm` |

List APIs use `pageNo/pageSize`; the CLI does not advertise generic `--pager` for these operations. Loop manually and bound the result.

Alarm actions can contain callback URLs with embedded access tokens. Every list/detail/read-back command must use a minimal `--query` output projection that retains only fields such as `code`, `success`, `requestId`, policy `id/name/state/metricKind`, target type/services/tags, rules, filters, and `actions[].notifyId`. Never include full callback URLs, callback headers, or arbitrary action payloads in terminal output, saved fixtures, or reports.

Current `ApmDescribeAlarmPolicies --help` may omit `LLM` and `LLM_OPERATION` from its `metricKind` filter enumeration even though the service can return policies of those kinds. Do not use a client-side help omission to discard a server-returned policy; omit that list filter and safely project/filter the response when necessary.

APM alarm actions reference shared BCM notification-template IDs. Resolve them read-only with `bce bcm DescribeNotifyTemplates` and `bce bcm DescribeNotifyTemplate`. This Skill must not create, update, or delete BCM notification templates.

## Create/update shape

Create contains:

- `name`, `state`;
- `target {type,tags,services}`;
- `metricKind`, `rule`, `filters`;
- `pendingCount`, re-notification fields, recovery and missing-data fields;
- `level`, `actions`.

Update has the same semantic fields plus exact policy `id`, but it does not accept `state`. State changes use `ApmUpdateAlarmPolicyState`. Generate the current skeleton before every create/update because nested action fields may evolve.

## Safe create/update protocol

```bash
bce apm ApmCreateAlarmPolicy --help
bce apm ApmCreateAlarmPolicy --generate-cli-skeleton
python3 <skill-directory>/scripts/validate_alarm_policy.py \
  --operation ApmCreateAlarmPolicy /absolute/policy.json
bce apm ApmCreateAlarmPolicy --region <region> \
  --cli-input-json file:///absolute/policy.json --dry-run
```

After the user confirms the rendered target, rule, state, and actions, repeat the same command without `--dry-run`. Then retrieve the returned/exact policy ID with `ApmDescribeAlarmPolicy` through a safe projection and compare every intended non-secret field.

For update, use `--operation ApmUpdateAlarmPolicy`; require a non-empty `id` and omit `state`. For create, require `state` and omit `id`.

Do not manually pass API `action` or `version` fields.

Inspect Dry Run before mutation because installed CLI metadata determines the endpoint and scheme. If transport must be encrypted, stop until a trusted/private route or an approved HTTPS-capable endpoint/CLI is available. Do not silently downgrade an explicitly supplied HTTPS endpoint.

## State, action, and delete protocol

Before `ApmUpdateAlarmPolicyState`, `ApmUpdateAlarmPolicyAction`, or `ApmDeleteAlarmPolicy`:

1. resolve every ID to current name, target, state, and notification actions;
2. show the complete affected set;
3. obtain confirmation immediately before execution;
4. execute once;
5. read back every affected policy, or verify absence after deletion.

Do not retry an ambiguous timed-out mutation. Read state first because the server may already have applied it.

## Baseline queries

Alarm evaluator names differ from APM/LLM query names. Use only the explicit query equivalents in `alarm-catalog.md`, and only for threshold evidence. Query results do not prove the evaluator's internal implementation.

Threshold design should show the selected time range, current aggregate, tail or peak where relevant, comparison period, unit conversion, and business tolerance. Never ship a placeholder threshold or notification template from an example.

## Error and audit behavior

- Authentication/permission/validation errors are not retryable by guessing alternate fields.
- Preserve service `requestId` in success/failure summaries when available.
- Do not use `--debug` by default; action payloads and signed headers can be sensitive.
- For updates, retain a redacted prior-state snapshot in the task response for rollback planning, but do not persist callbacks or credentials in repository files.
- If raw callback data is accidentally displayed, do not quote it in the audit response. Treat embedded URL/path/query tokens as exposed and recommend credential rotation.
- A mutation is complete only after read-back verification.

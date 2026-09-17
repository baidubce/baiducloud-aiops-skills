# BCM V3 alarm-masking CLI contract

## Supported operations

| Intent | BCE CLI operation |
| --- | --- |
| list masking rules | `DescribeAlarmMaskings` |
| read one masking rule | `DescribeAlarmMasking` |
| create | `CreateAlarmMasking` |
| update | `UpdateAlarmMasking` |
| enable or disable | `UpdateAlarmMaskingStates` |
| delete | `DeleteAlarmMaskings` |

Treat an operation as available when it appears in the installed `bce bcm --help` and its own `--help`/`--generate-cli-skeleton` output. Do not infer support from a numeric CLI version alone.

## CLI request shape

For BCE CLI input, each instance has `dimensions`, not `identifiers`, and the business region is a required top-level field shared by every instance:

```json
{
  "name": "maintenance-window",
  "scope": "BCE_CFS",
  "resourceType": "Instance",
  "instances": [
    {
      "dimensions": [
        {"key": "FsId", "value": "<protected-instance-id>"}
      ]
    }
  ],
  "region": "bj",
  "periodType": "FOREVER"
}
```

Current downloaded OpenAPI examples use `instances[].identifiers` and may show an instance-level `region`, while current BCE CLI help, skeleton, and V3 dry-run use `instances[].dimensions` plus the top-level `region`. Because this package executes BCE CLI, use the installed CLI shape. Do not copy the raw OpenAPI example into `--cli-input-json`.

Do not include `version` or `action` in request JSON. Selecting the installed operation routes the request; verify that `--dry-run` resolves `/v3/bcm` and the intended action before confirmation.

Instance dimension values follow the same resource-access boundary as alarm-policy targets: require them from the user, a user-selected existing BCM policy or masking rule, an exact alarm record used for diagnosis, or a BCM instance group. Query `DescribeMetricCatalogs` for the exact confirmed `scope/resourceType` and use its response to validate dimension keys and required resource identifiers. This structural check cannot prove that an instance exists. Do not call another cloud-product API automatically.

`metricNames` is optional. An omitted or empty list applies no metric-name filter. When it is present, resolve every name exactly from current metadata and remove duplicates. `policyId` is optional; if supplied, resolve and display the exact policy before mutation.

## Time modes

- `FOREVER`: omit fixed and daily time fields.
- `FIXED`: provide RFC3339 `beginTime` and `endTime` with timezone; `endTime` must be later.
- `RELATIVE`: provide `dailyBeginTimestamp` and `dailyEndTimestamp` as milliseconds from local midnight, satisfying `0 <= begin < end <= 86400000`. Set an explicit IANA `tz` when the intended timezone matters; omission uses the service default `Asia/Shanghai`. An optional `beginTime`/`endTime` pair can bound the overall recurring period when supported by current operation help.

Use `validate_alarm_masking.py` before a mutation:

```bash
python3 scripts/validate_alarm_masking.py <request.json> \
  --operation CreateAlarmMasking \
  --metric-catalog <describe-metric-catalogs-response.json>
```

`--metric-catalog` is required for create and update validation. Batch state changes and deletes use exact masking IDs and do not require metric metadata.

## Safe execution

1. Inspect the exact operation help and generate a current skeleton.
2. Resolve exact scope, resource type, instance dimensions, business region, optional policy, metrics, and time mode.
3. Check for a semantically equivalent masking rule with a bounded `DescribeAlarmMaskings` query and exact detail reads.
4. Validate JSON with `validate_alarm_masking.py`.
5. Run the exact command with `--dry-run`; verify `/v3/bcm`, the action, top-level region, instance count, time mode, and absence of unexpected fields.
6. Show affected rule IDs, protected target summary, metric/policy scope, period, initial or resulting state, and rollback action.
7. Obtain confirmation immediately before the mutation, execute once, then read back every intended non-secret field by exact ID.

Create has no input `state` field and the new masking rule is enabled immediately. Update requires the current complete CLI shape plus exact `id` and `state`. Batch state and delete operations require non-empty, duplicate-free exact ID lists.

For a timed-out mutation, use the reconciliation procedure in [alarm-policy-cli-contract.md](alarm-policy-cli-contract.md). Never retry automatically.

## Failures and output

On authentication or authorization failure, stop immediately. Report the exact operation, a redacted service error code/message, and `requestId` when returned. Do not retry, alter the selected profile, inspect credentials, or propose permissions; the user must resolve access.

Do not display raw instance values, callback data, account IDs, or credentials. A `requestId` is diagnostic evidence, not an idempotency token.

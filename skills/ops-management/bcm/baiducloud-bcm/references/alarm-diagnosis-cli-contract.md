# BCM alarm diagnosis CLI contract

## Read operations

| Intent | Operation |
| --- | --- |
| list alarm history | `DescribeAlarms` |
| alarm detail | `DescribeAlarm` |
| policy detail | `DescribeAlarmPolicy` |
| metric catalog/data | `DescribeMetricCatalogs`, `DescribeMetricData` |
| notification template | `DescribeNotifyTemplate` |
| recorded resource context | `DescribeAlarm`, exact selected `DescribeAlarmPolicy`, or user-provided evidence |

`DescribeAlarms` uses `pageNo/pageSize`; iterate explicitly and honor the requested bound. Query a narrow time range first. Use minimal output projection before displaying data so arbitrary notification actions and callback details never enter output.

For the current online contract, `orderBy` accepts `createdTime` or `updatedTime`. `startTime` and `endTime` are time filters, not valid sort fields. Prefer exact `policyId` when diagnosing one policy; `policyName` is fuzzy. The CLI/runtime may accept `--policyId` even when current operation help omits that flag, so re-check both help and a read-only request after a CLI or backend upgrade rather than silently falling back to a fuzzy name.

Metric request JSON for `DescribeMetricData` must contain a non-empty `region`. For alarm replay, this normally comes from the event resource's business region. Global profile/CLI `--region` still selects the endpoint and remains separate. Metric request JSON must not contain generated `version` or `action` fields.

## Safe projections

Retain only fields required for diagnosis, such as:

- alarm `id`, `seriesId`, `state`, `startTime`, `endTime`;
- resource `scope`, `resourceType`, `region`, identifiers;
- policy `id`, `name`, update time, target type, rules, pending/no-data fields, `notifyEnabled`, action template IDs;
- alert metric name, value, threshold, operator, trigger count;
- service `code`, `message`, `requestId`.

Do not display receiver phones/emails, callback URLs, headers, query strings, tokens, or full raw action payloads. Avoid `--debug`.

## Failure handling

Authentication, permission, invalid parameter, missing policy, and identifier mismatch errors are not retryable by guessing. Retry a read timeout or 5xx at most once with the same validated request. Preserve `requestId`. Never fabricate missing historical points or silently reinterpret an empty response as zero.

`DescribeAlarms` uses the separately routed `/v3/bcm/ah` path. If policy reads on
`/v3/bcm` succeed but the same validated history request repeatedly returns a
gateway 5xx, record the dry-run path and every `requestId`, then classify the
history backend or path routing as unavailable. Do not interpret the failure as
an empty alarm list, alter the policy, switch fields or endpoints by guesswork,
or claim that evaluation did not occur. Conversely, `code=OK`, `success=true`,
and `totalCount=0` is a valid empty result; after proving the trigger windows,
route that case to pipeline troubleshooting instead of blaming history routing.

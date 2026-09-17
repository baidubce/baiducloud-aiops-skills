# BCM alarm diagnostic workflow

## Evidence graph

```text
DescribeAlarms
  -> DescribeAlarm
      -> resource scope/type/region/identifiers
      -> policy id/name
      -> alert metric/value/threshold/operator
  -> DescribeAlarmPolicy
      -> target and effective OR/AND rule
      -> pending, no-data, notification configuration
  -> DescribeMetricCatalogs
      -> exact metric, identifiers, dimensions, native period, unit
  -> DescribeMetricData
      -> current/previous windows and recovery trend
  -> optional user-provided current resource evidence
      -> current lifecycle state or product-side eligibility
```

Treat each edge as a join that can fail. Do not silently join by a partial name, translated label, or case-insensitive identifier.

## Time-window construction

For a static condition, retrieve at least:

```text
windowSeconds + (pendingCount - 1) * effectiveCheckInterval
```

before the recorded trigger, plus one or more check intervals after it for recovery. `effectiveCheckInterval = max(60, checkIntervalSeconds)`.

For an `INC_RATE_*` or `DEC_RATE_*` condition, include one additional `windowSeconds` before that range because the evaluator reads the immediately previous aggregation window.

Align query periods to metric native period and evaluator cadence. Use UTC and state exact inclusive/exclusive assumptions; service query and evaluator windows may not have identical boundary behavior.

## State-oriented questions

### ALERT

Verify exact policy version, branch, every AND condition, aggregation, threshold, and consecutive windows. One above-threshold point does not prove a `pendingCount > 1` trigger.

### OK or CLOSED

Find the first non-alert evaluation after the active alarm and distinguish metric recovery from policy disable/update, resource deletion, or manual closure.

### NO_DATA

Check last observed point, metric native period, effective check interval, `noDataNotifyPendingMinutes`, ingestion delay, resource state, policy update, and scope/region-wide symptoms. The platform may suppress correlated NO_DATA output; absence of a record is not proof of healthy data flow.

### Notification not received

First separate evaluation from delivery. Confirm an alarm-history record exists, then check `notifyEnabled`, action template IDs, silence periods, channel availability, receiver membership, callbacks, renotify limits, and action result status. Never expose full callback URLs or receiver contact details.

## Resource context

Use event resource identifiers as the historical identity. Resources may have changed since the alarm. If identifier keys differ only in case from current metadata, report the mismatch and require an authoritative mapping rather than rewriting them silently.

Do not proactively call another cloud product for enrichment or validation. For a synthetic trigger test or successful-empty history investigation, current product existence remains an admission requirement, but the evidence must be supplied by the user or obtained only after a separate explicit request authorizes the exact product-side read. A 404/deleted resource can be filtered into the instance-deleted/CLOSED path after metric evaluation, so the absence of AlarmHouse history must not be attributed to the evaluator while eligibility is unverified. Metric visibility for the same identifier does not establish product-resource existence.

## Evidence quality

Prefer, in order:

1. recorded alarm and exact policy read-back;
2. current metadata and raw metric query;
3. user-provided or separately authorized current resource evidence;
4. inference.

Always state pagination coverage, query time range, metric unit, period, aggregation, and missing data.

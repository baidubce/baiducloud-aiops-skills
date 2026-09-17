# BCM alarm rule semantics

These rules reflect the current BCM manager API contract and alarm evaluator implementation.

## Boolean structure and cadence

- Each element of `rules` is an OR branch.
- Conditions within one `rules[].conditions` list are ANDed.
- `rules[].pendingCount` is the number of consecutive alert windows required for that OR branch. It is the value read by the evaluator.
- Top-level `pendingCount` is stored for compatibility but is not read by the current evaluator. Keep it positive because the API requires it; normally mirror the first OR branch and warn when OR branches use different counts.
- `rules[].checkIntervalSeconds` sets the evaluation alignment, but the evaluator applies `max(60, checkIntervalSeconds)`. Use at least 60 seconds.
- `conditions[].windowSeconds` controls the aggregation window and must be positive. A rate operator also reads the immediately preceding window, so it needs two windows of data.

## Operators

Static comparisons:

```text
>  >=  <  <=  =  !=
```

Adjacent-window percentage comparisons:

```text
INC_RATE_GT  INC_RATE_GE  INC_RATE_LT  INC_RATE_LE  INC_RATE_EQ  INC_RATE_NE
DEC_RATE_GT  DEC_RATE_GE  DEC_RATE_LT  DEC_RATE_LE  DEC_RATE_EQ  DEC_RATE_NE
```

For rate operators, the evaluator first computes:

```text
changePercent = 100 * (current - previous) / abs(previous)
```

`INC_RATE_*` compares `changePercent`; `DEC_RATE_*` compares its negative. If the previous value is effectively zero, the evaluator does not produce a comparison result. Rate thresholds and `displayUnit` are percentages.

Equality uses a tolerance near `1e-6`; it is not exact floating-point identity.

## Aggregation

Supported values are `MAX`, `MIN`, `SUM`, and `AVG`.

- `MAX` selects the maximum sample/statistic in the window.
- `MIN` selects the minimum.
- `SUM` adds sample/statistic sums.
- `AVG` divides accumulated sum by accumulated sample count; it is a weighted average when source statistics carry counts.

Do not approximate a weighted `AVG` by averaging already averaged points unless their counts are equal. Use catalog native period and raw unit. `windowSeconds` should be at least the native period; prefer a multiple.

## Dimensions and targets

`conditions[].metricDimensions` supports only `=` and `!=`, non-empty values, and AND semantics. The evaluator attempts these keys against metric dimensions and then resource identifiers. Keep them within the union of the selected catalog metric's `metricDimensions` and `resourceIdentifiers`.

Target semantics:

- instances: OR across entries; AND across dimensions inside an entry;
- tags: OR across configured tags;
- instance groups: OR across group IDs;
- including dimensions: AND-presence check;
- excluding dimensions: rejects on any presence.

## No-data and notification

- `IGNORE`: do not request a user-visible no-data state.
- `SHOW_NO_DATA_AND_NOTIFY`: emit a NO_DATA state after `noDataNotifyPendingMinutes`, subject to platform suppression and notification settings.
- `SHOW_OK`: map missing data to OK.
- `notifyEnabled=false` disables delivery, not evaluation or history persistence.

The platform can suppress large correlated NO_DATA waves by scope and resource region. Therefore, an absent user-visible NO_DATA record does not prove that an individual metric stream remained healthy.

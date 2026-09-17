# BCM metric query semantics

## Operation selection

| Need | Operation | Required time fields | Aggregation shape |
| --- | --- | --- | --- |
| Trend over a window | `DescribeMetricData` | `beginDatetime`, `endDatetime` | Non-empty list of `avg`, `sum`, `max`, `min`, `count` when supplied |
| Latest values | `DescribeMetricDataLatest` | `endDatetime` | Non-empty list of `avg`, `sum`, `max`, `min`, `count` when supplied |
| Latest TopN ranking | `DescribeMetricDataLatestTop` | `endDatetime` | One string: `avg`, `sum`, `max`, or `min` |
| Values of a dimension | `DescribeDimensionValues` | `beginDatetime`, `endDatetime` | None |

`DescribeMetricDataLatestTop` does not accept `resourceType` in its request body. The validator still requires `--resource-type` as local metadata context so that identifiers and dimensions can be checked against the correct catalog response.

## Trend limits

For `DescribeMetricData`:

- Use strict UTC timestamps and require `beginDatetime < endDatetime`.
- Keep the time range at or below 31 days.
- Keep the estimated points per curve at or below 1440: `ceil(rangeSeconds / periodSeconds)`.
- Set `periodSeconds` to a positive integer no smaller than the native catalog period. Prefer a multiple of the native period.
- If the catalog has a positive `period` and an empty `periodUnit`, the validator treats it as seconds and reports a compatibility warning; do not suppress that warning in the result.
- If `periodSeconds` is omitted, the service selects one according to the range. State that the exact point count was not precomputed.

`limit` controls returned curves, not data points. Its valid range is 1 through 100. `offset` is zero or greater.

## Latest and TopN

`DescribeMetricDataLatest` evaluates a rolling window of `periodSeconds` ending at `endDatetime`; it is not an unbounded search for the last historical sample. A curve can therefore be empty when its last raw point is older than that window, even though `DescribeMetricData` returns the point in a wider trend range. It supports `limit`, `offset`, a positive `periodSeconds`, and list-valued time aggregation. The returned point timestamp is the instant-query evaluation time, not necessarily the raw sample timestamp.

`DescribeMetricDataLatestTop` ranks matching curves over the same rolling window ending at `endDatetime`. `limit` is 1 through 100. `asc=false` means highest first and `asc=true` means lowest first. It accepts scalar aggregation and has no `offset`. Curves without a raw point inside the window are absent from the ranking.

Neither operation turns an absent sample into zero. State the end time, period, aggregation, sort direction, and number of returned curves.

## Dimension values

Use `DescribeDimensionValues` only for a dimension declared by the selected metric's `metricDimensions`. The request must include the exact metric name, strict UTC range with `beginDatetime <= endDatetime`, and resource identifier filters. Add previously selected metric-dimension filters for cascading discovery only when each key is declared by the metric.

## Interpretation

- Preserve catalog `unit` and response values exactly. If converting for display, show both raw and converted units.
- Time aggregation is not interchangeable across metric types. For example, `sum` may be meaningful for counts but misleading for gauges unless the service definition says otherwise.
- A missing point, empty curve, or empty response is unknown/no data, not measured zero.
- Compare series only when metric name, filters, period, aggregation, unit, and aligned time windows are compatible.
- Record pagination coverage and do not claim a fleet-wide result from a truncated page.

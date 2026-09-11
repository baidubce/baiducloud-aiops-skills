# APM query and diagnosis CLI contract

The Skill depends on the existing `bce` CLI. Re-read operation help at runtime because CLI metadata can change independently of this Skill.

## Supported read operations

| Operation | Use |
|---|---|
| `DescribeServicesNames` | resolve services, IDs, language, environment, source, and tags |
| `DescribeServicesMetrics` | compare service-level headline metrics |
| `DescribeEnv` | list environments |
| `DescribeMetricData` | direct Prom-derived APM/runtime metrics |
| `DescribeDimensionValues` | direct metric dimension discovery |
| `DescribeTraceMetricData` | Trace-semantic metric aggregation |
| `DescribeSpanFieldValues` | public Span-field discovery |
| `DescribeSpans` | Span search; supports marker paging and CLI `--pager` |
| `DescribeTrace` | Trace detail/tree |
| `DescribeExceptions` | batch exception detail after discovering exception IDs |
| `DescribeDbStatement` | batch database statement detail after discovering statement IDs |
| `DescribeTopology` | service/global topology |
| `DescribeServiceConfig` | read slow-request and related application settings |

`DescribeDefaultConfig` and `DescribeRetentionLimit` may explain defaults and retention. This Skill must not invoke `UpdateServiceConfig`, `BindServiceTag`, or `DeleteServices`.

## Direct metric request

`DescribeMetricData` uses:

- `metrics[]`: `{name, compareTo[], filters[]}`.
- strict UTC `beginDatetime`, `endDatetime`.
- top-level `filters[]` with `{key, op, value|values}`.
- `groupBy[]`, `orderBy`, `order`, `limit`, `periodSeconds`, `reserveEmptyDimensions`.

Controller-supported filter operators:

- single value: `=`, `!=`, `contains`, `not contains`;
- multiple values: `in`, `not in`, `notIn`, with a non-empty `values` array.

Do not generate the `:`, `<`, `<=`, `>`, or `>=` operators shown by some CLI help versions for this operation.

`DescribeDimensionValues` filters require a non-empty `values` array; when `op` is omitted the current controller defaults it to `in`.

## Trace metric request

`DescribeTraceMetricData` uses:

- `metrics[]`: `{name}`;
- strict UTC `beginDatetime`, `endDatetime`;
- top-level public Trace `filters[]`;
- `groupBy[]`, `periodSeconds`, and optional `aggregate[]`.

Use only top-level filters for predictable Prom/BLS/Doris routing. If `aggregate` is present, request one metric of one unit; allowed aggregate names are `sum` and `sumPerSecond`.

Each `metrics[]` item contains only `name`; metric-level filters are not part of this operation. Public DB fields use the full `attributes.db.*` form, for example `attributes.db.name`, never the direct Prom label `db.name`.

## CLI pattern

```bash
bce apm <Operation> --help
bce apm <Operation> --generate-cli-skeleton
python3 <skill-directory>/scripts/validate_apm_request.py --operation <Operation> /absolute/request.json
bce apm <Operation> --region <region> \
  --cli-input-json file:///absolute/request.json --output json
```

Do not manually pass `version` or `action`. A skeleton may contain those fields, but operation routing supplies them.

Inspect Dry Run before execution because installed CLI metadata determines the endpoint and scheme. If the request would cross an untrusted public network, stop and require a trusted/private path or an approved HTTPS-capable endpoint/CLI. Never silently downgrade an explicitly supplied HTTPS endpoint.

## Paging and limits

- `DescribeSpans` exposes `--pager` and `--total-count`, but sandbox testing showed that the first server page can exceed a smaller `--total-count`. Treat it as a soft client bound, project and slice the displayed rows to the requested count, and preserve a returned `nextMarker` when stopping early.
- With an exact `traceId` or another narrow filter, request one page first. Do not enable automatic paging merely because it exists.
- `DescribeSpans` documents `duration` in microseconds (`us`). Aggregate APM latency metrics remain seconds; do not compare the raw numbers without conversion.
- Operations using `pageNo/pageSize` require manual loops. Bound the total requested rows.
- Direct metric TopN uses `limit`; set it explicitly for grouped queries.

## Comparison and output semantics

- `compareTo` accepts `yesterday`, `lastweek`, minute/hour offsets such as `5m` or `2h`, and UTC dates.
- Comparison rate is `(current-compare)/compare`, not a percentage until multiplied by 100.
- Match comparison points by timestamp offset; array order is not a stable label.
- Missing series and non-finite ratios are not zeros.
- Successful metric data is returned under lowercase `timeseries`. A missing `timeSeries` field is not evidence that the backend returned no data.
- Preserve response `requestId` in failures and in any audit summary.

## Known contract boundaries

- Direct metrics use Prom labels; Trace metrics use public fields and backend mapping.
- Metric-level filters are safe for direct Prom queries but not consistently merged on Trace/LLM non-Prom routes.
- The response can be zero-filled and retention-truncated.
- Service discovery/headline cards can lag immediately after ingestion. Use them to resolve identity and scope, then use the selected metric operation for quantitative evidence.
- Debug output may include signed headers or sensitive payloads; do not enable it by default.
- List/detail responses may contain arbitrary Span attributes, URLs, SQL, stacks, or user data. Add an output `--query` projection to the command itself and retain only the fields needed for the next diagnostic decision.

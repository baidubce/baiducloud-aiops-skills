# LLM observability CLI contract

Use the existing BCE CLI and re-read each operation's help at runtime.

## Operations

| Operation | Use | Paging |
|---|---|---|
| `DescribeLLMServices` | LLM application discovery | operation-defined |
| `DescribeLLMDimensionValues` | service/model/kind dimension discovery | none advertised |
| `DescribeLLMMetricData` | aggregate metrics across Prom/Doris/BLS | metric `limit` |
| `DescribeLLMSessions` | session list | `pageNo/pageSize` |
| `DescribeLLMSession` | session detail | one ID |
| `DescribeLLMSessionsStatistics` | session statistics | bounded time range |
| `DescribeLLMTraces` | Trace list | `pageNo/pageSize` |
| `DescribeLLMTrace` | Trace detail | one Trace ID |
| `DescribeLLMTracesStatistics` | Trace statistics | bounded time range |
| `DescribeLLMSpans` | Span list | marker and CLI `--pager` |

Always inspect `bce apm <Operation> --help` for current required flags and limits.

## Metric request shape

`DescribeLLMMetricData` accepts:

- `metrics[]`: `{name, compareTo[], filters[]}`;
- strict UTC `beginDatetime`, `endDatetime`;
- top-level `filters[]`: `{key, op, value|values}`;
- `groupBy[]`, `orderBy`, `order`, `limit`, `periodSeconds`, `aggregate[]`.

For cross-route correctness, leave every `metrics[].filters` empty and place filters at the top level. Use public LLM fields, not internal Prom labels.

Use stable operators `=`, `!=`, and `in`. Split a request if a route or field requires other semantics.

## CLI pattern

```bash
bce apm DescribeLLMMetricData --help
bce apm DescribeLLMMetricData --generate-cli-skeleton
python3 <skill-directory>/scripts/validate_llm_request.py /absolute/request.json
bce apm DescribeLLMMetricData --region <region> \
  --cli-input-json file:///absolute/request.json --output json
```

Do not manually send `version` or an action field.

Inspect Dry Run before execution because installed CLI metadata determines the endpoint and scheme. Sensitive LLM detail must use an approved trusted/private path or an HTTPS-capable endpoint/CLI when required by the environment's transport policy. Do not silently downgrade an explicitly supplied HTTPS endpoint.

## List and detail discipline

- Bound `pageNo/pageSize` lists and stop once enough candidates are found.
- `DescribeLLMSpans --pager --total-count <N>` may aggregate marker pages, but sandbox testing showed the first server page can exceed a smaller `<N>`. Treat `<N>` as a soft client bound, slice displayed rows to the requested count, and preserve `nextMarker` when stopping early.
- For an exact `traceId`, request one page first and continue only if the returned marker and the task require it.
- Keep `parseLLMInputOutput=false` by default for `DescribeLLMSpans`.
- Fetch `DescribeLLMSession` only after `DescribeLLMSessions` identifies the exact `sessionID` and time range.
- Fetch `DescribeLLMTrace` only after `DescribeLLMTraces` identifies the exact `traceId` and time range.
- There is no `DescribeLLMSpan` operation. Isolate a Span by calling `DescribeLLMSpans` again with the exact `traceId` plus the narrowest verified begin/end time; add other exact public filters only when needed.
- Exact LLM Spans can exist while `DescribeLLMTraces`/`DescribeLLMSessions` remains empty when session/user aggregation metadata is absent or delayed. Keep those observations distinct and fall back to the exact Span path rather than declaring data loss.
- `DescribeLLMSpans` duration uses microseconds (`us`). `DescribeLLMSessions` and `DescribeLLMTraces` duration uses milliseconds (`ms`). Aggregate latency and first-token metrics use seconds.

## Privacy contract

LLM detail can include user/session IDs, prompts, completions, model content, tool inputs/outputs, and arbitrary attributes. Add a minimal output `--query` projection to every list/detail command. `parseLLMInputOutput=false` applies only to `DescribeLLMSpans`; it does not sanitize `DescribeLLMTrace` or `DescribeLLMSession`. Request and display the minimum needed fields, redact secrets and personal data, and do not log raw request/response content or use `--debug` by default.

## Error and comparison semantics

- Preserve `requestId` on errors.
- Do not retry authentication or invalid-parameter failures.
- Retry a timeout or 5xx at most once with the identical request.
- Comparison rate is a ratio; label periods by timestamp offset rather than result-array index.
- Response `db` is routing metadata and can be absent or coarse for mixed results.
- Metric series are returned under lowercase `timeseries`, not `timeSeries`.
- `DescribeLLMServices` headline values can temporarily remain zero after a service is discovered while `DescribeLLMMetricData` already has the newly ingested series. Use discovery to resolve identity and the metric operation for conclusions.

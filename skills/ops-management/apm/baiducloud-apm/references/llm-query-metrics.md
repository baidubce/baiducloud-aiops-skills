# LLM query metrics

Use this reference for executable LLM metric names, public dimensions, routes, and units. Alarm evaluator names belong to this Skill's alarm mode.

## Public LLM fields

| Meaning | Public request field | Internal Prom label |
|---|---|---|
| application | `service` | `service.name` |
| host | `host` | `host.name` |
| Span role | `kind` | `span.kind` |
| LLM/agent/tool kind | `attributes.gen_ai.kind` | `gen_ai.kind` |
| model | `attributes.gen_ai.response.model` | `model` |
| Token direction | `token.type` | `token.type` |
| component | `attributes.apm.component` | `component` |
| operation | `attributes.apm.operation` | `operation` |
| exception | `exception.type` | `exception.type` |

Use the public field column with `DescribeLLMMetricData` and `DescribeLLMDimensionValues`. Do not mix it with the internal column.

## Scale and RED metrics

| Meaning | Metric | Raw unit/route tendency |
|---|---|---|
| LLM applications | `llm_service_count` | distinct count, Prom |
| models | `llm_model_count` | distinct count, Prom |
| Spans | `llm_span_count` | count, Prom/BLS/Doris |
| Traces | `llm_trace_count` | distinct count, BLS/Doris |
| users | `llm_user_count` | distinct count, Doris or BLS |
| sessions | `llm_session_count` | count, Doris |
| calls | `llm_requests_seconds_count` | count/window |
| QPS | `llm_requests_count_per_second` | calls/s |
| errors | `llm_error_requests_count` | count/window |
| error rate | `llm_error_requests_rate` | ratio `[0,1]` |
| latency | `llm_requests_seconds_{avg|p50|p90|p95|p99|min|max|sum}` | seconds |

Do not send legacy example names `llm_requests_count`, `llm_requests_per_second`, or `llm_error_rate`.

## Token metrics

| Meaning | Metric | Unit |
|---|---|---|
| total Token use | `llm_token_usage_sum` | tokens; group by `token.type` |
| Token observations | `llm_token_usage_count` | observations, not total tokens |
| max/min observed Token use | `llm_token_usage_max`, `llm_token_usage_min` | tokens |
| average per LLM call | `llm_avg_token_count_per_llm_call` | tokens/call |
| average per request | `llm_avg_token_count_per_request` | tokens/Trace, BLS |
| average input/output per request | `llm_avg_input_token_count_per_request`, `llm_avg_output_token_count_per_request` | tokens/Trace, BLS |
| Token rate | `llm_token_usage_per_second` | tokens/s |

`llm_tokens_per_minute` is not implemented. Derive TPM as `llm_token_usage_per_second × 60` in the explanation. `llm_max_token_count_per_llm_call` and `llm_min_token_count_per_llm_call` are also not implemented; use raw max/min only as an explicitly qualified approximation.

## Generation performance

| Meaning | Metric | Unit and direction |
|---|---|---|
| first-token latency | `llm_time_to_first_token_{avg|p50|p90|p95|p99|min|max}` | seconds; lower is faster |
| time per output Token | `llm_time_per_output_token_{avg|min|max}` | seconds/token; lower is faster |
| output Token rate | `llm_output_token_per_second_avg` | tokens/s; higher is faster |
| LLM calls per request | `llm_avg_llm_call_per_request` | calls/Trace, BLS |

Do not describe seconds/token as tokens/second.

## User and session metrics

User analysis currently supports:

- `llm_user_count`.
- `llm_trace_per_user`, `llm_session_per_user`, `llm_span_per_user`, `llm_call_per_user`.
- `llm_token_per_user`, `llm_input_token_per_user`, `llm_output_token_per_user`.
- `llm_duration_per_user`.

These advanced names are accepted by the service implementation but not enumerated in public CLI help. Probe with one small read-only query and fall back to dedicated list/statistics operations on an invalid-metric response.

Session metrics:

- `llm_session_count`: time series; without explicit groupBy, multiple services may be grouped by service.
- `llm_session_trace_count`: average traces/turns per session, currently an application TopN point.
- `llm_session_token_count`: average session Token use, currently an application TopN point.

`llm_session_count.compareTo` applies only with `periodSeconds=0` and no explicit groupBy.

## Data-source routing

`DescribeLLMMetricData` can combine Prom, Doris, BLS, and BLS histogram paths:

- user and session metrics are split to Doris;
- mappable metrics/filters/groupBy use Prom;
- some single Token/Trace metrics use Doris optimization;
- other cases use BLS or BLS histogram.

Metrics that should normally be split from Prom overview requests include `llm_trace_count`, `llm_session_count`, `llm_user_count`, all three per-request Token averages, and `llm_avg_llm_call_per_request`.

The top-level response `db` field describes routing only coarsely. In a mixed response it is not a per-metric source guarantee, and a session-only response may omit it.

## Recommended request slices

### Overview

1. Prom-oriented RED and generation latency.
2. `llm_token_usage_sum` grouped by `token.type`.
3. Session/user/Trace/Span counts in route-compatible requests.

### Model TopN

- group by `attributes.gen_ai.response.model`;
- order by one call/error/latency/first-token metric;
- `periodSeconds=0`, `order=desc`, `limit=5` or `10`.

### Token analysis

1. total Token use by input/output;
2. average Token per LLM call by input/output;
3. per-request input and output averages as separate BLS queries;
4. first-token latency and output rate alongside Token volume.

### Detail drill-down

Use aggregate metrics to identify a target, then use `DescribeLLMSessions` → `DescribeLLMSession` and `DescribeLLMTraces` → `DescribeLLMTrace`. There is no `DescribeLLMSpan`; narrow `DescribeLLMSpans` by exact `traceId` and time range. Do not reconstruct individual calls from aggregates.

## Filters, aggregate, and compareTo

- Prefer stable operators `=`, `!=`, and `in` across storage routes.
- Use only top-level filters. Metric-level filters are not merged consistently across Prom, BLS, and Doris.
- `attributes.gen_ai.kind=llm` restricts to actual model calls; remove it when counting the full request chain where appropriate.
- If `aggregate` contains `sum` or `sumPerSecond`, request one metric of one unit.
- Match compare periods by timestamp offset, not array index.
- A zero-filled point can represent missing data.

## Evaluation metrics

Base collected families include categorical `llm_eval_categorical_count` and numeric `llm_eval_score_sum/count`, with `eval_name`, `content_type`, and where applicable `category`.

The query service can dynamically accept `<base>_sum`, `<base>_count`, and `<base>_avg`, but the current CLI exposes no evaluation-metadata discovery operation. Require an exact trusted metric base from evaluation configuration or the user; never construct it from an evaluation display name.

## Units

- Aggregate request, first-token, and time-per-token latency: seconds.
- `DescribeLLMSpans` duration: microseconds (`us`).
- `DescribeLLMSessions` and `DescribeLLMTraces` duration: milliseconds (`ms`).
- Error rate: `[0,1]`, multiply by 100 only for display.
- Token use: tokens.
- Counts: selected aggregation window.
- QPS and Token rate: already per second.

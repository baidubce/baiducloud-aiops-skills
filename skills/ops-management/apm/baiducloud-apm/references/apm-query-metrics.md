# APM query metrics

Use this reference to choose executable query metrics and dimensions. Alarm evaluator metrics belong to this Skill's alarm mode and are not interchangeable with these names.

## Choose the query operation

| Need | Operation | Dimension namespace |
|---|---|---|
| Derived APM, DB, JVM, Python, or Go metrics | `DescribeMetricData` | Prom labels such as `service.name`, `span.kind`, `operation` |
| HTTP status, exception, slow request, DB, or Span semantics | `DescribeTraceMetricData` | Public Trace fields such as `service`, `kind`, `attributes.apm.operation` |
| Prom dimension values | `DescribeDimensionValues` | Prom label in `dimensionKey` |
| Trace field values | `DescribeSpanFieldValues` | Public Trace field in `key` |
| Individual spans and trace trees | `DescribeSpans`, `DescribeTrace` | Public Trace fields |

Do not mix the two namespaces in one request.

## RED metrics

| Meaning | Metric | Raw unit |
|---|---|---|
| Requests | `apm_requests_count` | count/window |
| QPS | `apm_requests_per_second` | requests/s |
| Errors | `apm_error_requests_count` | count/window |
| Error QPS | `apm_error_requests_per_second` | errors/s |
| Error rate | `apm_error_rate` | ratio `[0,1]` |
| Average latency | `apm_requests_seconds_avg` | seconds |
| Tail latency | `apm_requests_seconds_p90`, `p95`, `p99` | seconds |

`apm_requests_seconds_p50`, `min`, `max`, and `sum` are available for special analysis but are not the default overview.

## Errors and slow requests

- Error latency: `apm_error_requests_seconds_{avg|p90|p95|p99}`.
- Exception request count/QPS: `apm_exceptions_requests_{count|per_second}`.
- HTTP groups: `apm_error_requests_{4xx|5xx}_{count|per_second}`.
- Specific status codes currently implemented: `400`, `401`, `403`, `404`, `500`, `501`, `503` with `_count` or `_per_second`.
- Slow requests: `apm_slow_requests_{count|per_second}` and `apm_slow_requests_seconds_{avg|p90|p95|p99}`.

The slow-request threshold comes from `DescribeServiceConfig`, not from the metric name.

## AppBuilder and topology metrics

| Meaning | Exact metric |
|---|---|
| AppBuilder success rate | `ab_success_rate` |
| AppBuilder error rate | `ab_error_rate` |
| AppBuilder average latency | `ab_requests_seconds_avg` |
| Topology request count | `apm_topo_requests_count` |
| Topology QPS | `apm_topo_requests_per_second` |
| Topology error request count | `apm_topo_error_requests_count` |
| Topology slow request count | `apm_topo_slow_requests_count` |
| Topology average latency | `apm_topo_requests_seconds_avg` |

Do not use `apm_topo_error_rate`: its current numerator/denominator formula is unresolved.

## Database metrics

| Meaning | Metric |
|---|---|
| DB requests/QPS | `apm_db_requests_count`, `apm_db_requests_per_second` |
| DB errors/QPS | `apm_db_error_requests_count`, `apm_db_error_requests_per_second` |
| DB error rate | `apm_db_error_rate` |
| DB latency | `apm_db_requests_seconds_{avg|p90|p95|p99}` |
| DB error latency | `apm_db_error_requests_seconds_{avg|p90|p95|p99}` |
| Slow SQL count/QPS | `apm_db_slow_requests_{count|per_second}` |
| Slow SQL latency | `apm_db_slow_requests_seconds_{avg|p90|p95|p99}` |

Direct-query dimensions are `service.name`, `db.system`, `db.name`, `db.statement.id`, `db.server.address`, `host.name`, and `version`. Alarm policies use `db.instance`; do not copy that name into a Prom query without dimension discovery.

## Direct-query dimensions

| Dimension | Meaning |
|---|---|
| `service.name` | service/application |
| `span.kind` | `server`, `client`, `internal`, `consumer`, `producer` |
| `component` | protocol/framework component |
| `operation` | endpoint or operation; often high cardinality |
| `host.name` | service instance |
| `exception.type` | exception class/type |
| `http.status` | HTTP status |
| `status` | slow-call status `ok` or `error` |
| `version` | metric version; normally not grouped |

## Trace public fields

| Public field | Prom label after routing |
|---|---|
| `service` | `service.name` |
| `kind` | `span.kind` |
| `host` | `host.name` |
| `attributes.apm.component` | `component` |
| `attributes.apm.operation` | `operation` |
| `attributes.http.response.status_code` | `http.status` |
| `hasException`, `exception.type` | `exception.type` |
| `attributes.db.system` | `db.system` |
| `attributes.db.statement.id` | `db.statement.id` |
| `attributes.db.name` | `db.name` |

For Trace metric analysis, use these stable public metrics: `apm_requests_count`, `apm_error_requests_count`, `apm_requests_seconds_avg`, `apm_requests_seconds_p90`, `apm_requests_seconds_p95`, and `apm_requests_seconds_p99`. The backend rewrites the underlying family when filters imply DB, error, exception, slow request, or slow DB semantics.

Trace requests use top-level filters only. `db.name` is a direct Prom label and is invalid here; use the public field `attributes.db.name`. Other custom Span attributes use their full `attributes.<key>` name.

`slowRequest=true` and `slowDBRequest=true` together return an empty result; never combine them.

## JVM metrics

Standard metrics:

- Class loading: `jvm.class.count`, `jvm.class.loaded`, `jvm.class.unloaded`.
- CPU: `jvm.cpu.count`, `jvm.cpu.recent_utilization`, `jvm.cpu.time`.
- GC: `jvm.gc.duration_count`, `jvm.gc.duration_sum`, `jvm.gc.duration_avg`.
- Memory: `jvm.memory.used`, `jvm.memory.limit`, `jvm.memory.committed`, `jvm.memory.used_after_last_gc`.
- Threads: `jvm.thread.count`.

Exact derived GC and CPU metrics:

- G1 new generation: `jvm.gc.duration_new_gen_count`, `jvm.gc.duration_new_gen_per_second`, `jvm.gc.duration_new_gen_avg`, `jvm.gc.duration_new_gen_sum`, `jvm.gc.duration_new_gen_max`, `jvm.gc.duration_new_gen_min`.
- G1 old generation: `jvm.gc.duration_old_gen_count`, `jvm.gc.duration_old_gen_per_second`, `jvm.gc.duration_old_gen_avg`, `jvm.gc.duration_old_gen_sum`, `jvm.gc.duration_old_gen_max`, `jvm.gc.duration_old_gen_min`.
- CPU: `jvm.cpu.recent_utilization_avg`, `jvm.cpu.count_avg`, `jvm.cpu.time_sum`.

Exact derived memory metrics:

- Heap: `jvm.memory.used_heap_pre_second`, `jvm.memory.used_heap_count`, `jvm.memory.limit_heap_pre_second`, `jvm.memory.limit_heap_count`, `jvm.memory.committed_heap_pre_second`, `jvm.memory.committed_heap_count`.
- Non-heap: `jvm.memory.used_non_heap_pre_second`, `jvm.memory.used_non_heap_count`, `jvm.memory.limit_non_heap_pre_second`, `jvm.memory.limit_non_heap_count`, `jvm.memory.committed_non_heap_pre_second`, `jvm.memory.committed_non_heap_count`.
- Pools: `jvm.memory.used_eden_space_pre_second`, `jvm.memory.used_eden_space_count`, `jvm.memory.used_survivor_space_pre_second`, `jvm.memory.used_survivor_space_count`, `jvm.memory.used_old_gen_pre_second`, `jvm.memory.used_old_gen_count`, `jvm.memory.used_metaspace_pre_second`, `jvm.memory.used_metaspace_count`, `jvm.memory.used_compressed_class_space_pre_second`, `jvm.memory.used_compressed_class_space_count`, `jvm.memory.used_code_heap_pre_second`, `jvm.memory.used_code_heap_count`.

Exact derived thread and class metrics:

- All threads: `jvm.thread.count_pre_second`, `jvm.thread.count_count`.
- Runnable: `jvm.thread.count_runnable_pre_second`, `jvm.thread.count_runnable_count`.
- Waiting: `jvm.thread.count_waiting_pre_second`, `jvm.thread.count_waiting_count`.
- Timed waiting: `jvm.thread.count_timed_waiting_pre_second`, `jvm.thread.count_timed_waiting_count`.
- Blocked: `jvm.thread.count_blocked_pre_second`, `jvm.thread.count_blocked_count`.
- Terminated: `jvm.thread.count_terminated_pre_second`, `jvm.thread.count_terminated_count`.
- Classes: `jvm.class.count_pre_second`, `jvm.class.loaded_per_second`, `jvm.class.loaded_count`, `jvm.class.unloaded_per_second`, `jvm.class.unloaded_count`.

`pre_second` is an existing backend spelling. Young/old generation templates are G1-specific; query raw `jvm.gc.name` for other collectors.

Common JVM dimensions are `service.name`, `host.name`, `jvm.gc.name`, `jvm.gc.action`, `jvm.memory.type`, `jvm.memory.pool.name`, `jvm.thread.state`, and `jvm.thread.daemon`.

## Python runtime

- GC: `process.runtime.cpython.gc_count`, `process.runtime.cpython.gc.collections`, `process.runtime.cpython.gc.duration_avg`.
- CPU: `process.runtime.cpython.cpu_time`, `process.runtime.cpython.cpu.utilization`.
- Memory/thread/context switches: `process.runtime.cpython.memory`, `process.runtime.cpython.thread_count`, `process.runtime.cpython.context_switches`.

Use `service.name`, `host.name`, and where applicable `count` or `type` dimensions.

## Go runtime

- GC: `process.runtime.go.gc.count`, `process.runtime.go.gc.pause_total_ns`, `process.runtime.go.gc.pause_ns`, `process.runtime.go.gc.pause_ns_sum`.
- Heap: `process.runtime.go.mem.heap_alloc`, `process.runtime.go.mem.heap_idle`, `process.runtime.go.mem.heap_inuse`, `process.runtime.go.mem.heap_released`, `process.runtime.go.mem.heap_sys`.
- Objects: `process.runtime.go.mem.live_objects`, `process.runtime.go.mem.heap_objects`.
- Other: `process.runtime.go.cgo.calls`, `process.runtime.go.mem.lookups`, `process.runtime.go.goroutines`, `runtime.uptime`.

UI selector names such as `stack-memory`, `file`, or `go_runtime_stack_momery_5` are not query metrics.

## Periods, TopN, and units

| Time range | Suggested `periodSeconds` |
|---|---:|
| ≤1h | 60 |
| ≤3h | 300 |
| ≤6h | 600 |
| ≤24h | 1800 |
| ≤48h | 3600 |
| ≤72h | 7200 |
| ≤120h | 14400 |
| ≤240h | 21600 |
| ≤720h | 43200 |
| longer | 86400 |

Use `periodSeconds=0` for a single aggregate point or TopN. Set `orderBy` to a metric in the same request, `order=desc|asc`, and an explicit limit. The sorting metric determines the dimension combinations retained for other metrics.

- Latencies are seconds; display seconds and optionally milliseconds.
- `DescribeSpans` duration is microseconds (`us`); it is a detail/list unit, not an aggregate metric unit.
- Error/CPU rates are ratios; display percent as ratio × 100.
- QPS is already per second.
- Count is for the selected aggregation window.
- Bytes remain Bytes in the raw result.

The service may fill missing points with zero and may truncate a range to retention. Never equate a filled zero with confirmed activity of zero.

## Automatic pre-aggregation

Always request public raw or derived names. The backend uses filter and `groupBy` keys to choose compatible `_by_srv_*` pre-aggregates and falls back to raw metrics when needed. Never select a pre-aggregate manually.

Do not use `apm_topo_error_rate` for automated analysis until its numerator/denominator formula is corrected or confirmed.

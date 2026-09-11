# APM and LLM alarm catalog

This catalog describes alarm evaluator metrics accepted by APM alarm policies. They are not the same namespace as `DescribeMetricData` query metrics.

Example boundary:

- alarm rule: `apm_requests` with statistic `sum`;
- baseline query: `apm_requests_count`.

Never replace the alarm name with its query equivalent.

## Statistics and threshold operators

Metric statistics are `avg`, `count_per_second`, `max`, `min`, `sum`, `p90`, `p95`, and `p99`, but each metric permits only the subset below.

Threshold operators:

- static: `gt`, `gte`, `lt`, `lte`;
- previous period: `prev_inc`, `prev_dec`;
- hour-over-hour: `hoh_inc`, `hoh_dec`;
- day-over-day: `dod_inc`, `dod_dec`.

Comparison thresholds use `%`. Do not generate compatibility-only `eq` or `ne` without a known working policy supplied by the user.

The window must be at least 60 seconds. Common UI values are 60, 300, 600, and 900 seconds. Do not use the conflicting catalog value `cycle=30`.

## Service kinds

`SERVER`, `CLIENT`, `INTERNAL_FUNCTION`, `CONSUMER`, and `PRODUCER` share these metrics:

| Alarm metric | Statistics | Unit | Baseline query |
|---|---|---|---|
| `apm_requests` | `count_per_second`, `sum` | count | `apm_requests_per_second` / `apm_requests_count` |
| `apm_requests_per_second` | `avg` | requests/s | same name |
| `apm_error_requests` | `count_per_second`, `sum` | count | `apm_error_requests_per_second` / `apm_error_requests_count` |
| `apm_error_rate` | `avg` | `%` | `apm_error_rate` ratio × 100 |
| `apm_requests_seconds` | `avg`, `sum`, `max`, `min`, `p90`, `p95`, `p99` | seconds | `apm_requests_seconds_<statistic>` |
| `apm_slow_requests` | `count_per_second`, `sum` | count | `apm_slow_requests_per_second` / `apm_slow_requests_count` |

`SERVER` alone also permits the following count metrics, each with `count_per_second` and `sum`:

- `apm_4xx_requests`, `apm_400_requests`, `apm_401_requests`, `apm_403_requests`, `apm_404_requests`;
- `apm_5xx_requests`, `apm_500_requests`, `apm_501_requests`, `apm_503_requests`.

The query equivalent inserts `error_` after `apm_` and uses `_per_second` or `_count`. Do not invent alarm names for unlisted status codes.

## DB and exception kinds

`DB` permits:

| Alarm metric | Statistics | Unit | Baseline query |
|---|---|---|---|
| `apm_db_requests` | `count_per_second`, `sum` | count | `apm_db_requests_per_second` / `apm_db_requests_count` |
| `apm_db_requests_per_second` | `avg` | requests/s | same name |
| `apm_db_error_requests` | `count_per_second`, `sum` | count | `apm_db_error_requests_per_second` / `apm_db_error_requests_count` |
| `apm_db_error_rate` | `avg` | `%` | query ratio × 100 |
| `apm_db_requests_seconds` | `avg`, `sum`, `max`, `min`, `p90`, `p95`, `p99` | seconds | `apm_db_requests_seconds_<statistic>` |
| `apm_db_slow_requests` | `count_per_second`, `sum` | count | `apm_db_slow_requests_per_second` / `apm_db_slow_requests_count` |

`EXCEPTION` permits only `apm_exceptions_requests` with `count_per_second` or `sum`; query `apm_exceptions_requests_per_second` or `_count`.

## JVM kind

### GC and CPU

| Alarm metric | Statistics | Unit | Baseline query family |
|---|---|---|---|
| `jvm_young_gc_count` | `count_per_second`, `sum` | count | `jvm.gc.duration_new_gen_per_second`, `jvm.gc.duration_new_gen_count` |
| `jvm_full_gc_count` | `count_per_second`, `sum` | count | `jvm.gc.duration_old_gen_per_second`, `jvm.gc.duration_old_gen_count` |
| `jvm_young_gc_time` | `avg`, `sum`, `max`, `min` | seconds | `jvm.gc.duration_new_gen_avg`, `jvm.gc.duration_new_gen_sum`, `jvm.gc.duration_new_gen_max`, `jvm.gc.duration_new_gen_min` |
| `jvm_full_gc_time` | `avg`, `sum`, `max`, `min` | seconds | `jvm.gc.duration_old_gen_avg`, `jvm.gc.duration_old_gen_sum`, `jvm.gc.duration_old_gen_max`, `jvm.gc.duration_old_gen_min` |
| `jvm_cpu_usage` | `avg` | `%` | `jvm.cpu.recent_utilization_avg` ratio × 100 |
| `jvm_cpu_count` | `avg` | count | `jvm.cpu.count_avg` |
| `jvm_cpu_time` | `sum` | seconds | `jvm.cpu.time_sum` |

Young/full baseline mappings currently assume G1 collector names. Validate `jvm.gc.name` before using them for thresholds.

### Memory

| Alarm metric | Statistics | Exact baseline query metrics |
|---|---|---|
| `jvm_heap_used` | `count_per_second`, `sum` | `jvm.memory.used_heap_pre_second`, `jvm.memory.used_heap_count` |
| `jvm_heap_limit` | `avg`, `sum` | `jvm.memory.limit_heap_pre_second`, `jvm.memory.limit_heap_count` |
| `jvm_heap_committed` | `count_per_second`, `sum` | `jvm.memory.committed_heap_pre_second`, `jvm.memory.committed_heap_count` |
| `jvm_non_heap_used` | `count_per_second`, `sum` | `jvm.memory.used_non_heap_pre_second`, `jvm.memory.used_non_heap_count` |
| `jvm_non_heap_limit` | `count_per_second`, `sum` | `jvm.memory.limit_non_heap_pre_second`, `jvm.memory.limit_non_heap_count` |
| `jvm_non_heap_committed` | `count_per_second`, `sum` | `jvm.memory.committed_non_heap_pre_second`, `jvm.memory.committed_non_heap_count` |
| `jvm_metaspace_used` | `count_per_second`, `sum` | `jvm.memory.used_metaspace_pre_second`, `jvm.memory.used_metaspace_count` |
| `jvm_compressed_class_space_used` | `count_per_second`, `sum` | `jvm.memory.used_compressed_class_space_pre_second`, `jvm.memory.used_compressed_class_space_count` |
| `jvm_code_cache_used` | `count_per_second`, `sum` | `jvm.memory.used_code_heap_pre_second`, `jvm.memory.used_code_heap_count` |
| `jvm_eden_space_used` | `count_per_second`, `sum` | `jvm.memory.used_eden_space_pre_second`, `jvm.memory.used_eden_space_count` |
| `jvm_survivor_space_used` | `count_per_second`, `sum` | `jvm.memory.used_survivor_space_pre_second`, `jvm.memory.used_survivor_space_count` |
| `jvm_old_gen_used` | `count_per_second`, `sum` | `jvm.memory.used_old_gen_pre_second`, `jvm.memory.used_old_gen_count` |

All of these alarm metrics use Bytes. Preserve the existing backend spelling `pre_second`. Convert Bytes only according to `displayUnit` (`Bytes`, `KB`, `MB`, `GB`, `TB`) and retain raw Bytes for audit.

### Threads and classes

| Alarm metric | Statistics | Exact baseline query metrics |
|---|---|---|
| `jvm_thread_count` | `count_per_second`, `sum` | `jvm.thread.count_pre_second`, `jvm.thread.count_count` |
| `jvm_thread_blocked` | `count_per_second`, `sum` | `jvm.thread.count_blocked_pre_second`, `jvm.thread.count_blocked_count` |
| `jvm_thread_runnable` | `count_per_second`, `sum` | `jvm.thread.count_runnable_pre_second`, `jvm.thread.count_runnable_count` |
| `jvm_thread_waiting` | `count_per_second`, `sum` | `jvm.thread.count_waiting_pre_second`, `jvm.thread.count_waiting_count` |
| `jvm_thread_timed_waiting` | `count_per_second`, `sum` | `jvm.thread.count_timed_waiting_pre_second`, `jvm.thread.count_timed_waiting_count` |
| `jvm_thread_terminated` | `count_per_second`, `sum` | `jvm.thread.count_terminated_pre_second`, `jvm.thread.count_terminated_count` |
| `jvm_class_current` | `count_per_second` | `jvm.class.count_pre_second` |
| `jvm_class_loaded` | `count_per_second`, `sum` | `jvm.class.loaded_per_second`, `jvm.class.loaded_count` |
| `jvm_class_unloaded` | `count_per_second`, `sum` | `jvm.class.unloaded_per_second`, `jvm.class.unloaded_count` |

## LLM kinds

### `LLM`

| Alarm metric | Statistics | Unit | Baseline query |
|---|---|---|---|
| `llm_requests` | `count_per_second`, `sum` | count | `llm_requests_count_per_second` / `llm_requests_seconds_count` |
| `llm_requests_per_second` | `avg` | calls/s | `llm_requests_count_per_second` |
| `llm_error_requests` | `count_per_second`, `sum` | count | sum → `llm_error_requests_count`; derive per-second cautiously |
| `llm_error_rate` | `avg` | `%` | `llm_error_requests_rate` ratio × 100 |
| `llm_requests_seconds` | `avg`, `max`, `min`, `p90`, `p95`, `p99` | seconds | same suffix query metric |

### `LLM_OPERATION`

- `llm_app_requests`: `count_per_second`, `sum`.
- `llm_app_error_requests`: `count_per_second`, `sum`.
- `llm_app_error_rate`: `avg`.
- `llm_app_requests_seconds`: `avg`, `max`, `min`, `p90`, `p95`, `p99`.

There is no authoritative `llm_app_*` query-template mapping. Do not invent a baseline query or automatically recommend a threshold.

### `LLM_TOKEN_ANALYSIS`

| Alarm metric | Statistics | Unit | Baseline query |
|---|---|---|---|
| `llm_token_usage` | `count_per_second`, `sum` | tokens | `llm_token_usage_per_second` / `llm_token_usage_sum` |
| `llm_token_usage_per_call` | `avg` | tokens/call | `llm_avg_token_count_per_llm_call` |
| `llm_time_to_first_token` | `avg`, `max`, `min` | seconds | same suffix query metric |
| `llm_time_per_output_token` | `avg`, `max`, `min` | seconds/token | same suffix query metric |

Seconds/token improves as it decreases; it is not Token output rate.

## Targets and dimensions

| metricKind | Dimensions and defaults |
|---|---|
| `SERVER` | implicit `span.kind=server`; service/component/operation/`host.name`; component and operation iterate by default, host aggregates by omission |
| `CLIENT` | implicit `span.kind=client`; same service dimensions and defaults |
| `CONSUMER` | implicit `span.kind=consumer`; same service dimensions and defaults |
| `PRODUCER` | implicit `span.kind=producer`; same service dimensions and defaults |
| `INTERNAL_FUNCTION` | implicit `span.kind=internal`; service/operation/`host.name`; operation iterates, host aggregates by omission |
| `DB` | service, `db.system`, `db.instance`, `host.name`; non-service dimensions aggregate by omission by default |
| `JVM` | service, `host.name`; host aggregates by omission by default |
| `EXCEPTION` | service, component, operation, `host.name`, exception.type; non-service dimensions aggregate by omission by default |
| `LLM` | service, `attributes.gen_ai.response.model` |
| `LLM_OPERATION` | service, `attributes.gen_ai.kind`, model |
| `LLM_TOKEN_ANALYSIS` | service, model |

Do not generate the internal-only `PRODUCER_CONSUMER` value.

Target types:

- all services: `{"type":"ALL_SERVICES","services":[]}`;
- named services: `{"type":"SERVICES","services":[...]}`;
- `SERVICE_TAGS` only after validating a working policy or current CLI semantics.

Service scope belongs in `target`, not `filters`.

Dimension filters use exact keys from this matrix. All listed dimensions allow `eq`, `ne`, and `iterate`; only `operation` also allows `contains` and `not_contain`. `iterate` uses `values=["*"]`. UI “aggregate” means omit the dimension filter entirely. Do not send an `aggregate` filter entry or use regex operators without a proven working policy.

## Rule tree

A leaf contains `metric`, `windowInSeconds`, `aggregate` (the metric statistic), `operator`, `displayValue`, and `displayUnit`.

Use only:

- one top-level `and` containing leaf rules; or
- one top-level `or` whose children are `and` groups containing leaf rules.

Do not generate deeper or arbitrary logic trees.

## Missing data and notification

- `pendingCount` is at least 1.
- Re-notification interval `0` disables it; when enabled, `renotifyCount` is at least 1.
- `notifyRecovery` controls recovery notification.
- `onMissingData`: `SHOW_NO_DATA_AND_NOTIFY`, `SHOW_NO_DATA`, `SHOW_OK`, or `EVALUATE_AS_ZERO`.
- With `SHOW_NO_DATA_AND_NOTIFY`, `noDataNotifyPendingIntervalInMinutes=0` is valid and means notify immediately; positive values wait that many minutes.
- `EVALUATE_AS_ZERO` can create low-threshold alarms and hide collection failure for high-threshold alarms; use only after explicit review.
- `level`: `NOTICE`, `WARNING`, `MAJOR`, `CRITICAL`.
- Every `actions[].notifyId` must be resolved and confirmed before mutation.

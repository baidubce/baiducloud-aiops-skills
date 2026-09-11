---
name: baiducloud-apm
description: Use when users need to diagnose Baidu Cloud APM applications or LLM workloads, query traces and runtime metrics, or safely manage APM/LLM alarm policies through the BCE CLI. Do not use for BCM V3 cloud-product metrics or alarms.
---

# Baidu Cloud Application Performance Monitoring

Operate APM and LLM observability through the existing `bce apm` CLI. Select one mode first and read only the references required for that mode.

## Route the request

| User intent | Read these references | Helper |
| --- | --- | --- |
| Diagnose service traffic, errors, latency, topology, Spans, Traces, SQL, exceptions, JVM, Python, or Go runtime | [apm-query-metrics.md](references/apm-query-metrics.md) and [apm-query-cli-contract.md](references/apm-query-cli-contract.md) | `validate_apm_request.py` |
| Analyze LLM services, models, calls, Token use, first-token performance, users, sessions, Traces, Spans, or evaluation metrics | [llm-query-metrics.md](references/llm-query-metrics.md) and [llm-query-cli-contract.md](references/llm-query-cli-contract.md) | `validate_llm_request.py` |
| Review, design, create, update, enable, disable, or delete an APM/LLM alarm policy; inspect alarm events or notification actions | [alarm-catalog.md](references/alarm-catalog.md) and [alarm-cli-contract.md](references/alarm-cli-contract.md) | `validate_alarm_policy.py` |
| Explain why an APM/LLM alarm fired | Read the alarm references, then the APM or LLM query references selected by `metricKind` and the catalog's explicit baseline mapping | alarm validator plus the matching request validator |

Do not load every metric catalog or CLI contract by default. Ordinary APM requests do not need LLM references; LLM analysis does not need the alarm catalog unless the user asks about alarms.

## Quick examples

- “Analyze the last hour of traffic, errors, and latency for a named service, then narrow only the most abnormal dimension.”
- “Investigate a slow Trace while displaying only IDs, timing, status, and the minimum fields needed for the diagnosis.”
- “Compare LLM call count, error rate, first-token latency, and Token use by model without exposing prompts or completions.”
- “Design an APM error-rate alarm as `DISABLED`; validate its complete JSON and show the dry run, but do not create it.”
- “Explain why an alarm fired by separating the recorded event, mapped metric evidence, and inference.”
- “Authentication failed during a dry run; stop and report the redacted error and `requestId` without retrying or changing profiles.”

## Package integrity

`SKILL.md`, `references/`, and `scripts/` form one atomic package. Before any CLI call, verify that every reference and helper named by the selected route exists locally. The route table is the package manifest: every file under `references/` and every Python helper under `scripts/` must be named there.

If a required file is missing, do not guess a schema or reconstruct a helper. Stop before any CLI call and report `status: incomplete_package`, the selected route, each missing package-relative path, the detected package root, and the action “reinstall or extract the complete release archive.”

## Shared preconditions

1. Check `command -v bce`, `bce version`, `bce apm --help`, the selected operation's `--help`, and its generated skeleton. Treat current CLI help and skeleton as authoritative for operation availability and request shape. If a required capability is absent or incompatible with the selected reference, stop and report it instead of guessing another operation or schema.
2. Check `python3 --version` for a route that names a helper and require Python 3.9 or newer. The packaged helpers use only the Python standard library. If the runtime is absent or too old, stop with `status: missing_runtime` before constructing a cloud request.
3. Use `bce configure list` only to confirm a usable profile. Never read, print, or request stored AK/SK values or credential files.
4. Confirm region and strict UTC time bounds. Do not infer region from a service name.
5. Inspect the first dry run for a new profile or endpoint. CLI metadata may advertise only HTTP for APM; require a trusted/private path or approved HTTPS-capable endpoint when transport policy requires encryption. Never force an unsupported scheme or silently downgrade HTTPS.
6. Use bounded pagination and minimal output projections. Do not enable `--debug` by default because signed headers and request payloads may be sensitive.

## Operation safety and timeout handling

| Operation class | Before execution | Timeout or ambiguous result |
| --- | --- | --- |
| Read-only query or diagnosis | Validate exact inputs; bound time and pagination | Retry the identical validated request at most once. Then report the failed page or window, partial coverage, and `requestId`; unknown is not empty or zero. |
| Policy mutation | Read current state; validate JSON; dry-run; show redacted impact; obtain immediate confirmation | Never retry automatically. Read exact current state first, then require a new preview and confirmation for any later attempt. |
| Authentication, authorization, or validation failure | None | Stop immediately. Report the exact operation, redacted service code/message, and `requestId`; do not retry, change profile, inspect credentials, or guess permissions. |

A service `requestId` is diagnostic evidence, not an idempotency key unless the operation explicitly documents that contract.

## APM diagnosis mode

Keep this mode read-only. Resolve the exact service/environment, establish a RED overview, narrow by one useful dimension, and drill into Span, Trace, SQL, exception, topology, or runtime detail only after identifying an abnormal interval or group. Query `DescribeServiceConfig` only when configuration is needed to interpret thresholds; do not update configuration, tags, or services.

Direct metrics use Prom-style fields such as `service.name`. Trace metrics use public fields such as `service` and `attributes.db.name`. Do not mix the namespaces. Preserve aggregate latency in seconds and Span duration in microseconds; rates remain ratios until explicitly displayed as percentages.

## LLM observability mode

Start with aggregate calls, errors, latency, Token use, first-token performance, and model TopN. Split Prom-oriented metrics from Doris/BLS-oriented session, user, and Trace metrics. Drill into exact sessions, Traces, or Spans only after an aggregate anomaly or an explicit identifier is selected.

Default to `parseLLMInputOutput=false`. It protects only `DescribeLLMSpans`; session and Trace details can still contain inputs, outputs, identities, and nested content, so project safe metadata at the command boundary. Do not construct an evaluation metric name without an exact trusted base.

## Alarm policy mode

Alarm evaluator metric names are not query metric names. Select `metricKind`, metric, statistic, dimensions, units, and rule shape from the alarm catalog. Use only the catalog's explicit baseline mapping for threshold evidence; when `LLM_OPERATION` has no authoritative query mapping, report the boundary instead of inventing one.

Read current policies, check semantic duplicates, query a representative baseline when mapped, validate the complete JSON, and run the exact command with `--dry-run`. Before every mutation:

1. show exact policy IDs, target, rule tree, state, missing-data behavior, notification-template IDs, and redacted callback presence;
2. obtain confirmation immediately before execution;
3. execute once;
4. read back every affected policy or verify exact absence after deletion.

Create requests require `state` and omit `id`; updates require `id` and omit `state`. Use `ApmUpdateAlarmPolicyState` for state changes. Never create an enabled policy unless the preview explicitly says `ENABLED` and the user confirms it. Do not retry an ambiguous timed-out mutation before reading current state.

APM alarm actions may reference shared BCM notification-template IDs. Read them only through `bce bcm DescribeNotifyTemplates` or `DescribeNotifyTemplate`, and never create, update, or delete BCM notification resources from this Skill.

## Alarm-event diagnosis

Keep event diagnosis read-only. Join the exact event and exact policy, select the catalog's explicit baseline query for its `metricKind`, and query the recorded interval. Drill into Trace or LLM detail only when the aggregate result and user request justify it. Separate recorded event facts, query evidence, and inference; absence of a baseline mapping is an evidence gap, not a zero or a healthy result.

## Privacy, failure, and completion

Spans, Trace attributes, SQL, exception stacks, URLs, callbacks, prompts, completions, tool arguments/results, user/session IDs, and model input/output can be sensitive. Project only fields required for the decision, redact credentials and personal identifiers, and never print a raw response first with the intent to redact later.

Authentication, permission, and validation failures are not retryable by guessing. Retry a read timeout or 5xx at most once with the same validated request. Preserve `requestId` when available. Report evidence, raw units, conversions, pagination coverage, missing/zero-filled uncertainty, and the next discriminating read-only query.

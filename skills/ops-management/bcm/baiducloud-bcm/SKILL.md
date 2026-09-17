---
name: baiducloud-bcm
description: 通过 BCE CLI 查询百度智能云监控（BCM）资源和指标、管理告警策略与报警屏蔽，并诊断告警触发、恢复、无数据及通知问题。适用于用户提到 BCM、云监控指标查询、告警策略、报警屏蔽或告警诊断的场景；不用于 APM 或 LLM 可观测。
---

# Baidu Cloud Monitor through BCE CLI

Operate BCM through the existing `bce bcm` CLI. Select one mode first, read only that mode's references, and preserve the boundary between read-only investigation and cloud-side mutation. Synthetic validation is limited to a small, finite sample plan; never turn it into batch load testing or sustained pressure.

## Route the request

| User intent | Read these references | Helpers |
| --- | --- | --- |
| Discover resource/metric metadata; query trend, latest, TopN, or dimension values | [metric-metadata.md](references/metric-metadata.md), [metric-query-semantics.md](references/metric-query-semantics.md), [metric-cli-contract.md](references/metric-cli-contract.md) | `flatten_metric_catalog.py`, `validate_metric_request.py` |
| Review, design, create, update, enable, disable, or delete an alarm policy; manage policy actions, templates, instance groups, or related control-plane objects | [alarm-resource-targeting.md](references/alarm-resource-targeting.md), [alarm-rule-semantics.md](references/alarm-rule-semantics.md), [alarm-policy-cli-contract.md](references/alarm-policy-cli-contract.md); also read the metric references before choosing a metric or threshold | `validate_alarm_policy.py` |
| List, read, design, create, update, enable, disable, or delete alarm masking | [alarm-masking-cli-contract.md](references/alarm-masking-cli-contract.md), [alarm-resource-targeting.md](references/alarm-resource-targeting.md); also read the metric references before choosing dimensions or metric names | `validate_alarm_masking.py` |
| Explain an alarm, recovery, NO_DATA, threshold result, or missing notification | [alarm-diagnostic-workflow.md](references/alarm-diagnostic-workflow.md), [alarm-evaluator-semantics.md](references/alarm-evaluator-semantics.md), [alarm-diagnosis-cli-contract.md](references/alarm-diagnosis-cli-contract.md); also read the metric references for metric replay | `evaluate_condition.py` |
| Plan a finite synthetic trigger test or investigate a successful empty alarm-history result | Also read [alarm-pipeline-troubleshooting.md](references/alarm-pipeline-troubleshooting.md) | `plan_trigger_samples.py` |

Do not load unrelated references merely because they are present.

## Quick examples

- “查询 `bj` 区域某个 BCC 实例最近两小时的 CPU 指标；先通过 BCM 元数据确认标识符、周期和单位，再查询趋势。”
- “为指定实例设计 CPU 告警策略；默认 `notifyEnabled=false`，只生成完整 JSON 和 `--dry-run`，不要执行创建。”
- “为指定 CFS 实例设计固定时段报警屏蔽；使用顶层业务 `region` 和 `instances[].dimensions`，只生成完整 JSON 和 `--dry-run`，不要执行创建。”
- “根据报警 ID 只读诊断为什么触发、恢复或没有通知；分别说明服务端记录、本地规则回放和推断。”
- “指标名在当前 `DescribeMetricCatalogs` 结果中不存在；停止构造请求，报告准确的 `scope/resourceType` 和缺失名称，不做模糊匹配。”
- “`--dry-run` 返回鉴权失败；停止操作，只报告脱敏后的错误原因和 `requestId`，不重试或更换 profile。”

## Package integrity

`SKILL.md`, `references/`, and `scripts/` are one atomic package. All route-linked references and helpers are package-local resources that must be distributed in the same release archive; they require no remote download. Before any CLI call, verify that every reference and helper named by the selected route exists locally.

If files are missing, do not degrade to guessed schemas or reconstructed scripts. Stop before any CLI call and return a structured package error containing `status: incomplete_package`, the selected route, every missing package-relative path, the detected package root, and the action “reinstall or extract the complete release archive.”

The route table is the authoritative package manifest: every file under `references/` and every executable helper under `scripts/` must be named there. Do not rely on an unlisted local file.

## Shared preconditions

1. Check `command -v bce`, `bce version`, `bce bcm --help`, and the selected operation's `--help`.
2. For a route that names a Python helper, check `python3 --version` and require Python 3.9 or newer; the packaged helpers use only the Python standard library. If the runtime is absent or too old, stop and report `missing_runtime` before constructing a cloud request.
3. If `bce` is unavailable, stop before constructing a request and direct the user to the [BCE CLI installation and configuration guide](https://cloud.baidu.com/doc/OpenAPI-Explorer/s/Smq6cpewk). Require BCE CLI `0.1.101` or newer because `0.1.101` introduced the BCM metric-metadata operations used by this Skill. Parse and compare the numeric `major.minor.patch` components from `bce version`; if the version is older or cannot be parsed, stop and report the detected output and minimum version.
4. Passing the version check is not sufficient. Require `bce bcm`, every operation needed by the selected route, its current help and generated skeleton, and the expected V3 routing in `--dry-run` when applicable. If an operation is absent or its current skeleton conflicts with the selected reference, stop and report the detected version, missing or incompatible capability, and selected route; do not guess an older command or API shape.
5. Use `bce configure list` only to confirm a usable profile. Never read, display, or request stored AK/SK values or credential files.
6. Confirm the global endpoint region separately from business data/resource regions. For metric queries, body `region` selects monitoring data and global `--region` selects the endpoint. A policy has no top-level body region; `target.region` applies only to exact `INSTANCES`.
7. Inspect the first dry-run endpoint and scheme for a new profile or override. Do not send identifiers or monitoring data across an untrusted public HTTP route, force an unsupported scheme, or silently downgrade HTTPS.
8. Use strict UTC timestamps and bounded pagination. Do not use `--debug` by default because signed headers and request bodies may be exposed.

## Operation safety and timeout handling

| Operation class | Before execution | Timeout or ambiguous result |
| --- | --- | --- |
| Read-only metadata, metric, or diagnosis request | Validate exact inputs; use bounded time and pagination | Retry the identical validated read at most once. Then report the failed page/window, partial coverage, and `requestId`; unknown is not empty or zero. |
| Policy, masking, group, template, action, state, or delete mutation | Validate JSON; dry-run; show redacted impact; obtain immediate confirmation; execute once; read back exact object | Never retry automatically. Use [alarm-policy-cli-contract.md](references/alarm-policy-cli-contract.md) to reconcile; a later attempt requires a new state read, preview, and confirmation. |
| Authentication or authorization failure | None | Stop immediately. Report the exact operation, redacted service code/message, and `requestId`; do not retry, change profile, inspect credentials, or propose permissions. |

A service `requestId` is diagnostic evidence, never an idempotency key unless a future operation explicitly documents that contract.

## Resource-access boundary

Do not proactively call BCC, CFS, RDS, BLB, or any other cloud-product API to discover, enrich, or validate instances. The availability of those commands in BCE CLI is not authorization to use them.

Resolve BCM alarm targets only through these supported paths:

- `ALL_INSTANCES`: no instance inventory is required. Explain that present and future matching resources are covered.
- `INSTANCE_GROUPS`: list and read exact group IDs with BCM `DescribeInstanceGroups` and `DescribeInstanceGroup`; do not query member products separately.
- `TAGS`: require the user to provide and confirm exact tag key/value pairs. Explain that multiple tags are OR alternatives.
- `INSTANCES`: require every identifier value and business region from the user, or reuse candidates from an existing BCM policy. If no exact policy was named, list only policies inside the already confirmed `scope/resourceType` with a safe projection and let the user select one; then read that exact policy. Match keys against `DescribeMetricCatalogs`, show protected candidates, and obtain confirmation before reuse. Never scan unrelated policies for identities or infer values from generic `id` fields.

Alarm history and a user-selected existing policy may provide identifiers for read-only correlation. Treat them as recorded identities, not proof that the resource still exists. For a synthetic end-to-end test, state that dispatcher product-side eligibility remains unverified unless the user separately supplies evidence or explicitly requests that product-side check.

## Metric mode

Resolve exact `scope`, `resourceType`, metric name, identifiers, dimensions, native period, and unit from BCM metadata before constructing a query. Actual identifier values still come from the user, an exact alarm record, an explicitly selected existing policy, or a BCM instance group. Validate every request against the same metric-catalog response. Keep metric mode read-only and report missing data as unknown, not zero.

## Alarm policy mode

Read current state, check semantic duplicates, resolve exact metadata and target inputs, and query a representative baseline before recommending a threshold. Examples and system templates are starting points, never production thresholds.

A new BCM policy is enabled immediately. Default a new design to `notifyEnabled=false` unless the user explicitly requests delivery and confirms destinations. Before every create, update, state change, action change, group/template mutation, or delete:

1. validate the exact JSON and run the exact CLI command with `--dry-run`;
2. show affected IDs, target scope, immediate state, rules, no-data behavior, notification impact, and a redacted rollback summary;
3. obtain confirmation immediately before execution;
4. execute once and read back the exact object.

## Alarm masking mode

Use the current installed operation help, [alarm-masking-cli-contract.md](references/alarm-masking-cli-contract.md), and `validate_alarm_masking.py`. For the validated V3 CLI shape, place the shared business region at top-level `region` and each instance selector under `instances[].dimensions`; never substitute the differently named nested fields from an unrelated request representation.

Resolve dimension keys and optional metric names from current BCM metadata, and pass the exact `DescribeMetricCatalogs` response to `validate_alarm_masking.py`. This validates names and selector structure, not whether an instance currently exists. Obtain dimension values only through the resource-access boundary above. A new masking rule is enabled immediately. Apply the mutation workflow in the safety table, then read the exact masking ID back and compare every intended non-secret field.

## Alarm diagnosis mode

Keep diagnosis read-only. Join the exact alarm, exact policy, metric metadata, and aligned metric windows. Classify evidence using these tests:

- **Recorded fact:** an exact field returned by a named service read, accompanied by its query scope/time and `requestId` when available.
- **Local replay:** a deterministic result calculated from explicitly listed policy and metric inputs; label it local and never claim the service made the same evaluation.
- **Inference:** any causal explanation not explicitly returned or deterministically replayed; state its assumptions, competing explanations, and next discriminating read-only check.

`rules` are OR groups, conditions within a group are AND, and the effective consecutive count is `rules[].pendingCount`. `notifyEnabled=false` suppresses delivery but not history after dispatcher admission.

A successful metric query proves TSDB visibility, not product-resource existence, policy matching, dispatcher admission, or AlarmHouse persistence. If history is successfully empty, report the first unverified checkpoint; do not automatically query another cloud product or blame the evaluator.

## Output and completion

Use minimal projections and redact receiver contacts, callback URLs, tokens, account IDs, and protected resource values. Preserve service `requestId` when available for tracing, but never treat it as an idempotency key unless a future documented API explicitly provides that contract. A mutation is complete only after read-back matches every intended non-secret field; a diagnosis is complete only when evidence, uncertainty, and the next discriminating read-only step are explicit.

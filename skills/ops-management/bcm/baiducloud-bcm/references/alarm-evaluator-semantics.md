# BCM evaluator semantics for diagnosis

## Rule evaluation

`rules` is OR; `rules[].conditions` is AND. Each OR group has its own effective `pendingCount` and `checkIntervalSeconds`. Top-level `pendingCount` is compatibility data and is not read by the current evaluator.

Evaluation windows align to `max(60, checkIntervalSeconds)`. Each condition aggregates samples over its `windowSeconds` using:

- `MAX`: largest value;
- `MIN`: smallest value;
- `SUM`: accumulated sum;
- `AVG`: accumulated sum divided by accumulated count.

`AVG` can be weighted. Do not average aggregate averages without their counts.

## Comparisons

Static operators compare the aggregate directly: `>`, `>=`, `<`, `<=`, `=`, `!=`. Equality uses an approximate `1e-6` tolerance.

Rate operators compare adjacent aggregation windows:

```text
changePercent = 100 * (current - previous) / abs(previous)
```

`INC_RATE_*` applies the suffix comparison to `changePercent`; `DEC_RATE_*` applies it to `-changePercent`. If `abs(previous) < 1e-6`, the evaluator produces no comparison.

## Consecutive triggering

An OR group becomes ALERT only when the most recent aligned windows contain at least `rules[].pendingCount` consecutive ALERT results with no gap. A non-alert evaluation breaks the sequence. Diagnose the entire sequence, not just the final metric point.

For a synthetic trigger test whose first sample can arrive at any alignment phase, use a conservative sustained-breach duration:

```text
effectiveCheckInterval = max(60, checkIntervalSeconds)
safeDuration = windowSeconds + pendingCount * effectiveCheckInterval
minimumSampleCount = ceil(safeDuration / cycleSeconds) + 1
```

This deliberately covers complete windows plus alignment/watermark advance. For `window=60`, `pendingCount=3`, `checkInterval=60`, and `cycle=10`, use at least 25 samples. Fewer samples can trigger when boundary alignment is favorable, but are not a robust validation plan. Keep producing current-timestamp data long enough for the watermark to pass the last required window, then use bounded polling.

Calculate the plan deterministically before a live test:

```bash
python3 <skill-directory>/scripts/plan_trigger_samples.py \
  --window-seconds 60 \
  --pending-count 3 \
  --check-interval-seconds 60 \
  --cycle-seconds 10
```

## Target matching

- exact instances: OR across instances, AND across one instance's dimensions;
- tags: OR across all configured key/value pairs;
- groups: OR across group IDs;
- metric-dimension filters: AND, with `=` or `!=`;
- including dimensions: all must exist;
- excluding dimensions: any existing key prevents a match.

Target region is business resource context for exact instances. It is not the global CLI endpoint region.

## NO_DATA and notification

`SHOW_NO_DATA_AND_NOTIFY` emits NO_DATA after its configured wait, subject to platform suppression. `SHOW_OK` maps missing data to OK. `notifyEnabled=false` stops delivery but not evaluation or alarm-history storage.

Correlated missing data can be suppressed by `(scope, resource region)` when platform heuristics identify a broad collection outage. This avoids a notification storm but means individual NO_DATA history alone is not a complete view of upstream health.

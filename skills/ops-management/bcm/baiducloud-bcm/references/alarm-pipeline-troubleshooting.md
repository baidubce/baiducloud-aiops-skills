# BCM empty alarm-history troubleshooting

Use this workflow only after `DescribeAlarms` itself returns a successful empty result and the exact policy, resource identity, metric metadata, and required consecutive windows have been verified.

## Evidence boundary

A BCM metric write fans the same accepted `ResourceMetrics` object to TSDB and the `resource-metrics` Kafka topic, but a successful trend query proves only the TSDB side. The alarm path still requires all of these joins:

```text
PutMetricsV1
  -> collector resource construction and identifier validation
  -> resource-metrics Kafka
  -> bcm-alarm policy watch/index
  -> binder resource + metric + target match
  -> applier / merger / emitter windows
  -> alarms Kafka
  -> alarm-dispatcher state decision
  -> AlarmHouse SaveAlarm
  -> DescribeAlarms
```

Find the first checkpoint whose counters or logs did not advance. Prefer deltas measured across one bounded marker sequence over cumulative values from a busy host.

Before treating an empty history result as an evaluator failure, validate the test resource. A synthetic identifier may be accepted by PutMetricsV1 and visible in TSDB but absent from the cloud product inventory used by the dispatcher.

## Checkpoints

### 1. Collector

Check `bcm_request_count{scope}`, `bcm_resource_metrics_count{scope}`, `bcm_metrics_count{scope}`, `bcm_kafka_metrics_count{topic="resource-metrics"}`, `kafka_error_count{topic}`, and `bcm_discarded_metrics_count{scope,reason}`.

For BCC V1 input, `resource.resourceId` becomes the `InstanceUuid` resource property and the supplied `InstanceId` becomes the resource identifier. Resource-object augmentation can fill a missing short ID, but it does not replace a non-empty short ID unless it equals the UUID. Compare keys and values without printing protected identifiers.

### 2. Policy loading and binder match

Check `server_watch_rev`, `alarm_policy_count{scope}`, `kafka_lag{partition}`, `alarm_in_metric_count{op="binder"}`, `alarm_out_metric_count{op="binder"}`, `alarm_late_metric_count{scope}`, and `alarm_metric_late_seconds{scope}`.

Interpret the deltas:

- no binder input: Kafka topic/cluster, consumer group, or lag problem;
- binder input but no binder output: policy not loaded or no match;
- policy count missing for the scope: manager watch/index problem;
- late counter rises: compare Kafka message timestamp, metric timestamp, configured lateness, and watermark delay.

The first policy-index key is exact `(userId, scope, resourceType)`. Target matching then checks exact instances against resource identifiers, metric dimensions, and resource properties. Metric name matching is exact and case-sensitive.

### 3. Evaluation and emission

Check `alarm_state_count{op,scope,kind}`, `op_watermark{op,key}`, `alarm_count{scope,state}`, `alarm_discarded_request_count{reason}`, `kafka_error_count{topic="alarms"}`, and relevant disk-queue/exporter errors. State gauges for `applier`, `merger`, and `emitter` should appear for a matched series. Binder output without applier state points to worker routing/export; applier state without `alarm_count` points to window alignment, pending-state, or watermark progression.

### 4. Dispatcher and history persistence

Check `ad_policy_count{scope}`, `ad_alarm_pipeline_total{scope,policy_type,alarm_state}`, `ad_alarm_preprocess_fail_total{reason}`, `ad_alarm_drop_total{reason}`, and `ad_alarm_state_update_total{sink,target_state,status}`. For a new state transition, AlarmHouse and Redis updates should succeed.

`notifyEnabled=false` changes the dispatcher decision to state-update-only; it still calls AlarmHouse for a non-repeat transition. Therefore it explains missing notification delivery, not missing history.

For cloud-product alarms, inspect `CloudProductFilter` before drawing that conclusion:

- Dispatcher calls the authoritative product `DescribeResource` adapter for OK, ALERT, and NO_DATA processing.
- A 404 or unavailable lifecycle result is classified as instance-deleted, changes the alarm to the CLOSED path, and sets `FilterDrop`. In the deployed path described for this environment, the alarm is dropped before normal AlarmHouse history delivery. The checked-out v2 source expresses this as `UpdateStateOnly` plus CLOSED, so confirm the deployed worker version when exact CLOSED-state persistence matters.
- For BCC, the current dispatcher source treats a present `SourceType` other than `console` as PaaS and filters it. Verify the deployed producer contract before changing synthetic payloads; do not claim this caused a run if the earlier resource lookup already returned 404.

Therefore a mock resource that cannot pass product lookup invalidates an end-to-end trigger/history test. It does not prove that bcm-alarm failed to match or emit the threshold event. Repeat with a real, product-resolvable test instance and a verified producer property contract before investigating evaluator internals.

At AlarmHouse, inspect `server_error_count{key="insertMysqlFailed"}` plus `SaveAlarm` logs and database errors. Preserve request or series correlation IDs in a protected channel; do not expose user IDs or resource values.

## Stop conditions

Do not mutate thresholds, pending counts, policy state, notification settings, or targets merely to locate a pipeline fault. Once one checkpoint fails to advance, report that boundary and request the corresponding service metrics/logs. If every checkpoint advances but history remains empty, investigate AlarmHouse query filters and persistence with the exact emitted series ID.

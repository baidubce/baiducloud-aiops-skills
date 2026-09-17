# BCM alarm resource targeting

## Target modes

| Type | Required body fields | Resource discovery | Runtime matching |
| --- | --- | --- | --- |
| `ALL_INSTANCES` | `type` | No instance discovery; report dynamic unbounded coverage | Every matching scope/resource type |
| `INSTANCES` | `instances`, `region` | User-supplied identifiers, or candidates from a user-selected existing BCM policy | Instances are OR; dimensions inside one instance are AND |
| `TAGS` | `tags` | Exact tags must be supplied and confirmed by the user | Tags are OR, including different keys |
| `INSTANCE_GROUPS` | `instanceGroups` | Resolve exact BCM group IDs | Groups are OR |

Do not translate multiple tags into an AND expression. The current evaluator returns a match when any configured key/value pair matches any resource tag. If the user asks for `env=prod AND app=payment`, exact instance resolution or a purpose-built instance group is safer unless the product provides a single unambiguous compound tag.

## Region fields

Three region concepts must stay separate:

- Global BCE CLI `--region`: selects the API endpoint; it is not request-body data.
- `CreateAlarmPolicy.target.region`: business region of exact `INSTANCES`; it is required only for that target mode.
- `CreateInstanceGroup.instances[].region`: business region of each group member, so an instance group can carry per-instance regions.

A policy has no top-level body region. One exact-instance target contains one `target.region`; do not combine resources from different business regions in that target. Use separate policies or a verified instance-group design.

## Metadata and allowed identifier sources

`DescribeResourceCatalogs` returns supported scope/resource-type metadata, not owned instances. `DescribeMetricCatalogs` returns `resourceIdentifiers` and `metricDimensions`, not identifier values. `DescribeDimensionValues` is metric-dimension discovery, not a general resource inventory API.

Do not proactively call BCC, CFS, RDS, BLB, or another cloud-product API to discover or validate instances. Resolve target values only as follows:

- `ALL_INSTANCES` needs no identifier values.
- `INSTANCE_GROUPS` uses exact IDs returned by BCM `DescribeInstanceGroups` and `DescribeInstanceGroup`.
- `TAGS` uses exact key/value pairs provided and confirmed by the user.
- `INSTANCES` uses identifiers and business region provided by the user. As a convenience, an existing BCM policy can provide candidates. If the user did not name one, list only policies in the already confirmed `scope/resourceType` with a safe projection, let the user select the exact policy, then read it. Extract target identifiers as protected candidates, match every key against current metric metadata, and wait for confirmation before reuse.

An alarm event can supply recorded identifiers for diagnosis. It does not establish current product-resource existence. Never infer a mapping from a generic `id` field, translated label, partial policy match, or unrelated policy.

## End-to-end alarm test eligibility

Separate API-level policy targeting from delivery-path test eligibility. The manager can accept a policy for an exact identifier, and the collector can store/query synthetic metrics for it, while the alarm dispatcher can still reject the resulting alarm after consulting the cloud product's authoritative resource API.

The Skill must not perform that product-side check automatically. Before claiming an exact instance is eligible for trigger, recovery, AlarmHouse history, or notification testing, require one of:

1. user-provided evidence that the exact identifiers currently resolve and the lifecycle state is usable; or
2. a separate, explicit user request authorizing a named product-side read.

Without that evidence, continue only with API-level policy validation or metric analysis and mark dispatcher admission as unverified. A 404/deleted resource can enter the instance-deleted/CLOSED filter path. For BCC, an incompatible `SourceType` can also be filtered; do not invent or rewrite it without a verified producer contract.

A mock identity absent from product inventory remains suitable for metric ingestion/query and policy request validation, but not for a full alarm delivery/history test.

## Dimension-presence selectors

`includingDimensions` means every named key must exist on the resource identifiers or metric dimensions. It also contributes to the alarm-series identity. `excludingDimensions` rejects a series if any named key exists. These lists select metric shapes; they do not supply values and do not replace `metricDimensions` filters.

Only use keys declared by the selected metric catalog. Keep the two lists disjoint.

## Impact preview

Before confirmation, show:

- exact or estimated count and whether it can drift dynamically;
- protected stable identifiers for exact instances and exact IDs/names for BCM instance groups; do not promise product display names unless the user supplied them;
- business region or regions;
- tags and their OR semantics;
- whether future resources will become covered automatically;
- unresolved or ambiguous identifiers and whether current product existence is unverified;
- pagination coverage and the timestamp of BCM discovery or user confirmation.

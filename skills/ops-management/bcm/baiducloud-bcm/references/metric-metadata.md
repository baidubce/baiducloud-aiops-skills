# BCM metric metadata resolution

## Resource catalog

`DescribeResourceCatalogs` is the starting point. Resolve:

1. An exact cloud-product `scope`, such as `BCE_APIGW`.
2. An exact resource `resourceType`, such as `Group`.

Names are stable request identifiers. Labels are localized display text and are not substitutes for names. If a label or partial user phrase matches multiple entries, present the candidates and require an exact selection.

A resource catalog describes resource types and may include fixed supported `regions`. It does not enumerate the user's resource instances. Obtain actual identifier values from the user, an exact BCM alarm record, an existing BCM policy the user explicitly selected, or a BCM instance group. Do not proactively call another cloud product's API to discover or enrich instances.

## Metric catalog

Call `DescribeMetricCatalogs` with the exact scope and resource type. The response is a recursive tree: each catalog can contain `metrics` and child `catalogs`; either field can be absent, `null`, or an empty list.

Flatten a saved response with:

```bash
python3 <skill-directory>/scripts/flatten_metric_catalog.py \
  /absolute/path/metric-catalog-response.json
```

Add `--name <exact-name>` or `--label <exact-label>` for exact filtering. The output includes the full catalog path so duplicate metric names can be detected and disambiguated.

For the selected metric, retain:

| Field | Meaning | Query rule |
| --- | --- | --- |
| `name` | Stable metric identifier | Match exactly, including case |
| `label` | Localized display text | Display only |
| `resourceIdentifiers` | Keys identifying a resource of this type | Every key must be present in filters |
| `metricDimensions` | Additional supported grouping/filter dimensions | Only these extra keys may appear in filters |
| `period` + `periodUnit` | Native sampling period | Query period must not be smaller |
| `unit` | Raw value unit | Preserve during interpretation |

Do not treat catalog path names or labels as filter dimensions.

BCM V3 can return a positive `period` with an empty-string `periodUnit` for
second-based metrics. The bundled tools preserve the raw empty unit, interpret
the positive period as seconds for lower-bound validation, and emit a
compatibility warning. A `null` unit or an unknown non-empty unit remains
unresolved; do not guess its conversion.

## Filters and actual resources

Allowed query filter keys are exactly:

```text
resourceIdentifiers union metricDimensions
```

All resource identifiers are required. Metric dimensions are optional. Keys are case-sensitive and cannot be duplicated.

Supported filter forms are:

```json
{"key": "InstanceId", "op": "=", "value": "i-example"}
{"key": "InstanceId", "op": "!=", "value": "i-example"}
{"key": "InstanceId", "op": "in", "values": ["i-example-1", "i-example-2"]}
```

For `DescribeDimensionValues`, `dimensionKey` must be one of `metricDimensions`, not a resource identifier. Include all required resource identifiers in `filters` before asking for downstream dimension values. This operation discovers metric dimension values, not cloud resources.

## Ambiguity handling

- No exact scope/resource/metric match: stop and show discovered candidates; never autocorrect silently.
- Duplicate exact metric names with identical metadata: still retain the full path and state which path was selected.
- Duplicate exact names with different identifiers, dimensions, period, or unit: require an exact `--catalog-path`.
- Empty catalog response: report that metadata is unavailable for the selected scope/resource type; do not invent a request.

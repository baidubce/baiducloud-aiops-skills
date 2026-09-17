# BCM metric CLI contract

## Supported read-only operations

| Operation | Purpose | Body region |
| --- | --- | --- |
| `DescribeResourceCatalogs` | Discover stable cloud-product scopes and resource types | Not accepted |
| `DescribeMetricCatalogs` | Discover metrics and their query metadata | Not accepted |
| `DescribeDimensionValues` | Discover values of a declared metric dimension | Optional |
| `DescribeMetricData` | Query a bounded metric time series | Required |
| `DescribeMetricDataLatest` | Query the latest value of matching curves | Required |
| `DescribeMetricDataLatestTop` | Rank matching curves by latest value | Required |

The current query-operation help can display `--region` twice: once among generated operation fields and once among global flags. These have distinct meanings:

- Body `region` is a BCM metric-query field that selects the monitoring-data region. It is required for all three metric-data operations and optional for dimension-value discovery.
- Global CLI `--region` selects the service endpoint.

The values are often identical, such as both being `bj`, but one must not be removed or inferred solely from the other. When a caller needs different values, keep them explicit and label them as query-data region and endpoint region.

Do not include generated `version` or `action` fields. Selecting the CLI operation supplies those routing fields. Use current operation help to detect future CLI changes, but do not weaken these invariants without an updated service contract.

## CLI checks

```bash
command -v bce
bce version
bce bcm --help
bce bcm DescribeResourceCatalogs --help
bce bcm DescribeMetricCatalogs --help
bce bcm DescribeMetricData --help
```

BCE CLI `0.1.101` is the minimum version because it introduced the BCM metric-metadata operations used by these workflows. Parse the numeric `major.minor.patch` output of `bce version` and stop if it is older or unparseable. Version eligibility is only the first gate: require every selected operation in `bce bcm --help`, inspect its current help and generated skeleton, and verify the expected `/v3/bcm` route with `--dry-run`. A missing operation or unexpected route is not permission to guess another command, fall back to a legacy operation, or reconstruct a request from memory.

If `bce` is unavailable, stop before constructing a request and use the [BCE CLI installation and configuration guide](https://cloud.baidu.com/doc/OpenAPI-Explorer/s/Smq6cpewk).

Confirm a configured profile with `bce configure list`; never inspect the credential file or display secret keys. On an authentication or authorization failure, stop immediately and report the exact operation, redacted service error code/message, and `requestId` when returned. Do not retry or change the profile.

## Metadata requests

Use stable names returned by the resource catalog, not translated labels:

```bash
bce bcm DescribeResourceCatalogs \
  --profile <profile> \
  --region <endpoint-region> \
  --locale zh-cn \
  --output json

bce bcm DescribeMetricCatalogs \
  --profile <profile> \
  --region <endpoint-region> \
  --scope <exact-scope> \
  --resourceType <exact-resource-type> \
  --locale zh-cn \
  --output json
```

Use `--cli-input-json file://<absolute-path>` for metric requests. Put the metric-query body `region` in that JSON. Keep `--profile`, global endpoint `--region`, `--endpoint`, `--scheme`, `--output`, `--query`, `--timeout`, and `--dry-run` on the command line.

## Endpoint overrides and dry runs

- Use a profile's standard endpoint by default.
- Use `--endpoint` and `--scheme` only when the environment owner provides an approved override.
- Do not copy sandbox hostnames or private IPs into reusable Skill files or requests.
- On a first request, add `--dry-run` and verify both the resolved endpoint and a body with the intended query-data `region` and no `version` or `action` fields.
- If the resolved scheme is HTTP, do not send resource identifiers or monitoring data across an untrusted public network. Require a trusted/private route or an approved HTTPS-capable endpoint when transport policy matters.
- Do not force an unsupported scheme or silently downgrade an explicitly supplied HTTPS endpoint.
- Do not enable `--debug` by default; it may expose signed headers and body content.

## JSON and pagination

Use `--output json` for analysis. Retain service error `code`, `message`, and `requestId`. `DescribeMetricData` and `DescribeMetricDataLatest` can match multiple curves, so use `limit` up to 100 and increment `offset` until the required coverage is reached. `DescribeMetricDataLatestTop` has `limit` but no offset and returns at most the requested TopN.

## Read timeouts and partial results

A metric read timeout is not evidence of no data. For one bounded request or page, retry the identical validated read at most once when the endpoint and transport remain trusted. Do not change identifiers, region, time range, aggregation, period, pagination, or profile during that retry.

If the retry also times out, stop that query and report the exact time window or page offset, which earlier pages completed, whether any returned data is partial, and the service `requestId` when available. Do not merge partial pages into a complete-looking result, widen the time range, silently switch operations, or convert unknown values to zero.

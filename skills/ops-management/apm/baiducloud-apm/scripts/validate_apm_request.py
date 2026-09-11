#!/usr/bin/env python3
"""Validate BCE APM metric request JSON without calling the cloud API."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    pass


DIRECT_OPERATORS = {"=", "!=", "contains", "not contains", "in", "not in", "notIn"}
MULTI_OPERATORS = {"in", "not in", "notIn"}
TRACE_STABLE_METRICS = {
    "apm_requests_count",
    "apm_error_requests_count",
    "apm_requests_seconds_avg",
    "apm_requests_seconds_p90",
    "apm_requests_seconds_p95",
    "apm_requests_seconds_p99",
}
TRACE_STABLE_OPERATORS = {"=", "!=", "in"}
DIRECT_FORBIDDEN_PUBLIC_FIELDS = {"service", "kind", "host"}
TRACE_FORBIDDEN_PROM_FIELDS = {"service.name", "span.kind", "host.name", "component", "operation", "http.status"}
TRACE_PUBLIC_FIELDS = {
    "service",
    "name",
    "kind",
    "host",
    "duration",
    "traceId",
    "statusCode",
    "hasException",
    "exception.type",
    "attributes.apm.operation",
    "attributes.apm.component",
    "attributes.db.system",
    "attributes.db.statement.id",
    "attributes.db.statement",
    "attributes.db.name",
    "attributes.http.response.status_code",
    "slow.status",
    "slowRequest",
    "slowDBRequest",
    "env",
}


def _latency_metrics(prefix: str, statistics: set[str]) -> set[str]:
    return {f"{prefix}_{statistic}" for statistic in statistics}


RAW_LATENCY_STATISTICS = {"count", "sum", "min", "max", "bucket"}
PUBLIC_LATENCY_STATISTICS = {"avg", "p50", "p90", "p95", "p99"}
KNOWN_DIRECT_METRICS = {
    "apm_requests_count",
    "apm_requests_per_second",
    "apm_error_requests_count",
    "apm_error_requests_per_second",
    "apm_error_rate",
    "apm_slow_requests_count",
    "apm_slow_requests_per_second",
    "apm_exceptions_requests_count",
    "apm_exceptions_requests_per_second",
    "apm_db_requests_count",
    "apm_db_requests_per_second",
    "apm_db_error_requests_count",
    "apm_db_error_requests_per_second",
    "apm_db_error_rate",
    "apm_db_slow_requests_count",
    "apm_db_slow_requests_per_second",
    "process.runtime.cpython.gc_count",
    "process.runtime.cpython.gc.collections",
    "process.runtime.cpython.gc.duration",
    "process.runtime.cpython.gc.duration_avg",
    "process.runtime.cpython.cpu_time",
    "process.runtime.cpython.cpu.utilization",
    "process.runtime.cpython.memory",
    "process.runtime.cpython.thread_count",
    "process.runtime.cpython.context_switches",
    "process.runtime.go.gc.count",
    "process.runtime.go.gc.pause_total_ns",
    "process.runtime.go.gc.pause_ns",
    "process.runtime.go.gc.pause_ns_sum",
    "process.runtime.go.mem.heap_alloc",
    "process.runtime.go.mem.heap_idle",
    "process.runtime.go.mem.heap_inuse",
    "process.runtime.go.mem.heap_released",
    "process.runtime.go.mem.heap_sys",
    "process.runtime.go.mem.live_objects",
    "process.runtime.go.mem.heap_objects",
    "process.runtime.go.cgo.calls",
    "process.runtime.go.mem.lookups",
    "process.runtime.go.goroutines",
    "runtime.uptime",
    "jvm.class.count",
    "jvm.class.loaded",
    "jvm.class.unloaded",
    "jvm.cpu.count",
    "jvm.cpu.recent_utilization",
    "jvm.cpu.time",
    "jvm.gc.duration_bucket",
    "jvm.gc.duration_count",
    "jvm.gc.duration_sum",
    "jvm.gc.duration_avg",
    "jvm.memory.committed",
    "jvm.memory.limit",
    "jvm.memory.used",
    "jvm.memory.used_after_last_gc",
    "jvm.thread.count",
    "jvm.cpu.recent_utilization_avg",
    "jvm.cpu.count_avg",
    "jvm.cpu.time_sum",
    "jvm.class.count_pre_second",
    "jvm.class.loaded_per_second",
    "jvm.class.loaded_count",
    "jvm.class.unloaded_per_second",
    "jvm.class.unloaded_count",
    "ab_success_rate",
    "ab_error_rate",
    "ab_requests_seconds_avg",
    "apm_topo_requests_count",
    "apm_topo_error_requests_count",
    "apm_topo_requests_seconds_avg",
    "apm_topo_slow_requests_count",
    "apm_topo_requests_per_second",
}
KNOWN_DIRECT_METRICS |= _latency_metrics("apm_requests_seconds", RAW_LATENCY_STATISTICS | PUBLIC_LATENCY_STATISTICS)
KNOWN_DIRECT_METRICS |= _latency_metrics(
    "apm_error_requests_seconds", RAW_LATENCY_STATISTICS | {"avg", "p90", "p95", "p99"}
)
KNOWN_DIRECT_METRICS |= _latency_metrics(
    "apm_slow_requests_seconds", RAW_LATENCY_STATISTICS | {"avg", "p90", "p95", "p99"}
)
KNOWN_DIRECT_METRICS |= _latency_metrics("apm_db_requests_seconds", RAW_LATENCY_STATISTICS | PUBLIC_LATENCY_STATISTICS)
KNOWN_DIRECT_METRICS |= _latency_metrics(
    "apm_db_error_requests_seconds", RAW_LATENCY_STATISTICS | PUBLIC_LATENCY_STATISTICS
)
KNOWN_DIRECT_METRICS |= _latency_metrics(
    "apm_db_slow_requests_seconds", RAW_LATENCY_STATISTICS | PUBLIC_LATENCY_STATISTICS
)
KNOWN_DIRECT_METRICS |= {
    f"apm_error_requests_{status}_{suffix}"
    for status in {"4xx", "400", "401", "403", "404", "5xx", "500", "501", "503"}
    for suffix in {"count", "per_second"}
}
KNOWN_DIRECT_METRICS |= {
    f"jvm.gc.duration_{generation}_{statistic}"
    for generation in {"new_gen", "old_gen"}
    for statistic in {"per_second", "count", "avg", "sum", "max", "min"}
}
KNOWN_DIRECT_METRICS |= {
    f"jvm.memory.{measurement}_{memory_type}_{statistic}"
    for measurement in {"used", "limit", "committed"}
    for memory_type in {"heap", "non_heap"}
    for statistic in {"pre_second", "count"}
}
KNOWN_DIRECT_METRICS |= {
    f"jvm.memory.used_{pool}_{statistic}"
    for pool in {"eden_space", "survivor_space", "old_gen", "metaspace", "compressed_class_space", "code_heap"}
    for statistic in {"pre_second", "count"}
}
KNOWN_DIRECT_METRICS |= {
    f"jvm.thread.count_{state}_{statistic}"
    for state in {"runnable", "waiting", "timed_waiting", "blocked", "terminated"}
    for statistic in {"pre_second", "count"}
}
KNOWN_DIRECT_METRICS |= {"jvm.thread.count_pre_second", "jvm.thread.count_count"}


def _strict_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a strict UTC string")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValidationError(f"{field} must match YYYY-MM-DDTHH:mm:ssZ") from exc
    return parsed


def _validate_filters(filters: Any, *, direct: bool, path: str, warnings: list[str]) -> None:
    if filters is None:
        return
    if not isinstance(filters, list):
        raise ValidationError(f"{path} must be a list")
    for index, item in enumerate(filters):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{item_path} must be an object")
        key = item.get("key")
        op = item.get("op")
        if not isinstance(key, str) or not key:
            raise ValidationError(f"{item_path}.key must be non-empty")
        if direct and (key in DIRECT_FORBIDDEN_PUBLIC_FIELDS or key.startswith("attributes.")):
            raise ValidationError(f"{item_path}.key {key!r} is a Trace public field; use a Prom label")
        if not direct:
            if key in TRACE_FORBIDDEN_PROM_FIELDS:
                raise ValidationError(f"{item_path}.key {key!r} is a Prom label; use the Trace public field")
            if key not in TRACE_PUBLIC_FIELDS and not key.startswith("attributes."):
                raise ValidationError(f"{item_path}.key {key!r} is not a public Trace field")
        if not isinstance(op, str) or not op:
            raise ValidationError(f"{item_path}.op must be non-empty")
        if direct and op not in DIRECT_OPERATORS:
            raise ValidationError(f"{item_path}.op {op!r} is not supported by direct metric queries")
        if not direct and op not in TRACE_STABLE_OPERATORS:
            warnings.append(f"{item_path}.op {op!r} is route-dependent; verify operation help and storage semantics")
        if op in MULTI_OPERATORS or op == "in":
            values = item.get("values")
            if not isinstance(values, list) or not values:
                raise ValidationError(f"{item_path}.values must be a non-empty list for {op!r}")
        elif "value" not in item or item.get("value") in (None, ""):
            raise ValidationError(f"{item_path}.value must be present for {op!r}")


def validate_request(data: Any, operation: str, allowed_metrics: set[str] | None = None) -> list[str]:
    if not isinstance(data, dict):
        raise ValidationError("request must be a JSON object")
    if operation not in {"DescribeMetricData", "DescribeTraceMetricData"}:
        raise ValidationError("operation must be DescribeMetricData or DescribeTraceMetricData")

    warnings: list[str] = []
    begin = _strict_utc(data.get("beginDatetime"), "beginDatetime")
    end = _strict_utc(data.get("endDatetime"), "endDatetime")
    if begin >= end:
        raise ValidationError("beginDatetime must be earlier than endDatetime")

    version = data.get("version")
    if version not in (None, "", "1", 1):
        raise ValidationError("APM request version must be 1 when present")
    action = data.get("action")
    if action not in (None, "", operation):
        raise ValidationError(f"action {action!r} conflicts with operation {operation}")

    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ValidationError("metrics must be a non-empty list")
    metric_names: list[str] = []
    metric_overrides = allowed_metrics or set()
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ValidationError(f"metrics[{index}] must be an object")
        name = metric.get("name")
        if not isinstance(name, str) or not name:
            raise ValidationError(f"metrics[{index}].name must be non-empty")
        if "_by_srv_" in name:
            raise ValidationError(f"{name} is a pre-aggregated metric; request a public metric instead")
        if name == "apm_topo_error_rate":
            raise ValidationError("apm_topo_error_rate is blocked because its formula is unresolved")
        if operation == "DescribeTraceMetricData" and name not in TRACE_STABLE_METRICS:
            raise ValidationError(f"{name} is not in the stable Trace metric set")
        if operation == "DescribeMetricData":
            if name not in KNOWN_DIRECT_METRICS and name not in metric_overrides:
                raise ValidationError(
                    f"metrics[{index}].name {name!r} is not in the verified APM metric catalog; "
                    "confirm it from a trusted current source and pass --allow-metric"
                )
            if name in metric_overrides and name not in KNOWN_DIRECT_METRICS:
                warnings.append(f"metrics[{index}].name {name!r} was accepted by explicit override")
            _validate_filters(metric.get("filters"), direct=True, path=f"metrics[{index}].filters", warnings=warnings)
        else:
            if "filters" in metric:
                raise ValidationError(
                    f"metrics[{index}].filters is not part of DescribeTraceMetricData; use top-level filters"
                )
            if "compareTo" in metric:
                raise ValidationError(f"metrics[{index}].compareTo is not part of DescribeTraceMetricData")
        metric_names.append(name)

    direct = operation == "DescribeMetricData"
    _validate_filters(data.get("filters"), direct=direct, path="filters", warnings=warnings)

    if not direct:
        unsupported = {"orderBy", "order", "limit", "reserveEmptyDimensions"} & data.keys()
        if unsupported:
            raise ValidationError(
                f"DescribeTraceMetricData does not accept top-level fields {sorted(unsupported)}"
            )

    group_by = data.get("groupBy", [])
    if not isinstance(group_by, list) or any(not isinstance(item, str) or not item for item in group_by):
        raise ValidationError("groupBy must be a list of non-empty strings")
    if direct and any(item in {"service", "kind", "host"} or item.startswith("attributes.") for item in group_by):
        raise ValidationError("DescribeMetricData groupBy must use Prom labels, not Trace public fields")
    if not direct:
        for item in group_by:
            if item in TRACE_FORBIDDEN_PROM_FIELDS:
                raise ValidationError("DescribeTraceMetricData groupBy must use Trace public fields, not Prom labels")
            if item not in TRACE_PUBLIC_FIELDS and not item.startswith("attributes."):
                raise ValidationError(f"DescribeTraceMetricData groupBy field {item!r} is not a public Trace field")

    period = data.get("periodSeconds", 0)
    if not isinstance(period, int) or isinstance(period, bool) or period < 0:
        raise ValidationError("periodSeconds must be a non-negative integer")

    limit = data.get("limit")
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 0 or limit > 1000):
        raise ValidationError("limit must be an integer from 0 to 1000")
    if direct and group_by and (limit is None or limit == 0):
        warnings.append("grouped query has no positive explicit TopN limit")

    order_by = data.get("orderBy")
    if order_by not in (None, "") and order_by not in metric_names:
        raise ValidationError("orderBy must name a metric in the same request")
    if data.get("order") not in (None, "", "asc", "desc"):
        raise ValidationError("order must be asc or desc")

    aggregate = data.get("aggregate", [])
    if aggregate:
        if operation != "DescribeTraceMetricData":
            raise ValidationError("aggregate is supported here only for DescribeTraceMetricData")
        if not isinstance(aggregate, list) or any(item not in {"sum", "sumPerSecond"} for item in aggregate):
            raise ValidationError("aggregate values must be sum or sumPerSecond")
        if len(metrics) != 1:
            raise ValidationError("aggregate requests must contain exactly one metric")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--operation", required=True, choices=["DescribeMetricData", "DescribeTraceMetricData"])
    parser.add_argument(
        "--allow-metric",
        action="append",
        default=[],
        metavar="NAME",
        help="accept one exact metric confirmed from a trusted current source; repeat as needed",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.request.read_text(encoding="utf-8"))
        warnings = validate_request(data, args.operation, set(args.allow_metric))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"valid": True, "operation": args.operation, "warnings": warnings}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

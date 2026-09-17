#!/usr/bin/env python3
"""Validate a BCM V3 read-only metric request against metric catalog JSON."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    """Raised when a metric request violates the BCM V3 contract."""


OPERATIONS = {
    "DescribeMetricData",
    "DescribeMetricDataLatest",
    "DescribeMetricDataLatestTop",
    "DescribeDimensionValues",
}
COMMON_FIELDS = {"scope", "metricName", "filters"}
ALLOWED_FIELDS = {
    "DescribeMetricData": COMMON_FIELDS
    | {
        "region",
        "resourceType",
        "beginDatetime",
        "endDatetime",
        "limit",
        "offset",
        "periodSeconds",
        "aggregationOverTime",
    },
    "DescribeMetricDataLatest": COMMON_FIELDS
    | {
        "region",
        "resourceType",
        "endDatetime",
        "limit",
        "offset",
        "periodSeconds",
        "aggregationOverTime",
    },
    "DescribeMetricDataLatestTop": COMMON_FIELDS
    | {"region", "endDatetime", "limit", "asc", "periodSeconds", "aggregationOverTime"},
    "DescribeDimensionValues": COMMON_FIELDS
    | {"region", "resourceType", "beginDatetime", "endDatetime", "dimensionKey"},
}
REQUIRED_FIELDS = {
    "DescribeMetricData": COMMON_FIELDS
    | {"region", "resourceType", "beginDatetime", "endDatetime"},
    "DescribeMetricDataLatest": COMMON_FIELDS | {"region", "resourceType", "endDatetime"},
    "DescribeMetricDataLatestTop": COMMON_FIELDS | {"region", "endDatetime"},
    "DescribeDimensionValues": COMMON_FIELDS
    | {"resourceType", "beginDatetime", "endDatetime", "dimensionKey"},
}
LIST_AGGREGATIONS = {"avg", "sum", "max", "min", "count"}
TOP_AGGREGATIONS = {"avg", "sum", "max", "min"}
SINGLE_FILTER_OPERATORS = {"=", "!="}
MULTI_FILTER_OPERATORS = {"in"}
FORBIDDEN_ROUTING_FIELDS = {"version", "action"}
MAX_TREND_RANGE_SECONDS = 31 * 24 * 60 * 60
MAX_POINTS_PER_CURVE = 1440


def _load_flatten_module() -> Any:
    path = Path(__file__).with_name("flatten_metric_catalog.py")
    spec = importlib.util.spec_from_file_location("bcm_flatten_metric_catalog", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


flatten_metric_catalog = _load_flatten_module()


def _strict_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a strict UTC string")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValidationError(f"{field} must match YYYY-MM-DDTHH:mm:ssZ") from exc


def _positive_int(value: Any, field: str, *, maximum: int | None = None) -> int:
    if type(value) is not int or value <= 0:
        raise ValidationError(f"{field} must be a positive integer")
    if maximum is not None and value > maximum:
        raise ValidationError(f"{field} must be at most {maximum}")
    return value


def _non_negative_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValidationError(f"{field} must be a non-negative integer")
    return value


def _metric_signature(metric: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(metric["resourceIdentifiers"]),
        tuple(metric["metricDimensions"]),
        metric["period"],
        metric["periodUnit"],
        metric["unit"],
    )


def _select_metric(
    catalog: dict[str, Any], metric_name: str, catalog_path: str | None, warnings: list[str]
) -> dict[str, Any]:
    try:
        matches = flatten_metric_catalog.flatten_catalog(catalog, name=metric_name)
    except flatten_metric_catalog.CatalogError as exc:
        raise ValidationError(f"invalid metric catalog: {exc}") from exc

    if catalog_path is not None:
        expected = [segment for segment in catalog_path.split("/") if segment]
        matches = [metric for metric in matches if metric["catalogPath"] == expected]
    if not matches:
        detail = f" under catalog path {catalog_path!r}" if catalog_path else ""
        raise ValidationError(f"metricName {metric_name!r} has no exact catalog match{detail}")
    if len(matches) == 1:
        return matches[0]

    signatures = {_metric_signature(metric) for metric in matches}
    paths = ["/".join(metric["catalogPath"]) or "<root>" for metric in matches]
    if len(signatures) > 1:
        raise ValidationError(
            f"metricName {metric_name!r} is ambiguous across catalog paths {paths}; pass --catalog-path"
        )
    warnings.append(
        f"metricName {metric_name!r} appears with identical metadata at {paths}; selected {paths[0]}"
    )
    return matches[0]


def _validate_filters(filters: Any, metric: dict[str, Any]) -> list[str]:
    if not isinstance(filters, list):
        raise ValidationError("filters must be a list")
    identifiers = metric["resourceIdentifiers"]
    dimensions = metric["metricDimensions"]
    allowed_keys = set(identifiers) | set(dimensions)
    seen: set[str] = set()

    for index, item in enumerate(filters):
        path = f"filters[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{path} must be an object")
        unknown = set(item) - {"key", "op", "value", "values"}
        if unknown:
            raise ValidationError(f"{path} contains unsupported fields: {sorted(unknown)}")
        key = item.get("key")
        operation = item.get("op")
        if not isinstance(key, str) or not key:
            raise ValidationError(f"{path}.key must be a non-empty string")
        if key not in allowed_keys:
            raise ValidationError(
                f"{path}.key {key!r} is not declared in resourceIdentifiers or metricDimensions"
            )
        if key in seen:
            raise ValidationError(f"duplicate filter key {key!r}")
        seen.add(key)
        if not isinstance(operation, str):
            raise ValidationError(f"{path}.op must be one of '=', '!=', or 'in'")
        if operation in SINGLE_FILTER_OPERATORS:
            if set(item) - {"key", "op", "value"}:
                raise ValidationError(f"{path} operator {operation!r} accepts value, not values")
            if not isinstance(item.get("value"), str) or not item["value"]:
                raise ValidationError(f"{path}.value must be a non-empty string for {operation!r}")
        elif operation in MULTI_FILTER_OPERATORS:
            if set(item) - {"key", "op", "values"}:
                raise ValidationError(f"{path} operator 'in' accepts values, not value")
            values = item.get("values")
            if not isinstance(values, list) or not values:
                raise ValidationError(f"{path}.values must be a non-empty list for 'in'")
            if any(not isinstance(value, str) or not value for value in values):
                raise ValidationError(f"{path}.values must contain only non-empty strings")
        else:
            raise ValidationError(f"{path}.op must be one of '=', '!=', or 'in'")

    missing_identifiers = [identifier for identifier in identifiers if identifier not in seen]
    if missing_identifiers:
        raise ValidationError(f"filters are missing required resource identifiers: {missing_identifiers}")
    return sorted(seen)


def _validate_aggregation(data: dict[str, Any], operation: str) -> None:
    if "aggregationOverTime" not in data:
        return
    value = data["aggregationOverTime"]
    if operation == "DescribeMetricDataLatestTop":
        if not isinstance(value, str) or value not in TOP_AGGREGATIONS:
            raise ValidationError("aggregationOverTime must be one of avg, sum, max, or min for LatestTop")
        return
    if not isinstance(value, list) or not value:
        raise ValidationError("aggregationOverTime must be a non-empty list")
    if any(not isinstance(item, str) or item not in LIST_AGGREGATIONS for item in value):
        raise ValidationError("aggregationOverTime contains an unsupported aggregation")
    if len(value) != len(set(value)):
        raise ValidationError("aggregationOverTime must not contain duplicates")


def validate_request(
    data: Any,
    operation: str,
    catalog: Any,
    scope: str,
    resource_type: str,
    catalog_path: str | None = None,
) -> dict[str, Any]:
    """Validate request data and return normalized metadata and warnings."""

    if operation not in OPERATIONS:
        raise ValidationError(f"unsupported operation {operation!r}")
    if not isinstance(data, dict):
        raise ValidationError("request must be a JSON object")
    if not isinstance(catalog, dict):
        raise ValidationError("metric catalog must be a JSON object")
    if not isinstance(scope, str) or not scope:
        raise ValidationError("--scope must be a non-empty string")
    if not isinstance(resource_type, str) or not resource_type:
        raise ValidationError("--resource-type must be a non-empty string")

    routing_fields = sorted(set(data) & FORBIDDEN_ROUTING_FIELDS)
    if routing_fields:
        raise ValidationError(f"routing fields do not belong in request JSON: {routing_fields}")
    unknown = sorted(set(data) - ALLOWED_FIELDS[operation])
    if unknown:
        raise ValidationError(f"unsupported fields for {operation}: {unknown}")
    missing = sorted(field for field in REQUIRED_FIELDS[operation] if field not in data)
    if missing:
        raise ValidationError(f"missing required fields for {operation}: {missing}")

    if "region" in data and (not isinstance(data["region"], str) or not data["region"]):
        raise ValidationError("region must be a non-empty string")

    if data.get("scope") != scope:
        raise ValidationError(f"request scope must exactly match metadata scope {scope!r}")
    if operation != "DescribeMetricDataLatestTop" and data.get("resourceType") != resource_type:
        raise ValidationError(
            f"request resourceType must exactly match metadata resource type {resource_type!r}"
        )
    metric_name = data.get("metricName")
    if not isinstance(metric_name, str) or not metric_name:
        raise ValidationError("metricName must be a non-empty string")

    warnings: list[str] = []
    metric = _select_metric(catalog, metric_name, catalog_path, warnings)
    if (
        metric["period"] is not None
        and isinstance(metric["periodUnit"], str)
        and not metric["periodUnit"].strip()
    ):
        warnings.append(
            "catalog periodUnit is empty; interpreted the positive period as seconds "
            "for BCM V3 compatibility"
        )
    filter_keys = _validate_filters(data.get("filters"), metric)

    begin: datetime | None = None
    end: datetime | None = None
    if "beginDatetime" in data:
        begin = _strict_utc(data["beginDatetime"], "beginDatetime")
    if "endDatetime" in data:
        end = _strict_utc(data["endDatetime"], "endDatetime")
    if begin is not None and end is not None:
        if operation == "DescribeMetricData" and begin >= end:
            raise ValidationError("beginDatetime must be earlier than endDatetime")
        if operation == "DescribeDimensionValues" and begin > end:
            raise ValidationError("beginDatetime must not be later than endDatetime")

    if "limit" in data:
        _positive_int(data["limit"], "limit", maximum=100)
    if "offset" in data:
        _non_negative_int(data["offset"], "offset")
    if "asc" in data and type(data["asc"]) is not bool:
        raise ValidationError("asc must be a boolean")
    _validate_aggregation(data, operation)

    estimated_points: int | None = None
    if "periodSeconds" in data:
        period_seconds = _positive_int(data["periodSeconds"], "periodSeconds")
        native_period = metric["periodSeconds"]
        if native_period is not None:
            if period_seconds < native_period:
                raise ValidationError(
                    f"periodSeconds {period_seconds} is smaller than native metric period {native_period}"
                )
            if period_seconds % native_period != 0:
                warnings.append(
                    f"periodSeconds {period_seconds} is not a multiple of native metric period {native_period}"
                )
    else:
        period_seconds = None

    if operation == "DescribeMetricData":
        assert begin is not None and end is not None
        range_seconds = int((end - begin).total_seconds())
        if range_seconds > MAX_TREND_RANGE_SECONDS:
            raise ValidationError("DescribeMetricData time range must not exceed 31 days")
        if period_seconds is None:
            warnings.append("periodSeconds is omitted; the service will choose an adaptive period")
        else:
            estimated_points = math.ceil(range_seconds / period_seconds)
            if estimated_points > MAX_POINTS_PER_CURVE:
                raise ValidationError(
                    f"estimated points per curve {estimated_points} exceed {MAX_POINTS_PER_CURVE}"
                )

    if operation == "DescribeDimensionValues":
        dimension_key = data.get("dimensionKey")
        if not isinstance(dimension_key, str) or not dimension_key:
            raise ValidationError("dimensionKey must be a non-empty string")
        if dimension_key not in metric["metricDimensions"]:
            raise ValidationError(
                f"dimensionKey {dimension_key!r} is not declared in metricDimensions {metric['metricDimensions']}"
            )

    return {
        "valid": True,
        "operation": operation,
        "scope": scope,
        "region": data.get("region"),
        "resourceType": resource_type,
        "metric": metric,
        "filterKeys": filter_keys,
        "estimatedPointsPerCurve": estimated_points,
        "warnings": warnings,
    }


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError(f"cannot read {label} {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} {path} is not valid JSON: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="metric request JSON")
    parser.add_argument("--operation", required=True, choices=sorted(OPERATIONS))
    parser.add_argument("--metric-catalog", required=True, type=Path, help="DescribeMetricCatalogs response JSON")
    parser.add_argument("--scope", required=True, help="exact scope used for metadata discovery")
    parser.add_argument("--resource-type", required=True, help="exact resource type used for metadata discovery")
    parser.add_argument("--catalog-path", help="exact slash-separated path for an ambiguous metric")
    args = parser.parse_args(argv)

    try:
        data = _load_json(args.request, "request")
        catalog = _load_json(args.metric_catalog, "metric catalog")
        result = validate_request(
            data,
            args.operation,
            catalog,
            args.scope,
            args.resource_type,
            args.catalog_path,
        )
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate BCE CLI JSON for BCM V3 alarm-masking mutations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ValidationError(ValueError):
    """Raised when a request violates the BCM V3 alarm-masking contract."""


OPERATIONS = {
    "CreateAlarmMasking",
    "UpdateAlarmMasking",
    "UpdateAlarmMaskingStates",
    "DeleteAlarmMaskings",
}
STATES = {"ENABLED", "DISABLED"}
PERIOD_TYPES = {"FOREVER", "FIXED", "RELATIVE"}
ROUTING_FIELDS = {"version", "action"}
FULL_FIELDS = {
    "name",
    "scope",
    "resourceType",
    "policyId",
    "instances",
    "region",
    "metricNames",
    "periodType",
    "beginTime",
    "endTime",
    "tz",
    "dailyBeginTimestamp",
    "dailyEndTimestamp",
}
REQUIRED_FULL_FIELDS = {"name", "scope", "resourceType", "instances", "region"}
DAY_MILLISECONDS = 24 * 60 * 60 * 1000
MANAGED_NAME = re.compile(r"^[A-Za-z\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]{2,149}$")


def _load_flatten_module() -> Any:
    path = Path(__file__).with_name("flatten_metric_catalog.py")
    spec = importlib.util.spec_from_file_location(
        "bcm_masking_flatten_metric_catalog", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


flatten_metric_catalog = _load_flatten_module()


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    return value


def _list(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        requirement = "a non-empty list" if nonempty else "a list"
        raise ValidationError(f"{path} must be {requirement}")
    return value


def _nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")
    return value


def _reject_unknown(data: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError(f"{path} contains unsupported fields: {unknown}")


def _parse_rfc3339(value: Any, path: str) -> datetime:
    text = _nonempty_string(value, path)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError(f"{path} must be an RFC3339 timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{path} must include a timezone")
    return parsed


def _validate_timezone(value: Any, path: str) -> str:
    text = _nonempty_string(value, path)
    try:
        ZoneInfo(text)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError(f"{path} must be a valid IANA timezone") from exc
    return text


def _validate_ids(value: Any, path: str = "ids") -> list[str]:
    ids = _list(value, path, nonempty=True)
    normalized = [_nonempty_string(item, f"{path}[{index}]") for index, item in enumerate(ids)]
    if len(normalized) != len(set(normalized)):
        raise ValidationError(f"{path} must not contain duplicates")
    return normalized


def _validate_instances(value: Any) -> tuple[int, list[str]]:
    instances = _list(value, "instances", nonempty=True)
    signatures: set[tuple[tuple[str, str], ...]] = set()
    all_keys: set[str] = set()
    for index, raw_instance in enumerate(instances):
        instance_path = f"instances[{index}]"
        instance = _object(raw_instance, instance_path)
        _reject_unknown(instance, {"dimensions"}, instance_path)
        dimensions = _list(
            instance.get("dimensions"), f"{instance_path}.dimensions", nonempty=True
        )
        seen: set[str] = set()
        signature: list[tuple[str, str]] = []
        for dimension_index, raw_dimension in enumerate(dimensions):
            dimension_path = f"{instance_path}.dimensions[{dimension_index}]"
            dimension = _object(raw_dimension, dimension_path)
            _reject_unknown(dimension, {"key", "value"}, dimension_path)
            key = _nonempty_string(dimension.get("key"), f"{dimension_path}.key")
            item_value = _nonempty_string(
                dimension.get("value"), f"{dimension_path}.value"
            )
            if key in seen:
                raise ValidationError(f"{instance_path} has duplicate dimension key {key!r}")
            seen.add(key)
            all_keys.add(key)
            signature.append((key, item_value))
        canonical = tuple(sorted(signature))
        if canonical in signatures:
            raise ValidationError("instances must not contain duplicate selectors")
        signatures.add(canonical)
    return len(instances), sorted(all_keys)


def _validate_period(data: dict[str, Any], warnings: list[str]) -> str:
    raw_period_type = data.get("periodType", "FOREVER")
    if raw_period_type in (None, ""):
        raw_period_type = "FOREVER"
        warnings.append("empty periodType is normalized to FOREVER; omit the empty field")
    period_type = _nonempty_string(raw_period_type, "periodType").upper()
    if period_type not in PERIOD_TYPES:
        raise ValidationError(f"periodType must be one of {sorted(PERIOD_TYPES)}")

    begin_value = data.get("beginTime")
    end_value = data.get("endTime")
    has_begin = begin_value not in (None, "")
    has_end = end_value not in (None, "")
    daily_begin = data.get("dailyBeginTimestamp")
    daily_end = data.get("dailyEndTimestamp")

    if has_begin != has_end:
        raise ValidationError("beginTime and endTime must be supplied together")
    if has_begin:
        begin = _parse_rfc3339(begin_value, "beginTime")
        end = _parse_rfc3339(end_value, "endTime")
        if end <= begin:
            raise ValidationError("endTime must be later than beginTime")

    if "tz" in data and data.get("tz") not in (None, ""):
        _validate_timezone(data.get("tz"), "tz")

    if period_type == "FOREVER":
        if has_begin or has_end:
            raise ValidationError("beginTime/endTime do not apply to periodType=FOREVER")
        if daily_begin not in (None, 0) or daily_end not in (None, 0):
            raise ValidationError(
                "dailyBeginTimestamp/dailyEndTimestamp do not apply to periodType=FOREVER"
            )
    elif period_type == "FIXED":
        if not has_begin or not has_end:
            raise ValidationError("beginTime and endTime are required for periodType=FIXED")
        if daily_begin not in (None, 0) or daily_end not in (None, 0):
            raise ValidationError(
                "dailyBeginTimestamp/dailyEndTimestamp do not apply to periodType=FIXED"
            )
    else:
        if "dailyBeginTimestamp" not in data or "dailyEndTimestamp" not in data:
            raise ValidationError(
                "dailyBeginTimestamp and dailyEndTimestamp are required for periodType=RELATIVE"
            )
        if type(daily_begin) is not int or type(daily_end) is not int:
            raise ValidationError(
                "dailyBeginTimestamp and dailyEndTimestamp must be integer milliseconds"
            )
        if not 0 <= daily_begin < daily_end <= DAY_MILLISECONDS:
            raise ValidationError(
                "RELATIVE daily timestamps must satisfy 0 <= begin < end <= 86400000 milliseconds"
            )
        if data.get("tz") in (None, ""):
            warnings.append("RELATIVE masking has no tz; the service default is Asia/Shanghai")

    return period_type


def _validate_full_request(
    request: dict[str, Any], operation: str, warnings: list[str]
) -> dict[str, Any]:
    allowed = set(FULL_FIELDS)
    required = set(REQUIRED_FULL_FIELDS)
    if operation == "UpdateAlarmMasking":
        allowed.update({"id", "state"})
        required.update({"id", "state"})
    _reject_unknown(request, allowed, "request")
    missing = sorted(field for field in required if field not in request)
    if missing:
        raise ValidationError(f"missing required fields for {operation}: {missing}")

    name = _nonempty_string(request.get("name"), "name")
    if not MANAGED_NAME.fullmatch(name):
        raise ValidationError(
            "name must start with a Chinese or English letter; only digits, Chinese/English letters, '_' and '-' are allowed; length must be 3-150 characters"
        )
    scope = _nonempty_string(request.get("scope"), "scope")
    resource_type = _nonempty_string(request.get("resourceType"), "resourceType")
    region = _nonempty_string(request.get("region"), "region")
    if "policyId" in request:
        _nonempty_string(request.get("policyId"), "policyId")

    instance_count, dimension_keys = _validate_instances(request.get("instances"))
    metric_names = _list(request.get("metricNames", []), "metricNames")
    if any(not isinstance(item, str) or not item.strip() for item in metric_names):
        raise ValidationError("metricNames must contain only non-empty strings")
    if len(metric_names) != len(set(metric_names)):
        raise ValidationError("metricNames must not contain duplicates")
    if not metric_names:
        warnings.append("metricNames is empty or omitted; masking applies without a metric-name filter")

    period_type = _validate_period(request, warnings)
    masking_id: str | None = None
    state: str | None = None
    if operation == "UpdateAlarmMasking":
        masking_id = _nonempty_string(request.get("id"), "id")
        state = _nonempty_string(request.get("state"), "state").upper()
        if state not in STATES:
            raise ValidationError(f"state must be one of {sorted(STATES)}")

    return {
        "id": masking_id,
        "name": name,
        "scope": scope,
        "resourceType": resource_type,
        "region": region,
        "state": state,
        "instanceCount": instance_count,
        "dimensionKeys": dimension_keys,
        "metricCount": len(metric_names),
        "periodType": period_type,
    }


def _validate_against_catalog(
    request: dict[str, Any], catalog: Any, warnings: list[str]
) -> dict[str, Any]:
    catalog_data = _object(catalog, "metric catalog")
    try:
        metrics = flatten_metric_catalog.flatten_catalog(catalog_data)
    except flatten_metric_catalog.CatalogError as exc:
        raise ValidationError(f"invalid metric catalog: {exc}") from exc
    if not metrics:
        raise ValidationError("metric catalog contains no metrics")

    requested_names = request.get("metricNames", [])
    available_names = {metric["name"] for metric in metrics}
    missing_names = sorted(set(requested_names) - available_names)
    if missing_names:
        raise ValidationError(
            f"metricNames have no exact match in the supplied metric catalog: {missing_names}"
        )
    selected = (
        [metric for metric in metrics if metric["name"] in requested_names]
        if requested_names
        else metrics
    )
    identifier_signatures = {
        tuple(sorted(metric["resourceIdentifiers"])) for metric in selected
    }
    if len(identifier_signatures) != 1:
        raise ValidationError(
            "selected metric metadata declares multiple resource-identifier sets; "
            "supply exact metricNames or a narrower metric catalog"
        )
    required_identifiers = set(next(iter(identifier_signatures)))
    allowed_keys: set[str] = set()
    for metric in selected:
        allowed_keys.update(metric["resourceIdentifiers"])
        allowed_keys.update(metric["metricDimensions"])

    for index, raw_instance in enumerate(request["instances"]):
        keys = {
            dimension["key"] for dimension in raw_instance["dimensions"]
        }
        unknown = sorted(keys - allowed_keys)
        if unknown:
            raise ValidationError(
                f"instances[{index}] contains dimensions not declared in metric metadata: {unknown}"
            )
        missing = sorted(required_identifiers - keys)
        if missing:
            raise ValidationError(
                f"instances[{index}] is missing resource identifiers: {missing}"
            )

    warnings.append(
        "metric metadata validates names and selector keys only; it does not prove that an instance currently exists"
    )
    return {
        "catalogMetricCount": len(metrics),
        "selectedMetricCount": len(selected),
        "requiredResourceIdentifiers": sorted(required_identifiers),
        "allowedDimensionKeys": sorted(allowed_keys),
    }


def validate_masking(data: Any, operation: str, catalog: Any | None = None) -> dict[str, Any]:
    """Validate one alarm-masking mutation and return a non-secret summary."""

    if operation not in OPERATIONS:
        raise ValidationError(f"unsupported operation {operation!r}")
    request = _object(data, "request")
    routing = sorted(set(request) & ROUTING_FIELDS)
    if routing:
        raise ValidationError(
            f"routing fields do not belong in request JSON: {routing}; select the BCE CLI operation and verify the V3 path with --dry-run"
        )

    warnings: list[str] = []
    if operation in {"CreateAlarmMasking", "UpdateAlarmMasking"}:
        masking = _validate_full_request(request, operation, warnings)
        if catalog is None:
            raise ValidationError(
                f"metric catalog is required for {operation}; use the exact DescribeMetricCatalogs response for the confirmed scope/resourceType"
            )
        metadata = _validate_against_catalog(request, catalog, warnings)
        if operation == "CreateAlarmMasking":
            warnings.append("CreateAlarmMasking is enabled immediately after creation")
        return {
            "valid": True,
            "operation": operation,
            "masking": masking,
            "metadata": metadata,
            "warnings": warnings,
        }

    if operation == "UpdateAlarmMaskingStates":
        _reject_unknown(request, {"ids", "state"}, "request")
        ids = _validate_ids(request.get("ids"))
        state = _nonempty_string(request.get("state"), "state").upper()
        if state not in STATES:
            raise ValidationError(f"state must be one of {sorted(STATES)}")
        return {
            "valid": True,
            "operation": operation,
            "maskingIdsCount": len(ids),
            "state": state,
            "warnings": warnings,
        }

    _reject_unknown(request, {"ids"}, "request")
    ids = _validate_ids(request.get("ids"))
    return {
        "valid": True,
        "operation": operation,
        "maskingIdsCount": len(ids),
        "warnings": warnings,
    }


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON from {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="alarm-masking request JSON file")
    parser.add_argument("--operation", choices=sorted(OPERATIONS), required=True)
    parser.add_argument(
        "--metric-catalog",
        type=Path,
        help="exact DescribeMetricCatalogs response; required for create and update",
    )
    args = parser.parse_args(argv)
    try:
        catalog = _read_json(args.metric_catalog) if args.metric_catalog else None
        result = validate_masking(_read_json(args.request), args.operation, catalog)
    except ValidationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

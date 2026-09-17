#!/usr/bin/env python3
"""Validate a BCM V3 cloud-product alarm policy against metric metadata."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


class ValidationError(ValueError):
    """Raised when a policy violates the BCM V3 contract."""


OPERATIONS = {"CreateAlarmPolicy", "UpdateAlarmPolicy"}
COMMON_FIELDS = {
    "name",
    "scope",
    "resourceType",
    "target",
    "rules",
    "pendingCount",
    "onMissingData",
    "noDataNotifyPendingMinutes",
    "type",
    "level",
    "actions",
    "notifyEnabled",
    "callbacks",
    "renotifyCount",
    "renotifyIntervalMinutes",
    "notifyMergeWindowSeconds",
}
REQUIRED_COMMON_FIELDS = {
    "name",
    "scope",
    "resourceType",
    "target",
    "rules",
    "pendingCount",
    "onMissingData",
    "type",
    "level",
    "actions",
    "notifyEnabled",
}
FORBIDDEN_ROUTING_FIELDS = {"version", "action", "region"}
STATIC_OPERATORS = {">", ">=", "<", "<=", "=", "!="}
RATE_OPERATORS = {
    f"{direction}_RATE_{suffix}"
    for direction in ("INC", "DEC")
    for suffix in ("GT", "GE", "LT", "LE", "EQ", "NE")
}
OPERATORS = STATIC_OPERATORS | RATE_OPERATORS
AGGREGATIONS = {"MAX", "MIN", "SUM", "AVG"}
LEVELS = {"NOTICE", "WARNING", "CRITICAL", "MAJOR"}
MISSING_DATA_BEHAVIORS = {"IGNORE", "SHOW_OK", "SHOW_NO_DATA_AND_NOTIFY"}
TARGET_TYPES = {"ALL_INSTANCES", "INSTANCES", "TAGS", "INSTANCE_GROUPS"}
CALLBACK_MENTION_TYPES = {"NONE", "ALL", "USERS"}


def _load_flatten_module() -> Any:
    path = Path(__file__).with_name("flatten_metric_catalog.py")
    spec = importlib.util.spec_from_file_location("bcm_alarm_flatten_metric_catalog", path)
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
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{path} must be a non-empty string")
    return value


def _positive_int(value: Any, path: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValidationError(f"{path} must be a positive integer")
    return value


def _nonnegative_int(value: Any, path: str) -> int:
    if type(value) is not int or value < 0:
        raise ValidationError(f"{path} must be a non-negative integer")
    return value


def _finite_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValidationError(f"{path} must be a finite number")
    return float(value)


def _reject_unknown(data: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValidationError(f"{path} contains unsupported fields: {unknown}")


def _metric_signature(metric: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(metric["resourceIdentifiers"]),
        tuple(metric["metricDimensions"]),
        metric["period"],
        metric["periodUnit"],
        metric["unit"],
    )


def _metric_index(catalog: dict[str, Any], warnings: list[str]) -> dict[str, dict[str, Any]]:
    try:
        metrics = flatten_metric_catalog.flatten_catalog(catalog)
    except flatten_metric_catalog.CatalogError as exc:
        raise ValidationError(f"invalid metric catalog: {exc}") from exc
    grouped: dict[str, list[dict[str, Any]]] = {}
    for metric in metrics:
        grouped.setdefault(metric["name"], []).append(metric)
    index: dict[str, dict[str, Any]] = {}
    for name, matches in grouped.items():
        signatures = {_metric_signature(metric) for metric in matches}
        paths = ["/".join(metric["catalogPath"]) or "<root>" for metric in matches]
        if len(signatures) > 1:
            raise ValidationError(
                f"metricName {name!r} is ambiguous across catalog paths {paths}; "
                "use a catalog response scoped to one unambiguous resource type"
            )
        if len(matches) > 1:
            warnings.append(
                f"metricName {name!r} appears with identical metadata at {paths}; selected {paths[0]}"
            )
        index[name] = matches[0]
    return index


def _period_seconds(metric: dict[str, Any]) -> int:
    return int(metric["periodSeconds"])


def _validate_condition_dimensions(
    value: Any, metric: dict[str, Any], path: str
) -> list[str]:
    items = _list(value, path)
    allowed = set(metric["resourceIdentifiers"]) | set(metric["metricDimensions"])
    seen: set[str] = set()
    for index, raw in enumerate(items):
        item_path = f"{path}[{index}]"
        item = _object(raw, item_path)
        _reject_unknown(item, {"key", "operator", "values"}, item_path)
        key = _nonempty_string(item.get("key"), f"{item_path}.key")
        if key not in allowed:
            raise ValidationError(
                f"{item_path}.key {key!r} is not declared in resourceIdentifiers or metricDimensions"
            )
        if key in seen:
            raise ValidationError(f"duplicate condition dimension key {key!r}")
        seen.add(key)
        if item.get("operator") not in {"=", "!="}:
            raise ValidationError(f"{item_path}.operator must be '=' or '!='")
        values = _list(item.get("values"), f"{item_path}.values", nonempty=True)
        if any(not isinstance(value, str) or not value for value in values):
            raise ValidationError(f"{item_path}.values must contain only non-empty strings")
    return sorted(seen)


def _validate_rules(
    value: Any, metric_index: dict[str, dict[str, Any]], warnings: list[str]
) -> tuple[list[dict[str, Any]], set[str], set[str], list[int]]:
    groups = _list(value, "rules", nonempty=True)
    metric_summaries: list[dict[str, Any]] = []
    all_identifiers: set[str] = set()
    all_dimension_keys: set[str] = set()
    pending_counts: list[int] = []
    for group_index, raw_group in enumerate(groups):
        group_path = f"rules[{group_index}]"
        group = _object(raw_group, group_path)
        _reject_unknown(group, {"conditions", "pendingCount", "checkIntervalSeconds"}, group_path)
        pending_counts.append(_positive_int(group.get("pendingCount"), f"{group_path}.pendingCount"))
        interval = _positive_int(
            group.get("checkIntervalSeconds"), f"{group_path}.checkIntervalSeconds"
        )
        if interval < 60:
            raise ValidationError(
                f"{group_path}.checkIntervalSeconds must be at least 60; the evaluator floors cadence to 60 seconds"
            )
        conditions = _list(group.get("conditions"), f"{group_path}.conditions", nonempty=True)
        for condition_index, raw_condition in enumerate(conditions):
            condition_path = f"{group_path}.conditions[{condition_index}]"
            condition = _object(raw_condition, condition_path)
            _reject_unknown(
                condition,
                {
                    "metricName",
                    "metricDimensions",
                    "operator",
                    "threshold",
                    "aggregateType",
                    "windowSeconds",
                    "displayUnit",
                    "displayThreshold",
                },
                condition_path,
            )
            metric_name = _nonempty_string(
                condition.get("metricName"), f"{condition_path}.metricName"
            )
            metric = metric_index.get(metric_name)
            if metric is None:
                raise ValidationError(f"metricName {metric_name!r} has no exact catalog match")
            if (
                metric["period"] is not None
                and isinstance(metric["periodUnit"], str)
                and not metric["periodUnit"].strip()
            ):
                warnings.append(
                    f"{condition_path} catalog periodUnit is empty; interpreted the positive "
                    "period as seconds for BCM V3 compatibility"
                )
            operator = condition.get("operator")
            if operator not in OPERATORS:
                raise ValidationError(f"{condition_path}.operator is unsupported: {operator!r}")
            _finite_number(condition.get("threshold"), f"{condition_path}.threshold")
            if condition.get("aggregateType") not in AGGREGATIONS:
                raise ValidationError(
                    f"{condition_path}.aggregateType must be one of {sorted(AGGREGATIONS)}"
                )
            window = _positive_int(
                condition.get("windowSeconds"), f"{condition_path}.windowSeconds"
            )
            native_period = _period_seconds(metric)
            if window < native_period:
                raise ValidationError(
                    f"{condition_path}.windowSeconds {window} is below native metric period {native_period}"
                )
            if window % native_period:
                warnings.append(
                    f"{condition_path}.windowSeconds {window} is not a multiple of native period {native_period}"
                )
            display_unit = _nonempty_string(
                condition.get("displayUnit"), f"{condition_path}.displayUnit"
            )
            display_threshold = condition.get("displayThreshold")
            if not isinstance(display_threshold, str) or not display_threshold:
                raise ValidationError(f"{condition_path}.displayThreshold must be a non-empty string")
            if operator in RATE_OPERATORS:
                if display_unit != "%":
                    raise ValidationError(f"{condition_path}.displayUnit must be '%' for a rate operator")
                warnings.append(
                    f"{condition_path} is a rate condition; a previous value near zero produces no comparison"
                )
            selected_dimensions = _validate_condition_dimensions(
                condition.get("metricDimensions", []), metric, f"{condition_path}.metricDimensions"
            )
            identifiers = set(metric["resourceIdentifiers"])
            dimension_keys = identifiers | set(metric["metricDimensions"])
            all_identifiers.update(identifiers)
            all_dimension_keys.update(dimension_keys)
            metric_summaries.append(
                {
                    "name": metric_name,
                    "unit": metric["unit"],
                    "nativePeriodSeconds": native_period,
                    "resourceIdentifiers": sorted(identifiers),
                    "metricDimensions": sorted(metric["metricDimensions"]),
                    "conditionDimensions": selected_dimensions,
                }
            )
    return metric_summaries, all_identifiers, all_dimension_keys, pending_counts


def _validate_dimension_presence_lists(
    target: dict[str, Any], allowed_keys: set[str]
) -> tuple[list[str], list[str]]:
    normalized: list[list[str]] = []
    for field in ("includingDimensions", "excludingDimensions"):
        values = _list(target.get(field, []), f"target.{field}")
        if any(not isinstance(value, str) or not value for value in values):
            raise ValidationError(f"target.{field} must contain only non-empty strings")
        if len(values) != len(set(values)):
            raise ValidationError(f"target.{field} must not contain duplicates")
        unknown = sorted(set(values) - allowed_keys)
        if unknown:
            raise ValidationError(f"target.{field} contains undeclared dimensions: {unknown}")
        normalized.append(sorted(values))
    overlap = sorted(set(normalized[0]) & set(normalized[1]))
    if overlap:
        raise ValidationError(f"dimensions cannot be both included and excluded: {overlap}")
    return normalized[0], normalized[1]


def _validate_target(
    value: Any,
    required_identifiers: set[str],
    allowed_dimension_keys: set[str],
    warnings: list[str],
) -> dict[str, Any]:
    target = _object(value, "target")
    _reject_unknown(
        target,
        {
            "type",
            "instances",
            "tags",
            "instanceGroups",
            "includingDimensions",
            "excludingDimensions",
            "region",
        },
        "target",
    )
    target_type = target.get("type")
    if target_type not in TARGET_TYPES:
        raise ValidationError(f"target.type must be one of {sorted(TARGET_TYPES)}")
    including, excluding = _validate_dimension_presence_lists(target, allowed_dimension_keys)

    def reject_nonempty(*fields: str) -> None:
        for field in fields:
            if field in target and target[field] not in (None, [], ""):
                raise ValidationError(f"target.{field} does not apply to target.type={target_type}")

    count: int | None = None
    business_region: str | None = None
    if target_type == "INSTANCES":
        reject_nonempty("tags", "instanceGroups")
        business_region = _nonempty_string(target.get("region"), "target.region")
        instances = _list(target.get("instances"), "target.instances", nonempty=True)
        count = len(instances)
        for index, raw_instance in enumerate(instances):
            instance_path = f"target.instances[{index}]"
            instance = _object(raw_instance, instance_path)
            _reject_unknown(instance, {"dimensions"}, instance_path)
            dimensions = _list(
                instance.get("dimensions"), f"{instance_path}.dimensions", nonempty=True
            )
            seen: set[str] = set()
            for dim_index, raw_dimension in enumerate(dimensions):
                dim_path = f"{instance_path}.dimensions[{dim_index}]"
                dimension = _object(raw_dimension, dim_path)
                _reject_unknown(dimension, {"key", "value"}, dim_path)
                key = _nonempty_string(dimension.get("key"), f"{dim_path}.key")
                _nonempty_string(dimension.get("value"), f"{dim_path}.value")
                if key in seen:
                    raise ValidationError(f"{instance_path} has duplicate dimension key {key!r}")
                if key not in allowed_dimension_keys:
                    raise ValidationError(f"{dim_path}.key {key!r} is not declared by selected metrics")
                seen.add(key)
            missing = sorted(required_identifiers - seen)
            if missing:
                raise ValidationError(f"{instance_path} is missing resource identifiers: {missing}")
    elif target_type == "TAGS":
        reject_nonempty("instances", "instanceGroups", "region")
        tags = _list(target.get("tags"), "target.tags", nonempty=True)
        count = len(tags)
        for index, raw_tag in enumerate(tags):
            tag_path = f"target.tags[{index}]"
            tag = _object(raw_tag, tag_path)
            _reject_unknown(tag, {"key", "value"}, tag_path)
            _nonempty_string(tag.get("key"), f"{tag_path}.key")
            if not isinstance(tag.get("value"), str):
                raise ValidationError(f"{tag_path}.value must be a string; empty means any value")
        if len(tags) > 1:
            warnings.append("multiple target.tags are OR alternatives, not an AND expression")
    elif target_type == "INSTANCE_GROUPS":
        reject_nonempty("instances", "tags", "region")
        groups = _list(target.get("instanceGroups"), "target.instanceGroups", nonempty=True)
        if any(not isinstance(group, str) or not group for group in groups):
            raise ValidationError("target.instanceGroups must contain only non-empty IDs")
        if len(groups) != len(set(groups)):
            raise ValidationError("target.instanceGroups must not contain duplicates")
        count = len(groups)
        if len(groups) > 1:
            warnings.append("multiple target.instanceGroups are OR alternatives")
    else:
        reject_nonempty("instances", "tags", "instanceGroups", "region")

    return {
        "type": target_type,
        "selectorCount": count,
        "businessRegion": business_region,
        "includingDimensions": including,
        "excludingDimensions": excluding,
    }


def _validate_actions_and_callbacks(data: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    actions = _list(data.get("actions"), "actions")
    for index, raw_action in enumerate(actions):
        path = f"actions[{index}]"
        action = _object(raw_action, path)
        _reject_unknown(action, {"notifyId"}, path)
        _nonempty_string(action.get("notifyId"), f"{path}.notifyId")

    callbacks = _list(data.get("callbacks", []), "callbacks")
    for index, raw_callback in enumerate(callbacks):
        path = f"callbacks[{index}]"
        callback = _object(raw_callback, path)
        _reject_unknown(callback, {"url", "mention"}, path)
        url = _nonempty_string(callback.get("url"), f"{path}.url")
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValidationError(f"{path}.url must be an absolute HTTP(S) URL")
        if parsed.username or parsed.password or parsed.query:
            warnings.append(f"{path}.url contains credentials or query data; do not persist or print it")
        raw_mention = callback.get("mention")
        if raw_mention is None:
            continue
        mention = _object(raw_mention, f"{path}.mention")
        _reject_unknown(mention, {"type", "userIds"}, f"{path}.mention")
        mention_type = mention.get("type")
        if mention_type not in CALLBACK_MENTION_TYPES:
            raise ValidationError(
                f"{path}.mention.type must be one of {sorted(CALLBACK_MENTION_TYPES)}"
            )
        users = _list(mention.get("userIds", []), f"{path}.mention.userIds")
        if any(not isinstance(user, str) or not user for user in users):
            raise ValidationError(f"{path}.mention.userIds must contain only non-empty strings")
        if mention_type == "USERS" and not users:
            raise ValidationError(f"{path}.mention.userIds is required when mention.type=USERS")
        if mention_type != "USERS" and users:
            raise ValidationError(f"{path}.mention.userIds only applies when mention.type=USERS")

    notify_enabled = data.get("notifyEnabled")
    if type(notify_enabled) is not bool:
        raise ValidationError("notifyEnabled must be a boolean")
    if notify_enabled and not actions and not callbacks:
        raise ValidationError("notifyEnabled=true requires at least one action or callback")
    if not notify_enabled:
        warnings.append(
            "notifyEnabled=false suppresses delivery but does not suppress history after dispatcher admission"
        )
    return {"notifyEnabled": notify_enabled, "actionCount": len(actions), "callbackCount": len(callbacks)}


def validate_policy(data: Any, operation: str, catalog: Any) -> dict[str, Any]:
    """Validate policy JSON and return a non-secret summary."""

    if operation not in OPERATIONS:
        raise ValidationError(f"unsupported operation {operation!r}")
    policy = _object(data, "policy")
    catalog_data = _object(catalog, "metric catalog")
    routing_fields = sorted(set(policy) & FORBIDDEN_ROUTING_FIELDS)
    if routing_fields:
        if "region" in routing_fields:
            raise ValidationError(
                "policy has no top-level region: use global --region for endpoint routing and target.region only for exact-instance business region"
            )
        raise ValidationError(f"routing fields do not belong in policy JSON: {routing_fields}")

    allowed = set(COMMON_FIELDS)
    required = set(REQUIRED_COMMON_FIELDS)
    if operation == "UpdateAlarmPolicy":
        allowed.update({"id", "state"})
        required.update({"id", "state"})
    else:
        if "id" in policy or "state" in policy:
            raise ValidationError("CreateAlarmPolicy does not accept id or state; a new policy is enabled immediately")
    _reject_unknown(policy, allowed, "policy")
    missing = sorted(field for field in required if field not in policy)
    if missing:
        raise ValidationError(f"missing required fields for {operation}: {missing}")

    if operation == "UpdateAlarmPolicy":
        _nonempty_string(policy.get("id"), "id")
        if policy.get("state") not in {"ENABLED", "DISABLED"}:
            raise ValidationError("state must be ENABLED or DISABLED")
    _nonempty_string(policy.get("name"), "name")
    _nonempty_string(policy.get("scope"), "scope")
    _nonempty_string(policy.get("resourceType"), "resourceType")
    if policy.get("type") != "CLOUD":
        raise ValidationError("type must be CLOUD for this BCM cloud-product skill")
    if policy.get("level") not in LEVELS:
        raise ValidationError(f"level must be one of {sorted(LEVELS)}")

    warnings: list[str] = []
    metric_index = _metric_index(catalog_data, warnings)
    metric_summaries, identifiers, dimension_keys, group_pending = _validate_rules(
        policy.get("rules"), metric_index, warnings
    )
    target_summary = _validate_target(
        policy.get("target"), identifiers, dimension_keys, warnings
    )

    top_pending = _positive_int(policy.get("pendingCount"), "pendingCount")
    warnings.append(
        "top-level pendingCount is compatibility data; the evaluator uses rules[].pendingCount"
    )
    if top_pending != group_pending[0]:
        warnings.append("top-level pendingCount differs from the first rule group's pendingCount")
    if len(set(group_pending)) > 1:
        warnings.append("OR rule groups use different consecutive-trigger counts")

    on_missing = policy.get("onMissingData")
    if on_missing not in MISSING_DATA_BEHAVIORS:
        raise ValidationError(f"onMissingData must be one of {sorted(MISSING_DATA_BEHAVIORS)}")
    no_data_minutes = policy.get("noDataNotifyPendingMinutes")
    if on_missing != "IGNORE":
        _positive_int(no_data_minutes, "noDataNotifyPendingMinutes")
    elif no_data_minutes is not None:
        _nonnegative_int(no_data_minutes, "noDataNotifyPendingMinutes")
        if no_data_minutes:
            warnings.append(
                "noDataNotifyPendingMinutes is non-zero although onMissingData does not notify on no data"
            )

    notification_summary = _validate_actions_and_callbacks(policy, warnings)
    renotify_count = _nonnegative_int(policy.get("renotifyCount", 0), "renotifyCount")
    renotify_interval = _nonnegative_int(
        policy.get("renotifyIntervalMinutes", 0), "renotifyIntervalMinutes"
    )
    if renotify_count and not renotify_interval:
        raise ValidationError("renotifyIntervalMinutes must be positive when renotifyCount > 0")
    _nonnegative_int(
        policy.get("notifyMergeWindowSeconds", 0), "notifyMergeWindowSeconds"
    )

    if operation == "CreateAlarmPolicy":
        warnings.append("CreateAlarmPolicy takes effect immediately; there is no create-time state field")
    return {
        "valid": True,
        "operation": operation,
        "policy": {
            "id": policy.get("id"),
            "name": policy["name"],
            "scope": policy["scope"],
            "resourceType": policy["resourceType"],
            "level": policy["level"],
            "onMissingData": on_missing,
            "ruleGroupCount": len(group_pending),
            "ruleGroupPendingCounts": group_pending,
            "topLevelPendingCount": top_pending,
        },
        "target": target_summary,
        "notifications": notification_summary,
        "metrics": metric_summaries,
        "warnings": warnings,
    }


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON from {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", type=Path, help="alarm-policy JSON file")
    parser.add_argument("--operation", choices=sorted(OPERATIONS), required=True)
    parser.add_argument("--metric-catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_policy(
            _read_json(args.policy), args.operation, _read_json(args.metric_catalog)
        )
    except ValidationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

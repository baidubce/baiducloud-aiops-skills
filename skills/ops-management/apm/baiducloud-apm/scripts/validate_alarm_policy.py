#!/usr/bin/env python3
"""Validate a BCE APM/LLM create or update alarm-policy JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    pass


def _entry(statistics: set[str], unit: str) -> tuple[set[str], str]:
    return statistics, unit


COUNT = {"count_per_second", "sum"}
LATENCY = {"avg", "sum", "max", "min", "p90", "p95", "p99"}
SERVICE_BASE = {
    "apm_requests": _entry(COUNT, "count"),
    "apm_requests_per_second": _entry({"avg"}, "rate"),
    "apm_error_requests": _entry(COUNT, "count"),
    "apm_error_rate": _entry({"avg"}, "percent"),
    "apm_requests_seconds": _entry(LATENCY, "seconds"),
    "apm_slow_requests": _entry(COUNT, "count"),
}
HTTP = {
    name: _entry(COUNT, "count")
    for name in {
        "apm_4xx_requests", "apm_400_requests", "apm_401_requests", "apm_403_requests",
        "apm_404_requests", "apm_5xx_requests", "apm_500_requests", "apm_501_requests",
        "apm_503_requests",
    }
}
DB = {
    "apm_db_requests": _entry(COUNT, "count"),
    "apm_db_requests_per_second": _entry({"avg"}, "rate"),
    "apm_db_error_requests": _entry(COUNT, "count"),
    "apm_db_error_rate": _entry({"avg"}, "percent"),
    "apm_db_requests_seconds": _entry(LATENCY, "seconds"),
    "apm_db_slow_requests": _entry(COUNT, "count"),
}
JVM = {
    "jvm_young_gc_count": _entry(COUNT, "count"),
    "jvm_full_gc_count": _entry(COUNT, "count"),
    "jvm_young_gc_time": _entry({"avg", "sum", "max", "min"}, "seconds"),
    "jvm_full_gc_time": _entry({"avg", "sum", "max", "min"}, "seconds"),
    "jvm_cpu_usage": _entry({"avg"}, "percent"),
    "jvm_cpu_count": _entry({"avg"}, "count"),
    "jvm_cpu_time": _entry({"sum"}, "seconds"),
    "jvm_heap_limit": _entry({"avg", "sum"}, "bytes"),
    "jvm_heap_used": _entry(COUNT, "bytes"),
    "jvm_heap_committed": _entry(COUNT, "bytes"),
    "jvm_non_heap_used": _entry(COUNT, "bytes"),
    "jvm_non_heap_limit": _entry(COUNT, "bytes"),
    "jvm_non_heap_committed": _entry(COUNT, "bytes"),
    "jvm_metaspace_used": _entry(COUNT, "bytes"),
    "jvm_compressed_class_space_used": _entry(COUNT, "bytes"),
    "jvm_code_cache_used": _entry(COUNT, "bytes"),
    "jvm_eden_space_used": _entry(COUNT, "bytes"),
    "jvm_survivor_space_used": _entry(COUNT, "bytes"),
    "jvm_old_gen_used": _entry(COUNT, "bytes"),
    "jvm_thread_count": _entry(COUNT, "count"),
    "jvm_thread_blocked": _entry(COUNT, "count"),
    "jvm_thread_runnable": _entry(COUNT, "count"),
    "jvm_thread_waiting": _entry(COUNT, "count"),
    "jvm_thread_timed_waiting": _entry(COUNT, "count"),
    "jvm_thread_terminated": _entry(COUNT, "count"),
    "jvm_class_current": _entry({"count_per_second"}, "count"),
    "jvm_class_loaded": _entry(COUNT, "count"),
    "jvm_class_unloaded": _entry(COUNT, "count"),
}
LLM = {
    "llm_requests": _entry(COUNT, "count"),
    "llm_requests_per_second": _entry({"avg"}, "rate"),
    "llm_error_requests": _entry(COUNT, "count"),
    "llm_error_rate": _entry({"avg"}, "percent"),
    "llm_requests_seconds": _entry({"avg", "max", "min", "p90", "p95", "p99"}, "seconds"),
}
LLM_OPERATION = {
    "llm_app_requests": _entry(COUNT, "count"),
    "llm_app_error_requests": _entry(COUNT, "count"),
    "llm_app_error_rate": _entry({"avg"}, "percent"),
    "llm_app_requests_seconds": _entry({"avg", "max", "min", "p90", "p95", "p99"}, "seconds"),
}
LLM_TOKEN = {
    "llm_token_usage": _entry(COUNT, "token"),
    "llm_token_usage_per_call": _entry({"avg"}, "token"),
    "llm_time_to_first_token": _entry({"avg", "max", "min"}, "seconds"),
    "llm_time_per_output_token": _entry({"avg", "max", "min"}, "seconds_per_token"),
}

SERVICE_KINDS = {"SERVER", "CLIENT", "INTERNAL_FUNCTION", "CONSUMER", "PRODUCER"}
KINDS = SERVICE_KINDS | {"DB", "EXCEPTION", "JVM", "LLM", "LLM_OPERATION", "LLM_TOKEN_ANALYSIS"}
COMPARISON_OPERATORS = {"prev_inc", "prev_dec", "hoh_inc", "hoh_dec", "dod_inc", "dod_dec"}
THRESHOLD_OPERATORS = {"gt", "gte", "lt", "lte"} | COMPARISON_OPERATORS
FILTER_OPERATORS = {"eq", "ne", "contains", "not_contain", "iterate"}
MISSING_DATA = {"SHOW_NO_DATA_AND_NOTIFY", "SHOW_NO_DATA", "SHOW_OK", "EVALUATE_AS_ZERO"}
LEVELS = {"NOTICE", "WARNING", "MAJOR", "CRITICAL"}
STATES = {"ENABLED", "DISABLED"}
BYTE_UNITS = {"Bytes", "KB", "MB", "GB", "TB"}
OPERATIONS = {"ApmCreateAlarmPolicy", "ApmUpdateAlarmPolicy"}
KIND_DIMENSIONS = {
    "SERVER": {"component", "operation", "host.name"},
    "CLIENT": {"component", "operation", "host.name"},
    "CONSUMER": {"component", "operation", "host.name"},
    "PRODUCER": {"component", "operation", "host.name"},
    "INTERNAL_FUNCTION": {"operation", "host.name"},
    "DB": {"db.system", "db.instance", "host.name"},
    "EXCEPTION": {"component", "operation", "host.name", "exception.type"},
    "JVM": {"host.name"},
    "LLM": {"attributes.gen_ai.response.model"},
    "LLM_OPERATION": {"attributes.gen_ai.kind", "attributes.gen_ai.response.model"},
    "LLM_TOKEN_ANALYSIS": {"attributes.gen_ai.response.model"},
}


def catalog_for(kind: str) -> dict[str, tuple[set[str], str]]:
    if kind in SERVICE_KINDS:
        catalog = dict(SERVICE_BASE)
        if kind == "SERVER":
            catalog.update(HTTP)
        return catalog
    if kind == "DB":
        return DB
    if kind == "EXCEPTION":
        return {"apm_exceptions_requests": _entry(COUNT, "count")}
    if kind == "JVM":
        return JVM
    if kind == "LLM":
        return LLM
    if kind == "LLM_OPERATION":
        return LLM_OPERATION
    if kind == "LLM_TOKEN_ANALYSIS":
        return LLM_TOKEN
    raise ValidationError(f"unsupported metricKind {kind!r}")


def _positive_int(value: Any, field: str, *, allow_zero: bool = False) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{field} must be an integer")
    minimum = 0 if allow_zero else 1
    if value < minimum:
        raise ValidationError(f"{field} must be >= {minimum}")
    return value


def _validate_unit(unit_type: str, display_unit: Any, operator: str, path: str) -> None:
    if not isinstance(display_unit, str):
        raise ValidationError(f"{path}.displayUnit must be a string")
    if operator in COMPARISON_OPERATORS:
        if display_unit != "%":
            raise ValidationError(f"{path}.displayUnit must be '%' for a comparison threshold")
        return
    if unit_type == "percent" and display_unit != "%":
        raise ValidationError(f"{path}.displayUnit must be '%' for a percentage metric")
    if unit_type == "seconds" and display_unit != "s":
        raise ValidationError(f"{path}.displayUnit must be 's' for a latency metric")
    if unit_type == "seconds_per_token" and display_unit not in {"s/token", "s"}:
        raise ValidationError(f"{path}.displayUnit must be 's/token' (or legacy 's')")
    if unit_type == "bytes" and display_unit not in BYTE_UNITS:
        raise ValidationError(f"{path}.displayUnit must be one of {sorted(BYTE_UNITS)}")


def _validate_leaf(leaf: Any, path: str, catalog: dict[str, tuple[set[str], str]]) -> str:
    if not isinstance(leaf, dict):
        raise ValidationError(f"{path} must be an object")
    if leaf.get("rules"):
        raise ValidationError(f"{path} must be a leaf and cannot contain nested rules")
    metric = leaf.get("metric")
    if metric not in catalog:
        raise ValidationError(f"{path}.metric {metric!r} is invalid for the selected metricKind")
    statistic = leaf.get("aggregate")
    allowed_statistics, unit_type = catalog[metric]
    if statistic not in allowed_statistics:
        raise ValidationError(f"{path}.aggregate {statistic!r} is invalid for {metric}; allowed: {sorted(allowed_statistics)}")
    window = leaf.get("windowInSeconds")
    if not isinstance(window, int) or isinstance(window, bool) or window < 60:
        raise ValidationError(f"{path}.windowInSeconds must be an integer >= 60")
    operator = leaf.get("operator")
    if operator not in THRESHOLD_OPERATORS:
        raise ValidationError(f"{path}.operator is not an allowed threshold operator")
    value = leaf.get("displayValue")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{path}.displayValue must be numeric")
    _validate_unit(unit_type, leaf.get("displayUnit"), operator, path)
    return metric


def _validate_rule(rule: Any, catalog: dict[str, tuple[set[str], str]]) -> list[str]:
    if not isinstance(rule, dict):
        raise ValidationError("rule must be an object")
    operator = rule.get("operator")
    children = rule.get("rules")
    if operator not in {"and", "or"} or not isinstance(children, list) or not children:
        raise ValidationError("rule must be a non-empty top-level 'and' or 'or' group")
    metrics: list[str] = []
    if operator == "and":
        for index, child in enumerate(children):
            if isinstance(child, dict) and child.get("operator") in {"and", "or"}:
                raise ValidationError("an 'and' root must contain leaves directly")
            metrics.append(_validate_leaf(child, f"rule.rules[{index}]", catalog))
        return metrics
    for group_index, group in enumerate(children):
        group_path = f"rule.rules[{group_index}]"
        if not isinstance(group, dict) or group.get("operator") != "and":
            raise ValidationError(f"{group_path} must be an 'and' group")
        leaves = group.get("rules")
        if not isinstance(leaves, list) or not leaves:
            raise ValidationError(f"{group_path}.rules must be non-empty")
        for leaf_index, leaf in enumerate(leaves):
            metrics.append(_validate_leaf(leaf, f"{group_path}.rules[{leaf_index}]", catalog))
    return metrics


def validate_policy(data: Any, operation: str = "ApmCreateAlarmPolicy") -> tuple[list[str], list[str]]:
    if not isinstance(data, dict):
        raise ValidationError("policy must be a JSON object")
    if operation not in OPERATIONS:
        raise ValidationError(f"operation must be one of {sorted(OPERATIONS)}")
    warnings: list[str] = []
    if data.get("version") not in (None, "", "1", 1):
        raise ValidationError("alarm API version must be 1 when present")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ValidationError("name must be non-empty")
    if operation == "ApmCreateAlarmPolicy":
        if data.get("state") not in STATES:
            raise ValidationError(f"state is required for create and must be one of {sorted(STATES)}")
        if "id" in data:
            raise ValidationError("id must not be sent to ApmCreateAlarmPolicy")
        if data["state"] == "ENABLED":
            warnings.append("policy will be enabled after creation")
    else:
        if not isinstance(data.get("id"), str) or not data["id"].strip():
            raise ValidationError("id is required for ApmUpdateAlarmPolicy")
        if "state" in data:
            raise ValidationError("state must not be sent to ApmUpdateAlarmPolicy; use ApmUpdateAlarmPolicyState")

    kind = data.get("metricKind")
    if kind not in KINDS:
        raise ValidationError(f"metricKind must be one of {sorted(KINDS)}")
    catalog = catalog_for(kind)
    metrics = _validate_rule(data.get("rule"), catalog)
    if kind == "LLM_OPERATION":
        warnings.append("LLM_OPERATION has no authoritative query-equivalent mapping for baseline validation")

    target = data.get("target")
    if not isinstance(target, dict):
        raise ValidationError("target must be an object")
    target_type = target.get("type")
    if target_type not in {"ALL_SERVICES", "SERVICES", "SERVICE_TAGS"}:
        raise ValidationError("target.type must be ALL_SERVICES, SERVICES, or SERVICE_TAGS")
    if target_type == "SERVICES" and (not isinstance(target.get("services"), list) or not target["services"]):
        raise ValidationError("target.services must be non-empty for SERVICES")
    if target_type == "SERVICE_TAGS" and (not isinstance(target.get("tags"), list) or not target["tags"]):
        raise ValidationError("target.tags must be non-empty for SERVICE_TAGS")

    filters = data.get("filters", [])
    if not isinstance(filters, list):
        raise ValidationError("filters must be a list")
    seen_filter_keys: set[str] = set()
    allowed_dimensions = KIND_DIMENSIONS[kind]
    for index, item in enumerate(filters):
        path = f"filters[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{path} must be an object")
        key, operator, values = item.get("key"), item.get("operator"), item.get("values")
        if not isinstance(key, str) or not key:
            raise ValidationError(f"{path}.key must be non-empty")
        if key in {"service", "service.name"}:
            raise ValidationError(f"{path}: service scope belongs in target, not filters")
        if key not in allowed_dimensions:
            raise ValidationError(
                f"{path}.key {key!r} is invalid for metricKind {kind}; "
                f"allowed: {sorted(allowed_dimensions)}"
            )
        if key in seen_filter_keys:
            raise ValidationError(f"{path}.key {key!r} is duplicated")
        seen_filter_keys.add(key)
        if operator == "aggregate":
            raise ValidationError(f"{path}: aggregate means omit the filter and must not be sent")
        if operator not in FILTER_OPERATORS:
            raise ValidationError(f"{path}.operator must be one of {sorted(FILTER_OPERATORS)}")
        if operator in {"contains", "not_contain"} and key != "operation":
            raise ValidationError(f"{path}.operator {operator!r} is supported only for operation")
        if not isinstance(values, list) or not values:
            raise ValidationError(f"{path}.values must be a non-empty list")
        if operator == "iterate" and values != ["*"]:
            raise ValidationError(f"{path}: iterate requires values=['*']")

    _positive_int(data.get("pendingCount"), "pendingCount")
    interval = _positive_int(data.get("renotifyIntervalInMinutes", 0), "renotifyIntervalInMinutes", allow_zero=True)
    count = _positive_int(data.get("renotifyCount", 0), "renotifyCount", allow_zero=True)
    if interval == 0 and count != 0:
        raise ValidationError("renotifyCount must be 0 when renotifyIntervalInMinutes is 0")
    if interval > 0 and count < 1:
        raise ValidationError("renotifyCount must be >= 1 when re-notification is enabled")
    if not isinstance(data.get("notifyRecovery"), bool):
        raise ValidationError("notifyRecovery must be boolean")

    missing = data.get("onMissingData")
    if missing not in MISSING_DATA:
        raise ValidationError(f"onMissingData must be one of {sorted(MISSING_DATA)}")
    if missing == "SHOW_NO_DATA_AND_NOTIFY":
        _positive_int(
            data.get("noDataNotifyPendingIntervalInMinutes"),
            "noDataNotifyPendingIntervalInMinutes",
            allow_zero=True,
        )
    if missing == "EVALUATE_AS_ZERO":
        warnings.append("EVALUATE_AS_ZERO can hide collection failures or create low-threshold alarms")
    if data.get("level") not in LEVELS:
        raise ValidationError(f"level must be one of {sorted(LEVELS)}")

    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValidationError("actions must contain at least one confirmed notification template")
    for index, action in enumerate(actions):
        if not isinstance(action, dict) or not isinstance(action.get("notifyId"), str) or not action["notifyId"]:
            raise ValidationError(f"actions[{index}].notifyId must be non-empty")

    return metrics, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", type=Path)
    parser.add_argument("--operation", required=True, choices=sorted(OPERATIONS))
    args = parser.parse_args()
    try:
        data = json.loads(args.policy.read_text(encoding="utf-8"))
        metrics, warnings = validate_policy(data, args.operation)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"valid": True, "operation": args.operation, "metricKind": data["metricKind"], "metrics": metrics, "warnings": warnings}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate BCE LLM metric request JSON without calling the cloud API."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    pass


KNOWN_METRICS = {
    "llm_service_count", "llm_model_count", "llm_span_count", "llm_trace_count", "llm_user_count",
    "llm_session_count", "llm_requests_seconds_count", "llm_requests_count_per_second",
    "llm_error_requests_count", "llm_error_requests_rate", "llm_requests_seconds_avg",
    "llm_requests_seconds_p50", "llm_requests_seconds_p90", "llm_requests_seconds_p95",
    "llm_requests_seconds_p99", "llm_requests_seconds_min", "llm_requests_seconds_max",
    "llm_requests_seconds_sum", "llm_token_usage_sum", "llm_token_usage_count",
    "llm_token_usage_max", "llm_token_usage_min", "llm_avg_token_count_per_llm_call",
    "llm_avg_token_count_per_request", "llm_avg_input_token_count_per_request",
    "llm_avg_output_token_count_per_request", "llm_token_usage_per_second",
    "llm_time_to_first_token_avg", "llm_time_to_first_token_p50", "llm_time_to_first_token_p90",
    "llm_time_to_first_token_p95", "llm_time_to_first_token_p99", "llm_time_to_first_token_min",
    "llm_time_to_first_token_max", "llm_time_per_output_token_avg", "llm_time_per_output_token_min",
    "llm_time_per_output_token_max", "llm_output_token_per_second_avg", "llm_avg_llm_call_per_request",
    "llm_trace_per_user", "llm_session_per_user", "llm_span_per_user", "llm_call_per_user",
    "llm_token_per_user", "llm_input_token_per_user", "llm_output_token_per_user",
    "llm_duration_per_user", "llm_session_trace_count", "llm_session_token_count",
    "llm_requests_seconds_bucket", "llm_token_usage_bucket", "llm_time_to_first_token_sum",
    "llm_time_to_first_token_count", "llm_time_to_first_token_bucket", "llm_time_per_output_token_sum",
    "llm_time_per_output_token_count", "llm_time_per_output_token_bucket",
    "llm_output_token_per_second_sum", "llm_output_token_per_second_count",
    "llm_eval_categorical_count", "llm_eval_score_sum", "llm_eval_score_count", "llm_eval_score_avg",
}
LEGACY_OR_UNSUPPORTED = {
    "llm_requests_count", "llm_requests_per_second", "llm_error_rate", "llm_tokens_per_minute",
    "llm_max_token_count_per_llm_call", "llm_min_token_count_per_llm_call",
}
ROUTE_SENSITIVE = {
    "llm_trace_count", "llm_user_count", "llm_session_count", "llm_session_trace_count",
    "llm_session_token_count", "llm_avg_token_count_per_request",
    "llm_avg_input_token_count_per_request", "llm_avg_output_token_count_per_request",
    "llm_avg_llm_call_per_request", "llm_trace_per_user", "llm_session_per_user",
    "llm_span_per_user", "llm_call_per_user", "llm_token_per_user", "llm_input_token_per_user",
    "llm_output_token_per_user", "llm_duration_per_user",
}
PUBLIC_FIELDS = {
    "service", "host", "kind", "attributes.gen_ai.kind", "attributes.gen_ai.response.model",
    "token.type", "attributes.apm.operation", "attributes.apm.component", "attributes.user.id",
    "attributes.session.id", "exception.type",
}
INTERNAL_FIELDS = {"service.name", "host.name", "span.kind", "gen_ai.kind", "model", "component", "operation"}
STABLE_OPERATORS = {"=", "!=", "in"}


def _strict_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a strict UTC string")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValidationError(f"{field} must match YYYY-MM-DDTHH:mm:ssZ") from exc


def _validate_filters(filters: Any, path: str, warnings: list[str]) -> None:
    if filters is None:
        return
    if not isinstance(filters, list):
        raise ValidationError(f"{path} must be a list")
    for index, item in enumerate(filters):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{item_path} must be an object")
        key, op = item.get("key"), item.get("op")
        if not isinstance(key, str) or not key:
            raise ValidationError(f"{item_path}.key must be non-empty")
        if key in INTERNAL_FIELDS:
            raise ValidationError(f"{item_path}.key {key!r} is an internal Prom label; use the public LLM field")
        if key not in PUBLIC_FIELDS:
            warnings.append(f"{item_path}.key {key!r} is not in the common public-field catalog")
        if not isinstance(op, str) or not op:
            raise ValidationError(f"{item_path}.op must be non-empty")
        if op not in STABLE_OPERATORS:
            warnings.append(f"{item_path}.op {op!r} is route-dependent")
        if op == "in":
            if not isinstance(item.get("values"), list) or not item["values"]:
                raise ValidationError(f"{item_path}.values must be a non-empty list for 'in'")
        elif "value" not in item or item.get("value") in (None, ""):
            raise ValidationError(f"{item_path}.value must be present for {op!r}")


def validate_request(data: Any, allowed_metrics: set[str] | None = None) -> list[str]:
    if not isinstance(data, dict):
        raise ValidationError("request must be a JSON object")
    warnings: list[str] = []
    allowed_metrics = allowed_metrics or set()

    begin = _strict_utc(data.get("beginDatetime"), "beginDatetime")
    end = _strict_utc(data.get("endDatetime"), "endDatetime")
    if begin >= end:
        raise ValidationError("beginDatetime must be earlier than endDatetime")
    if data.get("version") not in (None, "", "1", 1):
        raise ValidationError("LLM request version must be 1 when present")

    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ValidationError("metrics must be a non-empty list")
    names: list[str] = []
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            raise ValidationError(f"metrics[{index}] must be an object")
        name = metric.get("name")
        if not isinstance(name, str) or not name:
            raise ValidationError(f"metrics[{index}].name must be non-empty")
        if name in LEGACY_OR_UNSUPPORTED:
            raise ValidationError(f"{name} is a legacy or unsupported query name")
        if "_by_srv_" in name:
            raise ValidationError(f"{name} is pre-aggregated and must not be requested directly")
        if name not in KNOWN_METRICS and name not in allowed_metrics:
            raise ValidationError(f"unknown metric {name!r}; pass --allow-metric only for a trusted dynamic evaluation name")
        if metric.get("filters"):
            raise ValidationError(f"metrics[{index}].filters must be empty; use top-level filters")
        names.append(name)

    _validate_filters(data.get("filters"), "filters", warnings)
    group_by = data.get("groupBy", [])
    if not isinstance(group_by, list) or any(not isinstance(item, str) or not item for item in group_by):
        raise ValidationError("groupBy must be a list of non-empty strings")
    for field in group_by:
        if field in INTERNAL_FIELDS:
            raise ValidationError(f"groupBy field {field!r} is internal; use the public LLM field")
        if field not in PUBLIC_FIELDS:
            warnings.append(f"groupBy field {field!r} is not in the common public-field catalog")

    if len(names) > 1 and any(name in ROUTE_SENSITIVE for name in names):
        raise ValidationError("route-sensitive user/session/Trace metrics must be split from multi-metric requests")

    period = data.get("periodSeconds", 0)
    if not isinstance(period, int) or isinstance(period, bool) or period < 0:
        raise ValidationError("periodSeconds must be a non-negative integer")
    limit = data.get("limit")
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 0 or limit > 1000):
        raise ValidationError("limit must be an integer from 0 to 1000")
    if group_by and (limit is None or limit == 0):
        warnings.append("grouped query has no positive explicit TopN limit")
    order_by = data.get("orderBy")
    if order_by not in (None, "") and order_by not in names:
        raise ValidationError("orderBy must name a metric in the same request")
    if data.get("order") not in (None, "", "asc", "desc"):
        raise ValidationError("order must be asc or desc")

    aggregate = data.get("aggregate", [])
    if aggregate:
        if not isinstance(aggregate, list) or any(item not in {"sum", "sumPerSecond"} for item in aggregate):
            raise ValidationError("aggregate values must be sum or sumPerSecond")
        if len(names) != 1:
            raise ValidationError("aggregate requests must contain exactly one metric")

    if "llm_session_count" in names:
        compare_to = metrics[names.index("llm_session_count")].get("compareTo", [])
        if compare_to and (period != 0 or group_by):
            raise ValidationError("llm_session_count compareTo requires periodSeconds=0 and no explicit groupBy")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--allow-metric", action="append", default=[], help="trusted dynamic evaluation metric name")
    args = parser.parse_args()
    try:
        data = json.loads(args.request.read_text(encoding="utf-8"))
        warnings = validate_request(data, set(args.allow_metric))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"valid": True, "operation": "DescribeLLMMetricData", "warnings": warnings}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

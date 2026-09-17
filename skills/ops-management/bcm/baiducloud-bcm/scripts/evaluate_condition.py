#!/usr/bin/env python3
"""Reproduce one BCM alarm comparison without aggregating raw samples."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


class EvaluationError(ValueError):
    """Raised for malformed comparison input."""


STATIC_OPERATORS = {">", ">=", "<", "<=", "=", "!="}
RATE_OPERATORS = {
    f"{direction}_RATE_{suffix}"
    for direction in ("INC", "DEC")
    for suffix in ("GT", "GE", "LT", "LE", "EQ", "NE")
}
OPERATORS = STATIC_OPERATORS | RATE_OPERATORS
EPSILON = 1e-6


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise EvaluationError(f"{field} must be a finite number")
    return float(value)


def _compare(value: float, threshold: float, token: str) -> bool:
    if token in {"=", "EQ"}:
        return abs(value - threshold) < EPSILON
    if token in {"!=", "NE"}:
        return abs(value - threshold) >= EPSILON
    if token in {">", "GT"}:
        return value > threshold
    if token in {">=", "GE"}:
        return value >= threshold
    if token in {"<", "LT"}:
        return value < threshold
    if token in {"<=", "LE"}:
        return value <= threshold
    raise EvaluationError(f"unsupported comparison token {token!r}")


def evaluate_condition(data: Any) -> dict[str, Any]:
    """Evaluate a pre-aggregated current value, and optionally a previous value."""

    if not isinstance(data, dict):
        raise EvaluationError("input must be a JSON object")
    unknown = sorted(set(data) - {"operator", "threshold", "current", "previous"})
    if unknown:
        raise EvaluationError(f"input contains unsupported fields: {unknown}")
    operator = data.get("operator")
    if operator not in OPERATORS:
        raise EvaluationError(f"operator is unsupported: {operator!r}")
    threshold = _finite_number(data.get("threshold"), "threshold")
    current = _finite_number(data.get("current"), "current")
    result: dict[str, Any] = {
        "operator": operator,
        "threshold": threshold,
        "current": current,
    }
    if operator in STATIC_OPERATORS:
        result.update(
            {
                "comparable": True,
                "comparisonValue": current,
                "comparisonUnit": "metric unit",
                "alert": _compare(current, threshold, operator),
            }
        )
        return result

    previous = _finite_number(data.get("previous"), "previous")
    result["previous"] = previous
    if abs(previous) < EPSILON:
        result.update(
            {
                "comparable": False,
                "reason": "previous value is effectively zero; the BCM evaluator produces no rate comparison",
            }
        )
        return result
    rate = 100.0 * (current - previous) / abs(previous)
    if operator.startswith("DEC_RATE_"):
        rate = -rate
    token = operator.rsplit("_", 1)[1]
    result.update(
        {
            "comparable": True,
            "comparisonValue": rate,
            "comparisonUnit": "%",
            "alert": _compare(rate, threshold, token),
        }
    )
    return result


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON from {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition", type=Path, help="comparison JSON file")
    args = parser.parse_args()
    try:
        result = evaluate_condition(_read_json(args.condition))
    except EvaluationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

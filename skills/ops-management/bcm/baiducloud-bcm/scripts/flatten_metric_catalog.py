#!/usr/bin/env python3
"""Flatten a BCM V3 DescribeMetricCatalogs response without network access."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator


class CatalogError(ValueError):
    """Raised when metric catalog JSON does not match the documented shape."""


PERIOD_UNIT_SECONDS = {
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "m": 60.0,
    "min": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "h": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
}


def _optional_list(value: Any, path: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise CatalogError(f"{path} must be a list or null")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    items = _optional_list(value, path)
    if any(not isinstance(item, str) or not item for item in items):
        raise CatalogError(f"{path} must contain only non-empty strings")
    if len(items) != len(set(items)):
        raise CatalogError(f"{path} must not contain duplicate names")
    return items


def _period_seconds(period: Any, unit: Any, path: str) -> int | float | None:
    if period is not None and (
        isinstance(period, bool) or not isinstance(period, (int, float)) or period <= 0
    ):
        raise CatalogError(f"{path}.period must be a positive number or null")
    if unit is not None and not isinstance(unit, str):
        raise CatalogError(f"{path}.periodUnit must be a string or null")
    if period is None or unit is None:
        return None
    normalized_unit = unit.strip().lower()
    # BCM V3 currently returns an empty periodUnit for some second-based
    # metrics. Preserve the raw field in output, but normalize the positive
    # period to seconds so request validation can still enforce its lower
    # bound. Unknown non-empty units remain unresolved.
    multiplier = 1.0 if normalized_unit == "" else PERIOD_UNIT_SECONDS.get(normalized_unit)
    if multiplier is None:
        return None
    result = period * multiplier
    return int(result) if result.is_integer() else result


def iter_metrics(response: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield normalized metrics from all recursive catalog nodes."""

    if not isinstance(response, dict):
        raise CatalogError("catalog response must be a JSON object")

    def walk(catalogs: Any, names: list[str], labels: list[str], path: str) -> Iterator[dict[str, Any]]:
        for catalog_index, catalog in enumerate(_optional_list(catalogs, path)):
            catalog_path = f"{path}[{catalog_index}]"
            if not isinstance(catalog, dict):
                raise CatalogError(f"{catalog_path} must be an object")

            name = catalog.get("name", "")
            label = catalog.get("label", "")
            if not isinstance(name, str) or not isinstance(label, str):
                raise CatalogError(f"{catalog_path}.name and .label must be strings")
            next_names = names + ([name] if name else [])
            next_labels = labels + ([label] if label else [])

            for metric_index, metric in enumerate(_optional_list(catalog.get("metrics"), f"{catalog_path}.metrics")):
                metric_path = f"{catalog_path}.metrics[{metric_index}]"
                if not isinstance(metric, dict):
                    raise CatalogError(f"{metric_path} must be an object")
                metric_name = metric.get("name")
                metric_label = metric.get("label", "")
                if not isinstance(metric_name, str) or not metric_name:
                    raise CatalogError(f"{metric_path}.name must be a non-empty string")
                if not isinstance(metric_label, str):
                    raise CatalogError(f"{metric_path}.label must be a string")
                period = metric.get("period")
                period_unit = metric.get("periodUnit")
                unit = metric.get("unit")
                if unit is not None and not isinstance(unit, str):
                    raise CatalogError(f"{metric_path}.unit must be a string or null")
                yield {
                    "catalogPath": next_names,
                    "catalogLabels": next_labels,
                    "name": metric_name,
                    "label": metric_label,
                    "resourceIdentifiers": _string_list(
                        metric.get("resourceIdentifiers"), f"{metric_path}.resourceIdentifiers"
                    ),
                    "metricDimensions": _string_list(
                        metric.get("metricDimensions"), f"{metric_path}.metricDimensions"
                    ),
                    "period": period,
                    "periodUnit": period_unit,
                    "periodSeconds": _period_seconds(period, period_unit, metric_path),
                    "unit": unit,
                }

            yield from walk(catalog.get("catalogs"), next_names, next_labels, f"{catalog_path}.catalogs")

    yield from walk(response.get("catalogs"), [], [], "catalogs")


def flatten_catalog(
    response: dict[str, Any], *, name: str | None = None, label: str | None = None
) -> list[dict[str, Any]]:
    metrics = list(iter_metrics(response))
    if name is not None:
        metrics = [metric for metric in metrics if metric["name"] == name]
    if label is not None:
        metrics = [metric for metric in metrics if metric["label"] == label]
    return metrics


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"{path} is not valid JSON: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, help="DescribeMetricCatalogs response JSON")
    parser.add_argument("--name", help="exact metric name")
    parser.add_argument("--label", help="exact localized metric label")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)

    try:
        response = _load_json(args.catalog)
        metrics = flatten_catalog(response, name=args.name, label=args.label)
    except CatalogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = {"count": len(metrics), "metrics": metrics}
    if args.compact:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

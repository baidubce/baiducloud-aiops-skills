#!/usr/bin/env python3
"""Calculate a conservative finite sample plan for a BCM alarm trigger test."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any, Sequence


class PlanError(ValueError):
    pass


def positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PlanError(f"{field} must be a positive integer")
    return value


def build_plan(
    *,
    window_seconds: int,
    pending_count: int,
    check_interval_seconds: int,
    cycle_seconds: int,
) -> dict[str, int]:
    window = positive_int(window_seconds, "windowSeconds")
    pending = positive_int(pending_count, "pendingCount")
    check = positive_int(check_interval_seconds, "checkIntervalSeconds")
    cycle = positive_int(cycle_seconds, "cycleSeconds")

    effective_check = max(60, check)
    safe_duration = window + pending * effective_check
    minimum_count = math.ceil(safe_duration / cycle) + 1
    return {
        "windowSeconds": window,
        "pendingCount": pending,
        "checkIntervalSeconds": check,
        "effectiveCheckIntervalSeconds": effective_check,
        "cycleSeconds": cycle,
        "safeDurationSeconds": safe_duration,
        "minimumSampleCount": minimum_count,
        "plannedSampleSpanSeconds": (minimum_count - 1) * cycle,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Calculate a conservative BCM consecutive-window trigger sample count."
    )
    result.add_argument("--window-seconds", type=int, required=True)
    result.add_argument("--pending-count", type=int, required=True)
    result.add_argument("--check-interval-seconds", type=int, required=True)
    result.add_argument("--cycle-seconds", type=int, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        plan = build_plan(
            window_seconds=args.window_seconds,
            pending_count=args.pending_count,
            check_interval_seconds=args.check_interval_seconds,
            cycle_seconds=args.cycle_seconds,
        )
    except PlanError as exc:
        parser().error(str(exc))
    print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

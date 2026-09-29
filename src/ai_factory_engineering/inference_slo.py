from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .commissioning import GateStatus, TestOutcome
from .outcome import MetricRule


def load_inference_slo_rules(path: str | Path) -> tuple[MetricRule, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("inference SLO must declare at least one rule")
    result = []
    for item in rules:
        if not isinstance(item, dict):
            raise ValueError("inference SLO rule must be an object")
        result.append(
            MetricRule(
                metric=item["metric"],
                op=item["operator"],
                value=float(item["value"]),
            )
        )
    return tuple(result)


def evaluate_inference_slo(
    *,
    measurements: Mapping[str, float],
    rules: tuple[MetricRule, ...],
) -> TestOutcome:
    if not rules:
        return TestOutcome("inference-slo", GateStatus.ERROR, False, "missing SLO rules")
    operators = {
        "eq": lambda a, b: a == b,
        "lte": lambda a, b: a <= b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "gt": lambda a, b: a > b,
    }
    for rule in rules:
        observed = measurements.get(rule.metric)
        if not isinstance(observed, (int, float)):
            return TestOutcome(
                "inference-slo",
                GateStatus.FAIL,
                False,
                f"missing inference metric: {rule.metric}",
            )
        operator = operators.get(rule.op)
        if operator is None:
            return TestOutcome(
                "inference-slo", GateStatus.ERROR, True, f"unsupported operator: {rule.op}"
            )
        if not operator(float(observed), rule.value):
            return TestOutcome(
                "inference-slo",
                GateStatus.FAIL,
                True,
                f"{rule.metric} observed {observed} violates {rule.op} {rule.value}",
            )
    return TestOutcome("inference-slo", GateStatus.PASS, True)

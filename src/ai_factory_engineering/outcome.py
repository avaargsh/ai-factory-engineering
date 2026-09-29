from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .commissioning import GateStatus, TestOutcome


@dataclass(frozen=True)
class MetricRule:
    metric: str
    op: str
    value: float


def evaluate_evidence_outcome(
    *,
    test_id: str,
    evidence: Mapping[str, object],
    rules: tuple[MetricRule, ...],
) -> TestOutcome:
    """Turn measured evidence into a fail-closed commissioning test outcome."""
    measurements = evidence.get("measurements")
    artifacts = evidence.get("artifacts")
    if not isinstance(measurements, Mapping):
        return TestOutcome(test_id, GateStatus.ERROR, False, "missing measurements")
    if not isinstance(artifacts, list) or not artifacts:
        return TestOutcome(test_id, GateStatus.FAIL, False, "missing raw evidence artifact")

    for rule in rules:
        observed = measurements.get(rule.metric)
        if not isinstance(observed, (int, float)):
            return TestOutcome(
                test_id,
                GateStatus.FAIL,
                False,
                f"missing metric: {rule.metric}",
            )
        passed = {
            "eq": observed == rule.value,
            "lte": observed <= rule.value,
            "gte": observed >= rule.value,
            "lt": observed < rule.value,
            "gt": observed > rule.value,
        }.get(rule.op)
        if passed is None:
            return TestOutcome(
                test_id,
                GateStatus.ERROR,
                True,
                f"unsupported operator: {rule.op}",
            )
        if not passed:
            return TestOutcome(
                test_id,
                GateStatus.FAIL,
                True,
                f"{rule.metric} {rule.op} {rule.value} failed: observed {observed}",
            )

    return TestOutcome(test_id, GateStatus.PASS, True)

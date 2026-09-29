from __future__ import annotations

from .commissioning import GateStatus, TestOutcome
from .evaluator import AcceptanceResult


def acceptance_result_to_outcome(result: AcceptanceResult) -> TestOutcome:
    """Convert executable acceptance evaluation into gate input without losing failure evidence."""
    if result.passed:
        return TestOutcome(test_id=result.test_id, status=GateStatus.PASS)

    reasons: list[str] = []
    for metric in result.metrics:
        if not metric.passed:
            if metric.actual is None:
                reasons.append(f"metric {metric.name}: {metric.reason}")
            else:
                reasons.append(
                    f"metric {metric.name}: actual={metric.actual} {metric.op} threshold={metric.threshold} failed"
                )
    for evidence in result.evidence:
        if evidence.required and not evidence.present:
            reasons.append(f"missing required evidence: {evidence.source}")

    return TestOutcome(
        test_id=result.test_id,
        status=GateStatus.FAIL,
        evidence_complete=all(item.present or not item.required for item in result.evidence),
        reason="; ".join(reasons) or "acceptance evaluation failed",
    )

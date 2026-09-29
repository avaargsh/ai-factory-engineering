from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .commissioning import GateDecision, GateSpec, GateStatus, TestOutcome, evaluate_plan
from .evaluator import AcceptanceResult


class AcceptanceDisposition(str, Enum):
    ACCEPT = "ACCEPT"
    HOLD = "HOLD"
    REJECT = "REJECT"


@dataclass(frozen=True)
class CrossLayerAcceptanceDecision:
    disposition: AcceptanceDisposition
    accepted: bool
    gates: tuple[GateDecision, ...]
    reasons: tuple[str, ...]


def outcome_from_acceptance_result(
    result: AcceptanceResult,
    *,
    evidence_complete: bool = True,
) -> TestOutcome:
    reasons: list[str] = []

    for metric in result.metrics:
        if not metric.passed:
            reasons.append(f"{metric.name}: {metric.reason}")

    for evidence in result.evidence:
        if evidence.required and not evidence.present:
            reasons.append(f"missing evidence: {evidence.source}")

    return TestOutcome(
        test_id=result.test_id,
        status=GateStatus.PASS if result.passed else GateStatus.FAIL,
        evidence_complete=evidence_complete,
        reason="; ".join(reasons) or None,
    )


def decide_cross_layer_acceptance(
    gates: Iterable[GateSpec],
    outcomes: Mapping[str, Iterable[TestOutcome]],
) -> CrossLayerAcceptanceDecision:
    decisions = evaluate_plan(gates, outcomes)
    statuses = {decision.status for decision in decisions}

    reject_statuses = {
        GateStatus.FAIL,
        GateStatus.ERROR,
        GateStatus.BLOCKED,
    }

    if statuses & reject_statuses:
        disposition = AcceptanceDisposition.REJECT
    elif statuses & {GateStatus.WARN, GateStatus.PENDING}:
        disposition = AcceptanceDisposition.HOLD
    else:
        disposition = AcceptanceDisposition.ACCEPT

    reasons = tuple(
        f"{decision.gate_id}: {reason}"
        for decision in decisions
        for reason in decision.reasons
    )

    return CrossLayerAcceptanceDecision(
        disposition=disposition,
        accepted=disposition is AcceptanceDisposition.ACCEPT,
        gates=decisions,
        reasons=reasons,
    )

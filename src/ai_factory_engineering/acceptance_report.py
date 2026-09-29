from __future__ import annotations

from dataclasses import dataclass

from .acceptance_run import AcceptanceRunResult
from .commissioning import GateDecision, GateStatus


@dataclass(frozen=True)
class AcceptanceEvidenceRef:
    test_id: str
    bundle_id: str


@dataclass(frozen=True)
class AcceptanceReport:
    run_id: str
    accepted: bool
    evidence_refs: tuple[AcceptanceEvidenceRef, ...]
    gate_decisions: tuple[GateDecision, ...]


def build_acceptance_report(
    run: AcceptanceRunResult,
    decisions: tuple[GateDecision, ...],
) -> AcceptanceReport:
    evidence_refs = tuple(
        AcceptanceEvidenceRef(
            test_id=case.result.test_id,
            bundle_id=case.result.bundle_id,
        )
        for case in run.cases
    )
    gates_pass = bool(decisions) and all(
        decision.status == GateStatus.PASS
        for decision in decisions
    )
    return AcceptanceReport(
        run_id=run.run_id,
        accepted=run.passed and gates_pass,
        evidence_refs=evidence_refs,
        gate_decisions=decisions,
    )

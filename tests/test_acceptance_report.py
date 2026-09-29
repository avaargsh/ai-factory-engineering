from ai_factory_engineering.acceptance_report import build_acceptance_report
from ai_factory_engineering.acceptance_run import AcceptanceCaseResult, AcceptanceRunResult
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.evaluator import AcceptanceResult


def acceptance_run(passed: bool = True) -> AcceptanceRunResult:
    result = AcceptanceResult(
        test_id="FAB-NCCL-001",
        bundle_id="bundle-fabric-001",
        passed=passed,
        metrics=(),
        evidence=(),
    )
    return AcceptanceRunResult(
        run_id="commissioning-001",
        passed=passed,
        total=1,
        passed_count=1 if passed else 0,
        failed_count=0 if passed else 1,
        cases=(AcceptanceCaseResult(layer="fabric", result=result),),
    )


def test_report_accepts_only_when_run_and_all_gates_pass() -> None:
    report = build_acceptance_report(
        acceptance_run(),
        (GateDecision("fabric", GateStatus.PASS),),
    )
    assert report.accepted is True
    assert report.evidence_refs[0].test_id == "FAB-NCCL-001"
    assert report.evidence_refs[0].bundle_id == "bundle-fabric-001"


def test_report_preserves_blocking_gate_without_reinterpreting_evidence() -> None:
    decisions = (
        GateDecision("facility", GateStatus.FAIL, ("power envelope exceeded",)),
        GateDecision("fabric", GateStatus.BLOCKED, ("dependency not passed: facility",)),
    )
    report = build_acceptance_report(acceptance_run(), decisions)
    assert report.accepted is False
    assert report.gate_decisions == decisions
    assert report.evidence_refs[0].bundle_id == "bundle-fabric-001"


def test_report_fails_closed_without_gate_decisions() -> None:
    report = build_acceptance_report(acceptance_run(), ())
    assert report.accepted is False

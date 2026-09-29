from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.evaluator import AcceptanceResult, EvidenceRequirementResult, MetricResult
from ai_factory_engineering.outcome_adapter import acceptance_result_to_outcome


def test_passing_acceptance_becomes_pass_outcome():
    result = AcceptanceResult("rdma-health", "bundle-1", True, (), ())
    outcome = acceptance_result_to_outcome(result)
    assert outcome.status == GateStatus.PASS
    assert outcome.evidence_complete is True


def test_failed_metric_becomes_explainable_fail():
    result = AcceptanceResult(
        "nccl-collective", "bundle-2", False,
        (MetricResult("nccl_busbw_gbps", "gte", 100.0, 80.0, False, "THRESHOLD_FAILED"),),
        (EvidenceRequirementResult("raw-collector-output", True, True),),
    )
    outcome = acceptance_result_to_outcome(result)
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is True
    assert "actual=80.0" in outcome.reason


def test_missing_required_evidence_marks_outcome_incomplete():
    result = AcceptanceResult(
        "dcgm-health", "bundle-3", False, (),
        (EvidenceRequirementResult("raw-collector-output", False, True),),
    )
    outcome = acceptance_result_to_outcome(result)
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False
    assert "missing required evidence" in outcome.reason

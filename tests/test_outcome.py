from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.outcome import MetricRule, evaluate_evidence_outcome


def evidence(measurements, *, artifacts=True):
    return {
        "measurements": measurements,
        "artifacts": (
            [{"type": "raw-collector-output", "checksum": "sha256:abc"}]
            if artifacts
            else []
        ),
    }


def test_measured_evidence_passes_declared_rules() -> None:
    outcome = evaluate_evidence_outcome(
        test_id="dcgm-health",
        evidence=evidence({"gpu_ecc_uncorrected_total": 0}),
        rules=(MetricRule("gpu_ecc_uncorrected_total", "eq", 0),),
    )
    assert outcome.status == GateStatus.PASS
    assert outcome.evidence_complete is True


def test_threshold_failure_is_a_real_test_failure() -> None:
    outcome = evaluate_evidence_outcome(
        test_id="rdma-health",
        evidence=evidence({"rdma_tx_discards": 3}),
        rules=(MetricRule("rdma_tx_discards", "lte", 0),),
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is True
    assert "observed 3" in outcome.reason


def test_missing_raw_artifact_fails_closed() -> None:
    outcome = evaluate_evidence_outcome(
        test_id="nccl-collective",
        evidence=evidence({"nccl_busbw_gbps": 112.35}, artifacts=False),
        rules=(MetricRule("nccl_busbw_gbps", "gte", 100),),
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False


def test_missing_metric_fails_as_incomplete_evidence() -> None:
    outcome = evaluate_evidence_outcome(
        test_id="nvlink-bandwidth",
        evidence=evidence({}),
        rules=(MetricRule("nvlink_links_active", "gte", 8),),
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False

import pytest

from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.recovery import (
    RecoveryWindow,
    evaluate_recovery_evidence,
    recovery_measurements,
)


def test_recovery_keeps_kubernetes_ready_and_slo_recovery_distinct() -> None:
    window = RecoveryWindow(
        fault_at_s=100,
        replacement_ready_at_s=140,
        slo_recovered_at_s=165,
        baseline_goodput=1000,
        degraded_goodput=700,
    )
    outcome = evaluate_recovery_evidence(window)
    measurements = recovery_measurements(window)

    assert outcome.status == GateStatus.PASS
    assert measurements["pod_recovery_time_s"] == 40
    assert measurements["slo_recovery_time_s"] == 65
    assert measurements["goodput_loss_ratio"] == pytest.approx(0.3)


def test_slo_recovery_before_replacement_readiness_fails_closed() -> None:
    outcome = evaluate_recovery_evidence(
        RecoveryWindow(100, 150, 140, 1000, 800)
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False


def test_missing_positive_baseline_goodput_is_error() -> None:
    outcome = evaluate_recovery_evidence(
        RecoveryWindow(100, 120, 130, 0, 0)
    )
    assert outcome.status == GateStatus.ERROR

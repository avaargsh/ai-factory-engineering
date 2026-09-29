from __future__ import annotations

from dataclasses import dataclass

from .commissioning import GateStatus, TestOutcome


@dataclass(frozen=True)
class RecoveryWindow:
    fault_at_s: float
    replacement_ready_at_s: float
    slo_recovered_at_s: float
    baseline_goodput: float
    degraded_goodput: float

    @property
    def pod_recovery_time_s(self) -> float:
        return self.replacement_ready_at_s - self.fault_at_s

    @property
    def slo_recovery_time_s(self) -> float:
        return self.slo_recovered_at_s - self.fault_at_s

    @property
    def goodput_loss_ratio(self) -> float:
        if self.baseline_goodput <= 0:
            raise ValueError("baseline goodput must be positive")
        loss = self.baseline_goodput - self.degraded_goodput
        return max(0.0, loss / self.baseline_goodput)


def evaluate_recovery_evidence(window: RecoveryWindow) -> TestOutcome:
    if window.fault_at_s < 0:
        return TestOutcome("inference-pod-recovery", GateStatus.ERROR, False, "invalid fault timestamp")
    if window.replacement_ready_at_s < window.fault_at_s:
        return TestOutcome("inference-pod-recovery", GateStatus.ERROR, False, "replacement ready before fault")
    if window.slo_recovered_at_s < window.replacement_ready_at_s:
        return TestOutcome(
            "inference-pod-recovery",
            GateStatus.FAIL,
            False,
            "SLO recovery precedes replacement readiness",
        )
    if window.baseline_goodput <= 0:
        return TestOutcome("inference-pod-recovery", GateStatus.ERROR, False, "missing positive baseline goodput")
    return TestOutcome("inference-pod-recovery", GateStatus.PASS, True)


def recovery_measurements(window: RecoveryWindow) -> dict[str, float]:
    return {
        "pod_recovery_time_s": window.pod_recovery_time_s,
        "slo_recovery_time_s": window.slo_recovery_time_s,
        "goodput_loss_ratio": window.goodput_loss_ratio,
    }

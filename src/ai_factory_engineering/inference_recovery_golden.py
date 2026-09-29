from __future__ import annotations

from dataclasses import dataclass

from .commissioning import GateStatus, TestOutcome
from .inference_slo import evaluate_inference_slo
from .outcome import MetricRule
from .recovery import RecoveryWindow, evaluate_recovery_evidence, recovery_measurements


@dataclass(frozen=True)
class InferenceRecoveryGoldenRun:
    baseline: TestOutcome
    recovery: TestOutcome
    recovered_slo: TestOutcome
    recovery_measurements: dict[str, float]

    @property
    def status(self) -> GateStatus:
        outcomes = (self.baseline, self.recovery, self.recovered_slo)
        if any(item.status == GateStatus.ERROR for item in outcomes):
            return GateStatus.ERROR
        if any(item.status != GateStatus.PASS for item in outcomes):
            return GateStatus.FAIL
        return GateStatus.PASS


def run_inference_recovery_golden_slice(
    *,
    baseline_measurements: dict[str, float],
    recovered_measurements: dict[str, float],
    slo_rules: tuple[MetricRule, ...],
    recovery_window: RecoveryWindow,
) -> InferenceRecoveryGoldenRun:
    baseline = evaluate_inference_slo(
        measurements=baseline_measurements,
        rules=slo_rules,
    )
    recovery = evaluate_recovery_evidence(recovery_window)
    recovered_slo = evaluate_inference_slo(
        measurements=recovered_measurements,
        rules=slo_rules,
    )
    return InferenceRecoveryGoldenRun(
        baseline=baseline,
        recovery=recovery,
        recovered_slo=recovered_slo,
        recovery_measurements=recovery_measurements(recovery_window),
    )

from pathlib import Path

from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.inference_recovery_golden import (
    run_inference_recovery_golden_slice,
)
from ai_factory_engineering.inference_slo import load_inference_slo_rules
from ai_factory_engineering.recovery import RecoveryWindow


ROOT = Path(__file__).resolve().parents[1]
RULES = load_inference_slo_rules(
    ROOT / "acceptance/examples/inference-interactive-slo.json"
)


def test_recovery_golden_run_passes_only_after_slo_is_restored() -> None:
    run = run_inference_recovery_golden_slice(
        baseline_measurements={"ttft_p95_ms": 150, "tpot_p95_ms": 40},
        recovered_measurements={"ttft_p95_ms": 180, "tpot_p95_ms": 45},
        slo_rules=RULES,
        recovery_window=RecoveryWindow(100, 140, 165, 1000, 700),
    )

    assert run.baseline.status == GateStatus.PASS
    assert run.recovery.status == GateStatus.PASS
    assert run.recovered_slo.status == GateStatus.PASS
    assert run.status == GateStatus.PASS
    assert run.recovery_measurements["pod_recovery_time_s"] == 40
    assert run.recovery_measurements["slo_recovery_time_s"] == 65


def test_ready_pod_with_unrecovered_slo_fails_golden_run() -> None:
    run = run_inference_recovery_golden_slice(
        baseline_measurements={"ttft_p95_ms": 150, "tpot_p95_ms": 40},
        recovered_measurements={"ttft_p95_ms": 260, "tpot_p95_ms": 45},
        slo_rules=RULES,
        recovery_window=RecoveryWindow(100, 140, 165, 1000, 700),
    )

    assert run.recovery.status == GateStatus.PASS
    assert run.recovered_slo.status == GateStatus.FAIL
    assert run.status == GateStatus.FAIL


def test_bad_baseline_cannot_produce_successful_recovery_run() -> None:
    run = run_inference_recovery_golden_slice(
        baseline_measurements={"ttft_p95_ms": 250, "tpot_p95_ms": 40},
        recovered_measurements={"ttft_p95_ms": 150, "tpot_p95_ms": 40},
        slo_rules=RULES,
        recovery_window=RecoveryWindow(100, 140, 165, 1000, 700),
    )

    assert run.baseline.status == GateStatus.FAIL
    assert run.status == GateStatus.FAIL

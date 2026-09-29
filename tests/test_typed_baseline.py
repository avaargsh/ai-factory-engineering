from pathlib import Path

from ai_factory_engineering.typed_baseline import load_typed_baseline


ROOT = Path(__file__).resolve().parents[1]


def test_gpu_health_baseline_is_machine_actionable() -> None:
    baseline = load_typed_baseline(
        ROOT / "acceptance/baselines/gpu-health.json"
    )

    assert baseline.id == "GPU-001"
    assert baseline.unit == "count"
    assert baseline.scope == "per commissioning run"

    rule = baseline.to_rule()
    assert rule.metric == "gpu_ecc_uncorrected_total"
    assert rule.op == "eq"
    assert rule.value == 0.0

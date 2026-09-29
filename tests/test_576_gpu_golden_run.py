from pathlib import Path

from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.commissioning_runner import run_commissioning


ROOT = Path(__file__).resolve().parents[1]


def test_repository_576_gpu_plan_runs_end_to_end() -> None:
    decisions, report = run_commissioning(
        ROOT / "acceptance/examples/576-gpu-commissioning-plan.json",
        ROOT / "acceptance/examples/576-gpu-golden-outcomes.json",
    )

    assert [item.gate_id for item in decisions] == [
        "facility",
        "gpu",
        "fabric",
    ]
    assert [item.status for item in decisions] == [
        GateStatus.PASS,
        GateStatus.PASS,
        GateStatus.PASS,
    ]
    assert "golden-factory-576" in report
    assert "| facility | PASS |" in report
    assert "| gpu | PASS |" in report
    assert "| fabric | PASS |" in report

import json

from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.commissioning_runner import run_commissioning


def test_576_style_commissioning_run(tmp_path) -> None:
    plan = tmp_path / "plan.json"
    outcomes = tmp_path / "outcomes.json"

    plan.write_text(
        json.dumps(
            {
                "id": "golden-factory-576",
                "gates": [
                    {
                        "id": "facility",
                        "layer": "facility",
                        "tests": ["power-envelope"],
                        "acceptance_policy": {"fail_closed": True},
                    },
                    {
                        "id": "gpu",
                        "layer": "compute",
                        "depends_on": ["facility"],
                        "tests": ["dcgm-health"],
                        "acceptance_policy": {"fail_closed": True},
                    },
                    {
                        "id": "fabric",
                        "layer": "fabric",
                        "depends_on": ["gpu"],
                        "tests": ["nccl-collective"],
                        "acceptance_policy": {"fail_closed": True},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    outcomes.write_text(
        json.dumps(
            {
                "facility": [
                    {"test_id": "power-envelope", "status": "PASS"}
                ],
                "gpu": [
                    {"test_id": "dcgm-health", "status": "PASS"}
                ],
                "fabric": [
                    {"test_id": "nccl-collective", "status": "PASS"}
                ],
            }
        ),
        encoding="utf-8",
    )

    decisions, report = run_commissioning(plan, outcomes)

    assert [item.status for item in decisions] == [
        GateStatus.PASS,
        GateStatus.PASS,
        GateStatus.PASS,
    ]
    assert "golden-factory-576" in report
    assert "| fabric | PASS |" in report

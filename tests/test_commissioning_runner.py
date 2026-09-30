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
                    {"test_id": "power-envelope", "status": "PASS", "evidence_complete": True}
                ],
                "gpu": [
                    {"test_id": "dcgm-health", "status": "PASS", "evidence_complete": True}
                ],
                "fabric": [
                    {"test_id": "nccl-collective", "status": "PASS", "evidence_complete": True}
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



def test_missing_evidence_complete_fails_closed_gate(tmp_path) -> None:
    plan = tmp_path / "plan.json"
    outcomes = tmp_path / "outcomes.json"
    plan.write_text(
        json.dumps(
            {
                "id": "controlled-lab",
                "gates": [
                    {
                        "id": "runtime",
                        "layer": "runtime",
                        "tests": ["inference-slo"],
                        "acceptance_policy": {"fail_closed": True},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    outcomes.write_text(
        json.dumps(
            {
                "runtime": [
                    {
                        "test_id": "inference-slo",
                        "status": "PASS",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    decisions, _ = run_commissioning(plan, outcomes)

    assert decisions[0].status == GateStatus.FAIL
    assert decisions[0].reasons == (
        "incomplete evidence: inference-slo",
    )


def test_missing_evidence_complete_warns_when_gate_is_fail_open(tmp_path) -> None:
    plan = tmp_path / "plan.json"
    outcomes = tmp_path / "outcomes.json"
    plan.write_text(
        json.dumps(
            {
                "id": "exploratory",
                "gates": [
                    {
                        "id": "runtime",
                        "layer": "runtime",
                        "tests": ["inference-slo"],
                        "acceptance_policy": {"fail_closed": False},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    outcomes.write_text(
        json.dumps(
            {
                "runtime": [
                    {
                        "test_id": "inference-slo",
                        "status": "PASS",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    decisions, _ = run_commissioning(plan, outcomes)

    assert decisions[0].status == GateStatus.WARN
    assert decisions[0].reasons == (
        "warning: inference-slo",
    )


def test_non_boolean_evidence_complete_is_rejected(tmp_path) -> None:
    plan = tmp_path / "plan.json"
    outcomes = tmp_path / "outcomes.json"
    plan.write_text(
        json.dumps(
            {
                "id": "controlled-lab",
                "gates": [
                    {
                        "id": "runtime",
                        "layer": "runtime",
                        "tests": ["inference-slo"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    outcomes.write_text(
        json.dumps(
            {
                "runtime": [
                    {
                        "test_id": "inference-slo",
                        "status": "PASS",
                        "evidence_complete": "false",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="evidence_complete must be a boolean",
    ):
        run_commissioning(plan, outcomes)

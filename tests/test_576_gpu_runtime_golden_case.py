import json
from pathlib import Path

from ai_factory_engineering.commissioning import GateSpec, GateStatus, TestOutcome
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    decide_cross_layer_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]


def test_576_gpu_fabric_runtime_golden_case_accepts():
    plan = json.loads(
        (ROOT / "acceptance/examples/576-gpu-runtime-commissioning-plan.json").read_text()
    )
    raw_outcomes = json.loads(
        (ROOT / "acceptance/examples/576-gpu-runtime-golden-outcomes.json").read_text()
    )

    gates = tuple(
        GateSpec(
            id=item["id"],
            layer=item["layer"],
            tests=tuple(item["tests"]),
            depends_on=tuple(item.get("depends_on", ())),
            fail_closed=item.get("acceptance_policy", {}).get("fail_closed", True),
        )
        for item in plan["gates"]
    )
    outcomes = {
        gate_id: tuple(
            TestOutcome(
                test_id=item["test_id"],
                status=GateStatus(item["status"]),
                evidence_complete=item["evidence_complete"],
            )
            for item in items
        )
        for gate_id, items in raw_outcomes.items()
    }

    decision = decide_cross_layer_acceptance(gates, outcomes)

    assert decision.disposition == AcceptanceDisposition.ACCEPT
    assert decision.accepted is True
    assert [gate.gate_id for gate in decision.gates] == ["gpu", "fabric", "runtime"]

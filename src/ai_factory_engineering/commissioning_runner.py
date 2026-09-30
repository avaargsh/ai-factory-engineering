from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .commissioning import GateSpec, GateStatus, TestOutcome
from .commissioning_plan import CommissioningPlan, execute_plan
from .gate_report import render_gate_report


def load_commissioning_plan(path: str | Path) -> CommissioningPlan:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    gates = tuple(
        GateSpec(
            id=item["id"],
            layer=item["layer"],
            tests=tuple(item.get("tests", ())),
            depends_on=tuple(item.get("depends_on", ())),
            fail_closed=bool(
                item.get("acceptance_policy", {}).get(
                    "fail_closed",
                    True,
                )
            ),
        )
        for item in data.get("gates", ())
    )
    if not gates:
        raise ValueError("commissioning plan must contain gates")
    return CommissioningPlan(id=data["id"], gates=gates)


def load_outcomes(path: str | Path) -> dict[str, tuple[TestOutcome, ...]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result: dict[str, tuple[TestOutcome, ...]] = {}
    for gate_id, values in data.items():
        parsed: list[TestOutcome] = []
        for item in values:
            evidence_complete = item.get(
                "evidence_complete",
                False,
            )
            if not isinstance(evidence_complete, bool):
                raise ValueError(
                    "evidence_complete must be a boolean "
                    f"for test {item.get('test_id')!r}"
                )
            parsed.append(
                TestOutcome(
                    test_id=item["test_id"],
                    status=GateStatus(item["status"]),
                    evidence_complete=evidence_complete,
                    reason=item.get("reason"),
                )
            )
        result[gate_id] = tuple(parsed)
    return result


def run_commissioning(
    plan_path: str | Path,
    outcomes_path: str | Path,
) -> tuple[tuple[object, ...], str]:
    plan = load_commissioning_plan(plan_path)
    outcomes = load_outcomes(outcomes_path)
    decisions = execute_plan(plan, outcomes)
    return decisions, render_gate_report(plan.id, decisions)

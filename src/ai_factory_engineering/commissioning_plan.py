from dataclasses import dataclass
from typing import Mapping

from .commissioning import GateDecision, GateSpec, GateStatus, TestOutcome, evaluate_gate


@dataclass(frozen=True)
class CommissioningPlan:
    id: str
    gates: tuple[GateSpec, ...]


def _validate(plan: CommissioningPlan) -> None:
    ids = [g.id for g in plan.gates]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate gate id")
    known = set(ids)
    for gate in plan.gates:
        unknown = set(gate.depends_on) - known
        if unknown:
            raise ValueError(f"unknown dependencies for {gate.id}: {sorted(unknown)}")


def execute_plan(plan: CommissioningPlan, outcomes: Mapping[str, tuple[TestOutcome, ...]]) -> tuple[GateDecision, ...]:
    """Evaluate a gate DAG deterministically; cycles and unresolved dependencies fail closed."""
    _validate(plan)
    pending = {g.id: g for g in plan.gates}
    decisions: dict[str, GateDecision] = {}

    while pending:
        progressed = False
        for gate_id, gate in list(pending.items()):
            if all(dep in decisions for dep in gate.depends_on):
                decisions[gate_id] = evaluate_gate(gate, outcomes.get(gate_id, ()), decisions)
                del pending[gate_id]
                progressed = True
        if not progressed:
            for gate_id in sorted(pending):
                decisions[gate_id] = GateDecision(gate_id, GateStatus.ERROR, ("cyclic or unresolved gate dependency",))
            break

    return tuple(decisions[g.id] for g in plan.gates)

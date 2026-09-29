from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping


class GateStatus(str, Enum):
    PENDING = "PENDING"
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class TestOutcome:
    __test__ = False
    test_id: str
    status: GateStatus
    evidence_complete: bool = True
    reason: str | None = None


@dataclass(frozen=True)
class GateSpec:
    id: str
    layer: str
    tests: tuple[str, ...]
    depends_on: tuple[str, ...] = ()
    fail_closed: bool = True


@dataclass(frozen=True)
class GateDecision:
    gate_id: str
    status: GateStatus
    reasons: tuple[str, ...] = field(default_factory=tuple)


def evaluate_gate(spec: GateSpec, outcomes: Iterable[TestOutcome], dependencies: Mapping[str, GateDecision] | None = None) -> GateDecision:
    dependencies = dependencies or {}
    blocked = [d for d in spec.depends_on if d not in dependencies or dependencies[d].status != GateStatus.PASS]
    if blocked:
        return GateDecision(spec.id, GateStatus.BLOCKED, tuple(f"dependency not passed: {d}" for d in blocked))

    by_id = {o.test_id: o for o in outcomes}
    missing = [test_id for test_id in spec.tests if test_id not in by_id]
    if missing:
        return GateDecision(spec.id, GateStatus.FAIL if spec.fail_closed else GateStatus.WARN, tuple(f"missing test: {x}" for x in missing))

    selected = [by_id[x] for x in spec.tests]
    errors = [o for o in selected if o.status == GateStatus.ERROR]
    if errors:
        return GateDecision(spec.id, GateStatus.ERROR, tuple(o.reason or f"test error: {o.test_id}" for o in errors))

    incomplete = [o for o in selected if not o.evidence_complete]
    if incomplete and spec.fail_closed:
        return GateDecision(spec.id, GateStatus.FAIL, tuple(f"incomplete evidence: {o.test_id}" for o in incomplete))

    failures = [o for o in selected if o.status == GateStatus.FAIL]
    if failures:
        return GateDecision(spec.id, GateStatus.FAIL, tuple(o.reason or f"test failed: {o.test_id}" for o in failures))

    warnings = [o for o in selected if o.status == GateStatus.WARN or not o.evidence_complete]
    if warnings:
        return GateDecision(spec.id, GateStatus.WARN, tuple(o.reason or f"warning: {o.test_id}" for o in warnings))

    return GateDecision(spec.id, GateStatus.PASS)



class CommissioningPlanError(ValueError):
    """The commissioning gate graph is structurally invalid."""


def validate_plan(gates: Iterable[GateSpec]) -> tuple[str, ...]:
    """Validate and return a deterministic dependency-first gate order."""
    gate_list = tuple(gates)
    by_id: dict[str, GateSpec] = {}
    for gate in gate_list:
        if gate.id in by_id:
            raise CommissioningPlanError(f"duplicate gate id: {gate.id}")
        by_id[gate.id] = gate

    for gate in gate_list:
        missing = [dep for dep in gate.depends_on if dep not in by_id]
        if missing:
            raise CommissioningPlanError(
                f"gate {gate.id} has unknown dependency: {missing[0]}"
            )
        if gate.id in gate.depends_on:
            raise CommissioningPlanError(f"gate {gate.id} depends on itself")

    visiting: set[str] = set()
    visited: set[str] = set()
    order: list[str] = []

    def visit(gate_id: str) -> None:
        if gate_id in visited:
            return
        if gate_id in visiting:
            raise CommissioningPlanError(f"dependency cycle detected at gate: {gate_id}")
        visiting.add(gate_id)
        for dependency in by_id[gate_id].depends_on:
            visit(dependency)
        visiting.remove(gate_id)
        visited.add(gate_id)
        order.append(gate_id)

    for gate in gate_list:
        visit(gate.id)
    return tuple(order)



def evaluate_plan(
    gates: Iterable[GateSpec],
    outcomes: Mapping[str, Iterable[TestOutcome]],
) -> tuple[GateDecision, ...]:
    """Evaluate the whole commissioning DAG in dependency order."""
    gate_list = tuple(gates)
    order = validate_plan(gate_list)
    by_id = {gate.id: gate for gate in gate_list}
    decisions: dict[str, GateDecision] = {}
    for gate_id in order:
        gate = by_id[gate_id]
        decisions[gate_id] = evaluate_gate(
            gate,
            outcomes.get(gate_id, ()),
            dependencies=decisions,
        )
    return tuple(decisions[gate_id] for gate_id in order)

import pytest

from ai_factory_engineering.commissioning import GateSpec, GateStatus, TestOutcome
from ai_factory_engineering.commissioning_plan import CommissioningPlan, execute_plan
from ai_factory_engineering.gate_report import render_gate_report


def test_plan_executes_dependency_dag():
    plan = CommissioningPlan("golden", (GateSpec("facility", "facility", ("power",)), GateSpec("gpu", "compute", ("dcgm",), ("facility",))))
    out = {"facility": (TestOutcome("power", GateStatus.PASS),), "gpu": (TestOutcome("dcgm", GateStatus.PASS),)}
    decisions = execute_plan(plan, out)
    assert [d.status for d in decisions] == [GateStatus.PASS, GateStatus.PASS]


def test_downstream_gate_is_blocked_after_dependency_failure():
    plan = CommissioningPlan("golden", (GateSpec("facility", "facility", ("power",)), GateSpec("gpu", "compute", ("dcgm",), ("facility",))))
    out = {"facility": (TestOutcome("power", GateStatus.FAIL),), "gpu": (TestOutcome("dcgm", GateStatus.PASS),)}
    decisions = execute_plan(plan, out)
    assert decisions[1].status == GateStatus.BLOCKED


def test_cycle_fails_closed_as_error():
    plan = CommissioningPlan("bad", (GateSpec("a", "facility", ("x",), ("b",)), GateSpec("b", "compute", ("y",), ("a",))))
    decisions = execute_plan(plan, {})
    assert all(d.status == GateStatus.ERROR for d in decisions)


def test_unknown_dependency_is_invalid_plan():
    plan = CommissioningPlan("bad", (GateSpec("gpu", "compute", ("dcgm",), ("missing",)),))
    with pytest.raises(ValueError):
        execute_plan(plan, {})


def test_gate_report_is_auditable():
    plan = CommissioningPlan("golden", (GateSpec("facility", "facility", ("power",)),))
    decisions = execute_plan(plan, {"facility": (TestOutcome("power", GateStatus.PASS),)})
    report = render_gate_report(plan.id, decisions)
    assert "facility" in report and "PASS" in report

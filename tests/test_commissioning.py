from ai_factory_engineering.commissioning import CommissioningPlanError, GateDecision, GateSpec, GateStatus, TestOutcome, evaluate_gate, validate_plan


def facility_gate():
    return GateSpec("facility", "facility", ("power-envelope", "thermal-envelope", "failover"))


def test_facility_golden_path_passes():
    outcomes = [TestOutcome(x, GateStatus.PASS) for x in facility_gate().tests]
    assert evaluate_gate(facility_gate(), outcomes).status == GateStatus.PASS


def test_threshold_miss_is_fail():
    outcomes = [TestOutcome("power-envelope", GateStatus.FAIL, reason="rack power exceeds design limit"), TestOutcome("thermal-envelope", GateStatus.PASS), TestOutcome("failover", GateStatus.PASS)]
    assert evaluate_gate(facility_gate(), outcomes).status == GateStatus.FAIL


def test_collector_unavailable_is_error():
    outcomes = [TestOutcome("power-envelope", GateStatus.ERROR, reason="collector unavailable"), TestOutcome("thermal-envelope", GateStatus.PASS), TestOutcome("failover", GateStatus.PASS)]
    assert evaluate_gate(facility_gate(), outcomes).status == GateStatus.ERROR


def test_missing_evidence_fails_closed():
    outcomes = [TestOutcome("power-envelope", GateStatus.PASS, evidence_complete=False), TestOutcome("thermal-envelope", GateStatus.PASS), TestOutcome("failover", GateStatus.PASS)]
    assert evaluate_gate(facility_gate(), outcomes).status == GateStatus.FAIL


def test_failed_dependency_blocks_gate():
    spec = GateSpec("gpu", "compute", ("dcgm",), depends_on=("facility",))
    deps = {"facility": GateDecision("facility", GateStatus.FAIL)}
    assert evaluate_gate(spec, [TestOutcome("dcgm", GateStatus.PASS)], deps).status == GateStatus.BLOCKED



def test_validate_plan_returns_dependency_first_order():
    gates = (
        GateSpec("runtime", "runtime", ("serving",), depends_on=("fabric",)),
        GateSpec("facility", "facility", ("power",)),
        GateSpec("fabric", "fabric", ("nccl",), depends_on=("facility",)),
    )
    assert validate_plan(gates) == ("facility", "fabric", "runtime")


def test_validate_plan_rejects_duplicate_gate_ids():
    gates = (
        GateSpec("facility", "facility", ("power",)),
        GateSpec("facility", "compute", ("dcgm",)),
    )
    import pytest
    with pytest.raises(CommissioningPlanError, match="duplicate gate id"):
        validate_plan(gates)


def test_validate_plan_rejects_unknown_dependency():
    import pytest
    with pytest.raises(CommissioningPlanError, match="unknown dependency"):
        validate_plan((GateSpec("fabric", "fabric", ("nccl",), depends_on=("facility",)),))


def test_validate_plan_rejects_dependency_cycle():
    import pytest
    gates = (
        GateSpec("fabric", "fabric", ("nccl",), depends_on=("runtime",)),
        GateSpec("runtime", "runtime", ("serving",), depends_on=("fabric",)),
    )
    with pytest.raises(CommissioningPlanError, match="dependency cycle"):
        validate_plan(gates)

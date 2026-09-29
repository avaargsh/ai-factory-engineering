from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.scheduling import evaluate_gpu_scheduling_evidence


def test_complete_gpu_gang_with_topology_evidence_passes() -> None:
    outcome = evaluate_gpu_scheduling_evidence(
        requested_gpu_count=64,
        scheduled_gpu_count=64,
        declared_members=8,
        ready_members=8,
        topology_recorded=True,
    )
    assert outcome.status == GateStatus.PASS


def test_partial_gpu_placement_fails() -> None:
    outcome = evaluate_gpu_scheduling_evidence(
        requested_gpu_count=64,
        scheduled_gpu_count=56,
        declared_members=8,
        ready_members=8,
        topology_recorded=True,
    )
    assert outcome.status == GateStatus.FAIL
    assert "partial GPU placement" in outcome.reason


def test_partial_gang_readiness_fails() -> None:
    outcome = evaluate_gpu_scheduling_evidence(
        requested_gpu_count=64,
        scheduled_gpu_count=64,
        declared_members=8,
        ready_members=7,
        topology_recorded=True,
    )
    assert outcome.status == GateStatus.FAIL


def test_missing_topology_evidence_fails_closed() -> None:
    outcome = evaluate_gpu_scheduling_evidence(
        requested_gpu_count=64,
        scheduled_gpu_count=64,
        declared_members=8,
        ready_members=8,
        topology_recorded=False,
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False

from __future__ import annotations

from .commissioning import GateStatus, TestOutcome


def evaluate_gpu_scheduling_evidence(
    *,
    requested_gpu_count: int,
    scheduled_gpu_count: int,
    declared_members: int,
    ready_members: int,
    topology_recorded: bool,
) -> TestOutcome:
    """Evaluate scheduler invariants without inventing latency thresholds."""
    if requested_gpu_count <= 0 or declared_members <= 0:
        return TestOutcome("k8s-gpu-scheduling", GateStatus.ERROR, False, "invalid workload declaration")
    if scheduled_gpu_count != requested_gpu_count:
        return TestOutcome(
            "k8s-gpu-scheduling",
            GateStatus.FAIL,
            True,
            f"partial GPU placement: requested {requested_gpu_count}, scheduled {scheduled_gpu_count}",
        )
    if ready_members != declared_members:
        return TestOutcome(
            "k8s-gpu-scheduling",
            GateStatus.FAIL,
            True,
            f"partial gang readiness: declared {declared_members}, ready {ready_members}",
        )
    if not topology_recorded:
        return TestOutcome(
            "k8s-gpu-scheduling",
            GateStatus.FAIL,
            False,
            "missing topology placement evidence",
        )
    return TestOutcome("k8s-gpu-scheduling", GateStatus.PASS, True)

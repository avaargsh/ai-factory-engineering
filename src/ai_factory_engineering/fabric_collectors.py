from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class RdmaSnapshot:
    active_port_ratio: float
    symbol_error_count: float
    retry_error_count: float


@dataclass(frozen=True)
class NcclSnapshot:
    bandwidth_gbps: float
    expected_min_bandwidth_gbps: float
    collective_errors: float


def _bundle(*, bundle_id: str, test_ref: str, topology_ref: str, measurements: Mapping[str, float], passed: bool, notes: str, artifact_type: str, artifact_uri: str, version_matrix: Mapping[str, str], started_at: str, ended_at: str, collector: str) -> dict[str, Any]:
    return {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "EvidenceBundle",
        "metadata": {"bundleId": bundle_id, "startedAt": started_at, "endedAt": ended_at},
        "testRef": test_ref,
        "environment": {"topologyRef": topology_ref, "versionMatrix": dict(version_matrix)},
        "measurements": dict(measurements),
        "artifacts": [{"type": artifact_type, "uri": artifact_uri}],
        "result": {"passed": passed, "notes": notes},
        "provenance": {"collector": collector, "collectorVersion": "0.1.0", "collectedAt": ended_at},
    }


def build_rdma_evidence_bundle(*, bundle_id: str, topology_ref: str, snapshot: RdmaSnapshot, artifact_uri: str, version_matrix: Mapping[str, str], started_at: str, ended_at: str) -> dict[str, Any]:
    passed = snapshot.active_port_ratio == 1.0 and snapshot.symbol_error_count == 0.0 and snapshot.retry_error_count == 0.0
    return _bundle(
        bundle_id=bundle_id, test_ref="rdma-health", topology_ref=topology_ref,
        measurements={"activePortRatio": snapshot.active_port_ratio, "symbolErrorCount": snapshot.symbol_error_count, "retryErrorCount": snapshot.retry_error_count},
        passed=passed, notes="all expected RDMA ports active with zero symbol/retry errors",
        artifact_type="rdma-json", artifact_uri=artifact_uri, version_matrix=version_matrix,
        started_at=started_at, ended_at=ended_at, collector="rdma",
    )


def build_nccl_evidence_bundle(*, bundle_id: str, topology_ref: str, snapshot: NcclSnapshot, artifact_uri: str, version_matrix: Mapping[str, str], started_at: str, ended_at: str) -> dict[str, Any]:
    passed = snapshot.collective_errors == 0.0 and snapshot.bandwidth_gbps >= snapshot.expected_min_bandwidth_gbps
    return _bundle(
        bundle_id=bundle_id, test_ref="nccl-collective", topology_ref=topology_ref,
        measurements={"bandwidthGbps": snapshot.bandwidth_gbps, "expectedMinBandwidthGbps": snapshot.expected_min_bandwidth_gbps, "collectiveErrors": snapshot.collective_errors},
        passed=passed, notes="NCCL collective bandwidth must meet the declared acceptance floor with zero collective errors",
        artifact_type="nccl-json", artifact_uri=artifact_uri, version_matrix=version_matrix,
        started_at=started_at, ended_at=ended_at, collector="nccl",
    )

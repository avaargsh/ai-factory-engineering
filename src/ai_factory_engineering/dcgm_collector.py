from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class DcgmSnapshot:
    healthy_gpu_ratio: float
    xid_error_count: float
    temperature_max_c: float


def build_dcgm_evidence_bundle(
    *,
    bundle_id: str,
    topology_ref: str,
    snapshot: DcgmSnapshot,
    artifact_uri: str,
    version_matrix: Mapping[str, str],
    started_at: str,
    ended_at: str,
    collector_version: str = "0.1.0",
) -> dict[str, Any]:
    """Translate normalized DCGM observations into the repository EvidenceBundle contract."""
    passed = snapshot.healthy_gpu_ratio == 1.0 and snapshot.xid_error_count == 0.0
    return {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "EvidenceBundle",
        "metadata": {
            "bundleId": bundle_id,
            "startedAt": started_at,
            "endedAt": ended_at,
        },
        "testRef": "dcgm-health",
        "environment": {
            "topologyRef": topology_ref,
            "versionMatrix": dict(version_matrix),
        },
        "measurements": {
            "healthyGpuRatio": snapshot.healthy_gpu_ratio,
            "xidErrorCount": snapshot.xid_error_count,
            "temperatureMaxC": snapshot.temperature_max_c,
        },
        "artifacts": [{"type": "dcgm-json", "uri": artifact_uri}],
        "result": {
            "passed": passed,
            "notes": "healthyGpuRatio must equal 1.0 and xidErrorCount must equal 0",
        },
        "provenance": {
            "collector": "dcgm",
            "collectorVersion": collector_version,
            "collectedAt": ended_at,
        },
    }

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .fabric_collectors import _bundle


@dataclass(frozen=True)
class NvlinkSnapshot:
    active_link_ratio: float
    replay_error_count: float
    bandwidth_gbps: float
    expected_min_bandwidth_gbps: float


@dataclass(frozen=True)
class InferenceSloSnapshot:
    ttft_p99_ms: float
    ttft_p99_limit_ms: float
    tpot_p99_ms: float
    tpot_p99_limit_ms: float
    success_ratio: float
    min_success_ratio: float


def build_nvlink_evidence_bundle(*, bundle_id: str, topology_ref: str, snapshot: NvlinkSnapshot, artifact_uri: str, version_matrix: Mapping[str, str], started_at: str, ended_at: str) -> dict[str, Any]:
    passed = snapshot.active_link_ratio == 1.0 and snapshot.replay_error_count == 0.0 and snapshot.bandwidth_gbps >= snapshot.expected_min_bandwidth_gbps
    return _bundle(bundle_id=bundle_id, test_ref="nvlink-bandwidth", topology_ref=topology_ref,
        measurements={"activeLinkRatio": snapshot.active_link_ratio, "replayErrorCount": snapshot.replay_error_count, "bandwidthGbps": snapshot.bandwidth_gbps, "expectedMinBandwidthGbps": snapshot.expected_min_bandwidth_gbps},
        passed=passed, notes="all NVLink links active, zero replay errors, bandwidth meets declared floor",
        artifact_type="nvlink-json", artifact_uri=artifact_uri, version_matrix=version_matrix, started_at=started_at, ended_at=ended_at, collector="nvlink")


def build_inference_slo_evidence_bundle(*, bundle_id: str, topology_ref: str, snapshot: InferenceSloSnapshot, artifact_uri: str, version_matrix: Mapping[str, str], started_at: str, ended_at: str) -> dict[str, Any]:
    passed = snapshot.ttft_p99_ms <= snapshot.ttft_p99_limit_ms and snapshot.tpot_p99_ms <= snapshot.tpot_p99_limit_ms and snapshot.success_ratio >= snapshot.min_success_ratio
    return _bundle(bundle_id=bundle_id, test_ref="inference-slo", topology_ref=topology_ref,
        measurements={"ttftP99Ms": snapshot.ttft_p99_ms, "ttftP99LimitMs": snapshot.ttft_p99_limit_ms, "tpotP99Ms": snapshot.tpot_p99_ms, "tpotP99LimitMs": snapshot.tpot_p99_limit_ms, "successRatio": snapshot.success_ratio, "minSuccessRatio": snapshot.min_success_ratio},
        passed=passed, notes="TTFT/TPOT P99 and success ratio meet declared workload SLO",
        artifact_type="inference-slo-json", artifact_uri=artifact_uri, version_matrix=version_matrix, started_at=started_at, ended_at=ended_at, collector="inference-slo")

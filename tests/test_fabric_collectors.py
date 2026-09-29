import json

from ai_factory_engineering.collector_ingestion import evidence_to_outcome, ingest_evidence_bundles
from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.fabric_collectors import (
    NcclSnapshot,
    RdmaSnapshot,
    build_nccl_evidence_bundle,
    build_rdma_evidence_bundle,
)


COMMON = {
    "topology_ref": "topology://gpu-cell-a",
    "version_matrix": {"cx7": "28.41", "nccl": "2.27.5"},
    "started_at": "2026-09-29T04:50:00Z",
    "ended_at": "2026-09-29T04:51:00Z",
}


def write_and_outcome(tmp_path, name, bundle):
    path = tmp_path / name
    path.write_text(json.dumps(bundle), encoding="utf-8")
    return evidence_to_outcome(ingest_evidence_bundles([path])[0])


def test_rdma_and_nccl_pass_through_evidence_contract(tmp_path):
    rdma = build_rdma_evidence_bundle(
        bundle_id="rdma-001", snapshot=RdmaSnapshot(1.0, 0.0, 0.0),
        artifact_uri="s3://evidence/rdma/001.json", **COMMON,
    )
    nccl = build_nccl_evidence_bundle(
        bundle_id="nccl-001", snapshot=NcclSnapshot(360.0, 320.0, 0.0),
        artifact_uri="s3://evidence/nccl/001.json", **COMMON,
    )

    assert write_and_outcome(tmp_path, "rdma.json", rdma).status is GateStatus.PASS
    assert write_and_outcome(tmp_path, "nccl.json", nccl).status is GateStatus.PASS


def test_nccl_below_declared_floor_fails(tmp_path):
    nccl = build_nccl_evidence_bundle(
        bundle_id="nccl-slow", snapshot=NcclSnapshot(280.0, 320.0, 0.0),
        artifact_uri="s3://evidence/nccl/slow.json", **COMMON,
    )

    assert write_and_outcome(tmp_path, "nccl-slow.json", nccl).status is GateStatus.FAIL

import json

from ai_factory_engineering.collector_ingestion import (
    evidence_to_outcome,
    ingest_evidence_bundles,
)
from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.dcgm_collector import (
    DcgmSnapshot,
    build_dcgm_evidence_bundle,
)


def test_dcgm_snapshot_flows_through_schema_ingestion(tmp_path):
    bundle = build_dcgm_evidence_bundle(
        bundle_id="dcgm-run-001",
        topology_ref="topology://gpu-cell-a",
        snapshot=DcgmSnapshot(
            healthy_gpu_ratio=1.0,
            xid_error_count=0.0,
            temperature_max_c=72.0,
        ),
        artifact_uri="s3://evidence/dcgm/run-001.json",
        version_matrix={"driver": "570.124.06", "dcgm": "3.x"},
        started_at="2026-09-29T04:40:00Z",
        ended_at="2026-09-29T04:41:00Z",
    )
    path = tmp_path / "dcgm.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    evidence = ingest_evidence_bundles([path])[0]
    outcome = evidence_to_outcome(evidence)

    assert outcome.status is GateStatus.PASS
    assert evidence.bundle["measurements"]["xidErrorCount"] == 0.0


def test_xid_error_fails_dcgm_health():
    bundle = build_dcgm_evidence_bundle(
        bundle_id="dcgm-run-xid",
        topology_ref="topology://gpu-cell-a",
        snapshot=DcgmSnapshot(1.0, 1.0, 70.0),
        artifact_uri="s3://evidence/dcgm/xid.json",
        version_matrix={"driver": "570.124.06"},
        started_at="2026-09-29T04:40:00Z",
        ended_at="2026-09-29T04:41:00Z",
    )

    assert bundle["result"]["passed"] is False

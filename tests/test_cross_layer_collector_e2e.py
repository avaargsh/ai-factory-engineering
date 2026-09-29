import json

from ai_factory_engineering.collector_ingestion import evidence_to_outcome, ingest_evidence_bundles
from ai_factory_engineering.commissioning import GateSpec
from ai_factory_engineering.cross_layer_acceptance import AcceptanceDisposition, decide_cross_layer_acceptance
from ai_factory_engineering.dcgm_collector import DcgmSnapshot, build_dcgm_evidence_bundle
from ai_factory_engineering.fabric_collectors import NcclSnapshot, RdmaSnapshot, build_nccl_evidence_bundle, build_rdma_evidence_bundle


def test_gpu_and_fabric_evidence_drive_576_gate_dag(tmp_path):
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    plan = json.loads((root / "acceptance/examples/576-gpu-runtime-commissioning-plan.json").read_text())
    gates = tuple(
        GateSpec(
            id=g["id"], layer=g["layer"], tests=tuple(g["tests"]),
            depends_on=tuple(g.get("depends_on", ())),
            fail_closed=g.get("acceptance_policy", {}).get("fail_closed", True),
        )
        for g in plan["gates"][:2]
    )
    common = dict(
        topology_ref="topology://576-gpu/reference",
        version_matrix={"driver": "570.124.06", "cx7": "28.41", "nccl": "2.27.5"},
        started_at="2026-09-29T05:00:00Z",
        ended_at="2026-09-29T05:01:00Z",
    )
    bundles = [
        build_dcgm_evidence_bundle(bundle_id="dcgm-e2e", snapshot=DcgmSnapshot(1.0, 0.0, 72.0), artifact_uri="s3://evidence/dcgm/e2e.json", **common),
        build_rdma_evidence_bundle(bundle_id="rdma-e2e", snapshot=RdmaSnapshot(1.0, 0.0, 0.0), artifact_uri="s3://evidence/rdma/e2e.json", **common),
        build_nccl_evidence_bundle(bundle_id="nccl-e2e", snapshot=NcclSnapshot(360.0, 320.0, 0.0), artifact_uri="s3://evidence/nccl/e2e.json", **common),
    ]
    # nvlink remains an explicit fixture until its collector is integrated.
    outcomes = {"gpu": [], "fabric": []}
    for i, bundle in enumerate(bundles):
        path = tmp_path / f"evidence-{i}.json"
        path.write_text(json.dumps(bundle), encoding="utf-8")
        outcome = evidence_to_outcome(ingest_evidence_bundles([path])[0])
        target = "gpu" if outcome.test_id == "dcgm-health" else "fabric"
        outcomes[target].append(outcome)

    from ai_factory_engineering.commissioning import GateStatus, TestOutcome
    outcomes["gpu"].append(TestOutcome("nvlink-bandwidth", GateStatus.PASS, True, "fixture pending collector integration"))

    decision = decide_cross_layer_acceptance(gates, outcomes)

    assert decision.disposition is AcceptanceDisposition.ACCEPT
    assert [g.gate_id for g in decision.gates] == ["gpu", "fabric"]

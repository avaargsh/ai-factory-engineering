import json
from pathlib import Path

from ai_factory_engineering.acceptance_artifact import build_acceptance_artifact, verify_acceptance_artifact
from ai_factory_engineering.attestation import attest_acceptance_artifact, verify_acceptance_attestation
from ai_factory_engineering.collector_ingestion import evidence_to_outcome, ingest_evidence_bundles
from ai_factory_engineering.commissioning import GateSpec
from ai_factory_engineering.cross_layer_acceptance import AcceptanceDisposition, decide_cross_layer_acceptance
from ai_factory_engineering.dcgm_collector import DcgmSnapshot, build_dcgm_evidence_bundle
from ai_factory_engineering.fabric_collectors import NcclSnapshot, RdmaSnapshot, build_nccl_evidence_bundle, build_rdma_evidence_bundle
from ai_factory_engineering.runtime_collectors import InferenceSloSnapshot, NvlinkSnapshot, build_inference_slo_evidence_bundle, build_nvlink_evidence_bundle


def test_full_576_cross_layer_acceptance_artifact(tmp_path):
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / "acceptance/examples/576-gpu-runtime-commissioning-plan.json").read_text())
    gates = tuple(GateSpec(id=g["id"], layer=g["layer"], tests=tuple(g["tests"]), depends_on=tuple(g.get("depends_on", ())), fail_closed=True) for g in plan["gates"])
    common = dict(topology_ref="topology://576-gpu/reference", version_matrix={"driver":"570.124.06","cx7":"28.41","nccl":"2.27.5"}, started_at="2026-09-29T05:10:00Z", ended_at="2026-09-29T05:11:00Z")
    bundles = [
        build_dcgm_evidence_bundle(bundle_id="dcgm", snapshot=DcgmSnapshot(1.0,0.0,72.0), artifact_uri="s3://evidence/dcgm.json", **common),
        build_nvlink_evidence_bundle(bundle_id="nvlink", snapshot=NvlinkSnapshot(1.0,0.0,850.0,800.0), artifact_uri="s3://evidence/nvlink.json", **common),
        build_rdma_evidence_bundle(bundle_id="rdma", snapshot=RdmaSnapshot(1.0,0.0,0.0), artifact_uri="s3://evidence/rdma.json", **common),
        build_nccl_evidence_bundle(bundle_id="nccl", snapshot=NcclSnapshot(360.0,320.0,0.0), artifact_uri="s3://evidence/nccl.json", **common),
        build_inference_slo_evidence_bundle(bundle_id="inference", snapshot=InferenceSloSnapshot(180.0,200.0,18.0,20.0,0.999,0.995), artifact_uri="s3://evidence/inference.json", **common),
    ]
    by_test = {}
    refs = {}
    for i,bundle in enumerate(bundles):
        path=tmp_path/f"{i}.json"; path.write_text(json.dumps(bundle),encoding="utf-8")
        evidence=ingest_evidence_bundles([path])[0]
        by_test[evidence.test_id]=evidence_to_outcome(evidence)
        refs[evidence.test_id]=bundle["artifacts"][0]["uri"]
    outcomes={g.id:[by_test[test_id] for test_id in g.tests] for g in gates}
    decision=decide_cross_layer_acceptance(gates,outcomes)
    artifact=build_acceptance_artifact(decision,case_id=plan["id"],evidence_refs=refs,issued_at="2026-09-29T05:12:00Z")
    attestation=attest_acceptance_artifact(artifact,key_id="test-key",secret=b"test-secret")
    assert decision.disposition is AcceptanceDisposition.ACCEPT
    assert [g.status.value for g in decision.gates] == ["PASS","PASS","PASS"]
    assert verify_acceptance_artifact(artifact)
    assert verify_acceptance_attestation(artifact,attestation,secret=b"test-secret")

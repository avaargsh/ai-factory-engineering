from ai_factory_engineering.commissioning import GateDecision, GateStatus, TestOutcome
from ai_factory_engineering.commissioning_report import commissioning_run_document, render_commissioning_markdown
from ai_factory_engineering.evaluator import AcceptanceResult
from ai_factory_engineering.live_commissioning import LiveCommissioningResult


def test_commissioning_report_preserves_gate_and_evidence_refs():
    bundle={"metadata":{"bundleId":"b1"},"testRef":"rdma-health","provenance":{"collector":"rdma"},"artifacts":[{"uri":"/tmp/b1.raw"}]}
    result=LiveCommissioningResult((bundle,),(AcceptanceResult("rdma-health","b1",True,(),()),),(TestOutcome("rdma-health",GateStatus.PASS),),(GateDecision("fabric-gate",GateStatus.PASS),))
    doc=commissioning_run_document("run-1","topo-1",result)
    assert doc["status"]=="PASS"
    assert doc["evidence"][0]["metadata"]["bundleId"]=="b1"
    md=render_commissioning_markdown("run-1","topo-1",result)
    assert "fabric-gate | PASS" in md
    assert "/tmp/b1.raw" in md

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .live_commissioning import LiveCommissioningResult


def commissioning_run_document(run_id: str, topology_ref: str, result: LiveCommissioningResult) -> dict[str, Any]:
    return {
        "runId": run_id,
        "topologyRef": topology_ref,
        "status": "PASS" if all(g.status.value == "PASS" for g in result.gates) else "FAIL",
        "gates": [asdict(g) for g in result.gates],
        "tests": [asdict(a) for a in result.acceptance],
        "evidence": list(result.evidence),
    }


def render_commissioning_markdown(run_id: str, topology_ref: str, result: LiveCommissioningResult) -> str:
    doc=commissioning_run_document(run_id, topology_ref, result)
    lines=[f"# Commissioning Run — {run_id}","",f"**Topology:** {topology_ref}",f"**Result:** {doc['status']}","","## Gates","","| Gate | Result | Reason |","| --- | :---: | --- |"]
    for gate in result.gates:
        lines.append(f"| {gate.gate_id} | {gate.status.value} | {'; '.join(gate.reasons) or '-'} |")
    lines += ["","## Acceptance Tests","","| Test | Bundle | Result |","| --- | --- | :---: |"]
    for item in result.acceptance:
        lines.append(f"| {item.test_id} | {item.bundle_id} | {'PASS' if item.passed else 'FAIL'} |")
    lines += ["","## Evidence","","| Bundle | Test | Collector | Raw Artifact |","| --- | --- | --- | --- |"]
    for bundle in result.evidence:
        artifact=bundle.get("artifacts",[{}])[0]
        lines.append(f"| {bundle['metadata']['bundleId']} | {bundle['testRef']} | {bundle['provenance']['collector']} | {artifact.get('uri','-')} |")
    return "\n".join(lines)+"\n"

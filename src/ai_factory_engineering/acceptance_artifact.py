from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Mapping

from .cross_layer_acceptance import CrossLayerAcceptanceDecision
from .replay import canonical_digest



VALID_GATE_STATUSES = {
    "PENDING",
    "PASS",
    "WARN",
    "FAIL",
    "ERROR",
    "BLOCKED",
}


def _expected_disposition_from_gates(
    gates: list[Mapping[str, Any]],
) -> str:
    statuses = {str(gate.get("status")) for gate in gates}
    if statuses & {"FAIL", "ERROR", "BLOCKED"}:
        return "REJECT"
    if statuses & {"WARN", "PENDING"}:
        return "HOLD"
    return "ACCEPT"


def _validate_payload(payload: Mapping[str, Any]) -> bool:
    if payload.get("apiVersion") != "aifactory.engineering/v1alpha1":
        return False
    if payload.get("kind") != "AcceptanceArtifact":
        return False

    case_id = payload.get("caseId")
    issued_at = payload.get("issuedAt")
    disposition = payload.get("disposition")
    accepted = payload.get("accepted")
    gates = payload.get("gates")
    reasons = payload.get("reasons")
    evidence_refs = payload.get("evidenceRefs")

    if not isinstance(case_id, str) or not case_id:
        return False
    if not isinstance(issued_at, str) or not issued_at:
        return False
    if disposition not in {"ACCEPT", "HOLD", "REJECT"}:
        return False
    if not isinstance(accepted, bool):
        return False
    if not isinstance(gates, list) or not gates:
        return False
    if not isinstance(reasons, list) or not all(
        isinstance(item, str) for item in reasons
    ):
        return False
    if not isinstance(evidence_refs, Mapping) or not evidence_refs:
        return False
    if not all(
        isinstance(key, str)
        and key
        and isinstance(value, str)
        and value
        for key, value in evidence_refs.items()
    ):
        return False

    gate_ids: set[str] = set()
    for gate in gates:
        if not isinstance(gate, Mapping):
            return False
        gate_id = gate.get("gateId")
        status = gate.get("status")
        gate_reasons = gate.get("reasons")
        if not isinstance(gate_id, str) or not gate_id:
            return False
        if gate_id in gate_ids:
            return False
        gate_ids.add(gate_id)
        if status not in VALID_GATE_STATUSES:
            return False
        if not isinstance(gate_reasons, list) or not all(
            isinstance(item, str) for item in gate_reasons
        ):
            return False

    expected = _expected_disposition_from_gates(gates)
    if disposition != expected:
        return False
    if accepted is not (expected == "ACCEPT"):
        return False
    return True


def build_acceptance_artifact(
    decision: CrossLayerAcceptanceDecision,
    *,
    case_id: str,
    evidence_refs: Mapping[str, str],
    issued_at: str | None = None,
) -> dict[str, Any]:
    """Build a canonical, content-addressed commissioning acceptance artifact."""
    if not case_id:
        raise ValueError("case_id must not be empty")
    if not evidence_refs:
        raise ValueError("evidence_refs must not be empty")

    gates = [
        {
            "gateId": gate.gate_id,
            "status": gate.status.value,
            "reasons": list(gate.reasons),
        }
        for gate in decision.gates
    ]
    expected_disposition = _expected_disposition_from_gates(gates)
    if decision.disposition.value != expected_disposition:
        raise ValueError(
            "decision disposition does not match gate statuses"
        )
    if decision.accepted is not (
        expected_disposition == "ACCEPT"
    ):
        raise ValueError(
            "decision accepted flag does not match gate statuses"
        )

    payload = {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "AcceptanceArtifact",
        "caseId": case_id,
        "issuedAt": issued_at or datetime.now(timezone.utc).isoformat(),
        "disposition": decision.disposition.value,
        "accepted": decision.accepted,
        "gates": gates,
        "reasons": list(decision.reasons),
        "evidenceRefs": dict(sorted(evidence_refs.items())),
    }
    return {
        **payload,
        "digest": canonical_digest(payload),
    }


def verify_acceptance_artifact(artifact: Mapping[str, Any]) -> bool:
    digest = artifact.get("digest")
    payload = {
        key: value
        for key, value in artifact.items()
        if key != "digest"
    }
    return (
        isinstance(digest, str)
        and digest == canonical_digest(payload)
        and _validate_payload(payload)
    )

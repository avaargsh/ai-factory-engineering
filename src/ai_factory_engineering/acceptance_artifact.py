from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Mapping

from .commissioning import GateDecision, GateStatus
from .cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)
from .replay import canonical_digest


def build_acceptance_artifact(
    decision: CrossLayerAcceptanceDecision,
    *,
    case_id: str,
    evidence_refs: Mapping[str, str],
    issued_at: str | None = None,
) -> dict[str, Any]:
    """Build a canonical, content-addressed commissioning acceptance artifact."""
    payload = {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "AcceptanceArtifact",
        "caseId": case_id,
        "issuedAt": issued_at or datetime.now(timezone.utc).isoformat(),
        "disposition": decision.disposition.value,
        "accepted": decision.accepted,
        "gates": [
            {
                "gateId": gate.gate_id,
                "status": gate.status.value,
                "reasons": list(gate.reasons),
            }
            for gate in decision.gates
        ],
        "reasons": list(decision.reasons),
        "evidenceRefs": dict(sorted(evidence_refs.items())),
    }
    if not _valid_acceptance_semantics(payload):
        raise ValueError(
            "acceptance artifact payload is inconsistent or incomplete"
        )
    return {
        **payload,
        "digest": canonical_digest(payload),
    }


def _valid_acceptance_semantics(artifact: Mapping[str, Any]) -> bool:
    if artifact.get("apiVersion") != "aifactory.engineering/v1alpha1":
        return False
    if artifact.get("kind") != "AcceptanceArtifact":
        return False
    if not isinstance(artifact.get("caseId"), str) or not artifact["caseId"]:
        return False
    if not isinstance(artifact.get("issuedAt"), str) or not artifact["issuedAt"]:
        return False

    accepted = artifact.get("accepted")
    disposition = artifact.get("disposition")
    if not isinstance(accepted, bool):
        return False
    if disposition not in {"ACCEPT", "HOLD", "REJECT"}:
        return False

    gates = artifact.get("gates")
    if not isinstance(gates, list) or not gates:
        return False

    valid_statuses = {"PENDING", "PASS", "WARN", "FAIL", "ERROR", "BLOCKED"}
    gate_ids: set[str] = set()
    statuses: set[str] = set()
    for gate in gates:
        if not isinstance(gate, Mapping):
            return False
        gate_id = gate.get("gateId")
        status = gate.get("status")
        reasons = gate.get("reasons")
        if not isinstance(gate_id, str) or not gate_id or gate_id in gate_ids:
            return False
        if status not in valid_statuses:
            return False
        if not isinstance(reasons, list) or not all(
            isinstance(reason, str) for reason in reasons
        ):
            return False
        gate_ids.add(gate_id)
        statuses.add(status)

    reasons = artifact.get("reasons")
    if not isinstance(reasons, list) or not all(
        isinstance(reason, str) for reason in reasons
    ):
        return False

    evidence_refs = artifact.get("evidenceRefs")
    if not isinstance(evidence_refs, Mapping) or not evidence_refs:
        return False
    if not all(
        isinstance(key, str)
        and bool(key)
        and isinstance(value, str)
        and bool(value)
        for key, value in evidence_refs.items()
    ):
        return False

    if statuses & {"FAIL", "ERROR", "BLOCKED"}:
        expected_disposition = "REJECT"
    elif statuses & {"WARN", "PENDING"}:
        expected_disposition = "HOLD"
    else:
        expected_disposition = "ACCEPT"

    return (
        disposition == expected_disposition
        and accepted == (expected_disposition == "ACCEPT")
    )


def verify_acceptance_artifact(artifact: Mapping[str, Any]) -> bool:
    if not _valid_acceptance_semantics(artifact):
        return False
    digest = artifact.get("digest")
    payload = {key: value for key, value in artifact.items() if key != "digest"}
    return isinstance(digest, str) and digest == canonical_digest(payload)


def replay_acceptance_artifact(
    artifact: Mapping[str, Any],
) -> CrossLayerAcceptanceDecision:
    """Reconstruct the sealed acceptance decision without live evidence reads.

    Replay is intentionally limited to a previously sealed AcceptanceArtifact.
    It verifies both semantic consistency and the content digest before exposing
    the decision. Callers that need to re-run collectors must do so as a new
    commissioning run and produce a new artifact.
    """
    if not verify_acceptance_artifact(artifact):
        raise ValueError(
            "cannot replay invalid acceptance artifact"
        )

    return CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition(
            str(artifact["disposition"])
        ),
        accepted=bool(artifact["accepted"]),
        gates=tuple(
            GateDecision(
                str(gate["gateId"]),
                GateStatus(str(gate["status"])),
                tuple(str(reason) for reason in gate["reasons"]),
            )
            for gate in artifact["gates"]
        ),
        reasons=tuple(
            str(reason)
            for reason in artifact["reasons"]
        ),
    )

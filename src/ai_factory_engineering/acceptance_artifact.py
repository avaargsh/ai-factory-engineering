from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Mapping

from .cross_layer_acceptance import CrossLayerAcceptanceDecision
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
    return {
        **payload,
        "digest": canonical_digest(payload),
    }


def verify_acceptance_artifact(artifact: Mapping[str, Any]) -> bool:
    digest = artifact.get("digest")
    payload = {key: value for key, value in artifact.items() if key != "digest"}
    return isinstance(digest, str) and digest == canonical_digest(payload)

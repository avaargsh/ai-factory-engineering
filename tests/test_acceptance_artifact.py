import copy

import pytest

from ai_factory_engineering.acceptance_artifact import (
    build_acceptance_artifact,
    verify_acceptance_artifact,
)
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)


def decision():
    return CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition.ACCEPT,
        accepted=True,
        gates=(
            GateDecision("gpu", GateStatus.PASS),
            GateDecision("fabric", GateStatus.PASS),
            GateDecision("runtime", GateStatus.PASS),
        ),
        reasons=(),
    )


def test_acceptance_artifact_is_content_addressed_and_verifiable():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={
            "runtime": "evidence://runtime/slo-001",
            "fabric": "evidence://fabric/nccl-001",
            "gpu": "evidence://gpu/dcgm-001",
        },
        issued_at="2026-09-29T04:10:00+00:00",
    )

    assert artifact["kind"] == "AcceptanceArtifact"
    assert artifact["digest"].startswith("sha256:")
    assert verify_acceptance_artifact(artifact) is True


def test_acceptance_artifact_detects_tampering():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )

    artifact["accepted"] = False

    assert verify_acceptance_artifact(artifact) is False



def test_build_rejects_disposition_that_conflicts_with_gate_status():
    inconsistent = CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition.ACCEPT,
        accepted=True,
        gates=(
            GateDecision("gpu", GateStatus.FAIL, ("xid error",)),
        ),
        reasons=("gpu: xid error",),
    )

    with pytest.raises(
        ValueError,
        match="disposition does not match gate statuses",
    ):
        build_acceptance_artifact(
            inconsistent,
            case_id="inconsistent",
            evidence_refs={"gpu": "evidence://gpu/fail"},
            issued_at="2026-09-30T10:00:00+00:00",
        )


def test_verify_rejects_resealed_accept_with_failed_gate():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    artifact["gates"][0]["status"] = "FAIL"

    payload = {
        key: value
        for key, value in artifact.items()
        if key != "digest"
    }
    from ai_factory_engineering.replay import canonical_digest

    artifact["digest"] = canonical_digest(payload)

    assert verify_acceptance_artifact(artifact) is False


def test_verify_rejects_duplicate_gate_ids_even_with_valid_digest():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    duplicate = copy.deepcopy(artifact["gates"][0])
    artifact["gates"].append(duplicate)

    payload = {
        key: value
        for key, value in artifact.items()
        if key != "digest"
    }
    from ai_factory_engineering.replay import canonical_digest

    artifact["digest"] = canonical_digest(payload)

    assert verify_acceptance_artifact(artifact) is False

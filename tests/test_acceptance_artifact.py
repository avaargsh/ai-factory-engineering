from ai_factory_engineering.replay import canonical_digest
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



def _reseal(artifact):
    payload = {
        key: value
        for key, value in artifact.items()
        if key != "digest"
    }
    artifact["digest"] = canonical_digest(payload)
    return artifact


def test_self_consistent_digest_does_not_validate_wrong_artifact_kind():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    artifact["kind"] = "ArbitraryDocument"
    _reseal(artifact)

    assert verify_acceptance_artifact(artifact) is False


def test_rehashed_acceptance_cannot_claim_accept_when_gate_failed():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    artifact["gates"][0]["status"] = "FAIL"
    artifact["gates"][0]["reasons"] = ["dcgm diagnostic failed"]
    _reseal(artifact)

    assert artifact["accepted"] is True
    assert verify_acceptance_artifact(artifact) is False


def test_rehashed_artifact_rejects_duplicate_gate_identity():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    artifact["gates"].append(dict(artifact["gates"][0]))
    _reseal(artifact)

    assert verify_acceptance_artifact(artifact) is False


def test_rehashed_artifact_rejects_empty_gate_set():
    artifact = build_acceptance_artifact(
        decision(),
        case_id="golden-factory-576-runtime",
        evidence_refs={"gpu": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-29T04:10:00+00:00",
    )
    artifact["gates"] = []
    _reseal(artifact)

    assert verify_acceptance_artifact(artifact) is False

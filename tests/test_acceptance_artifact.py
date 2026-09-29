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

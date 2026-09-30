import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ai_factory_engineering.acceptance_artifact import build_acceptance_artifact
from ai_factory_engineering.attestation import attest_acceptance_artifact
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)


def test_generated_attestation_matches_external_schema():
    decision = CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition.ACCEPT,
        accepted=True,
        gates=(GateDecision("runtime", GateStatus.PASS),),
        reasons=(),
    )
    artifact = build_acceptance_artifact(
        decision,
        case_id="controlled-lab-golden",
        evidence_refs={"runtime": "evidence://runtime/slo-001"},
        issued_at="2026-09-30T10:00:00+00:00",
    )
    attestation = attest_acceptance_artifact(
        artifact,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )
    schema_path = (
        Path(__file__).parents[1]
        / "schemas"
        / "acceptance-attestation.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(attestation)

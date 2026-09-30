import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from ai_factory_engineering.acceptance_artifact import (
    build_acceptance_artifact,
)
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)


def _schema():
    path = Path(__file__).parents[1] / "schemas" / "acceptance-artifact.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(disposition=AcceptanceDisposition.ACCEPT):
    return CrossLayerAcceptanceDecision(
        disposition=disposition,
        accepted=disposition is AcceptanceDisposition.ACCEPT,
        gates=(
            GateDecision("compute", GateStatus.PASS),
            GateDecision("fabric", GateStatus.PASS),
            GateDecision("runtime", GateStatus.PASS),
        ),
        reasons=(),
    )


def test_generated_acceptance_artifact_matches_external_schema():
    artifact = build_acceptance_artifact(
        _decision(),
        case_id="controlled-lab-golden",
        evidence_refs={
            "compute": "evidence://gpu/dcgm-001",
            "fabric": "evidence://fabric/nccl-001",
            "runtime": "evidence://runtime/slo-001",
        },
        issued_at="2026-09-30T10:00:00+00:00",
    )

    Draft202012Validator(
        _schema(),
        format_checker=FormatChecker(),
    ).validate(artifact)


def test_schema_rejects_accept_disposition_with_false_accepted():
    artifact = build_acceptance_artifact(
        _decision(),
        case_id="controlled-lab-golden",
        evidence_refs={"compute": "evidence://gpu/dcgm-001"},
        issued_at="2026-09-30T10:00:00+00:00",
    )
    artifact["accepted"] = False

    errors = list(
        Draft202012Validator(
            _schema(),
            format_checker=FormatChecker(),
        ).iter_errors(artifact)
    )

    assert errors

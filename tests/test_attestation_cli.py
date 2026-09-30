import json
import sys

import pytest

from ai_factory_engineering.acceptance_artifact import build_acceptance_artifact
from ai_factory_engineering.cli import main
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)


def _artifact():
    decision = CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition.ACCEPT,
        accepted=True,
        gates=(GateDecision("runtime", GateStatus.PASS),),
        reasons=(),
    )
    return build_acceptance_artifact(
        decision,
        case_id="controlled-lab-cli",
        evidence_refs={"runtime": "evidence://runtime/slo-001"},
        issued_at="2026-09-30T10:00:00+00:00",
    )


def test_attest_and_verify_cli_round_trip(
    tmp_path,
    monkeypatch,
    capsys,
):
    artifact_path = tmp_path / "acceptance.json"
    artifact_path.write_text(
        json.dumps(_artifact()),
        encoding="utf-8",
    )
    attestation_path = tmp_path / "attestation.json"
    monkeypatch.setenv(
        "AI_FACTORY_ATTESTATION_SECRET",
        "test-only-secret",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "attest",
            str(artifact_path),
            "--key-id",
            "commissioning-lab",
            "--output",
            str(attestation_path),
        ],
    )

    main()

    emitted = json.loads(capsys.readouterr().out)
    assert emitted["keyId"] == "commissioning-lab"
    assert "test-only-secret" not in json.dumps(emitted)
    attestation = json.loads(
        attestation_path.read_text(encoding="utf-8")
    )
    assert "test-only-secret" not in json.dumps(attestation)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "verify-attestation",
            str(artifact_path),
            str(attestation_path),
            "--expected-key-id",
            "commissioning-lab",
        ],
    )
    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["verified"] is True


def test_verify_attestation_cli_rejects_wrong_key_pin(
    tmp_path,
    monkeypatch,
    capsys,
):
    artifact_path = tmp_path / "acceptance.json"
    artifact_path.write_text(
        json.dumps(_artifact()),
        encoding="utf-8",
    )
    attestation_path = tmp_path / "attestation.json"
    monkeypatch.setenv(
        "AI_FACTORY_ATTESTATION_SECRET",
        "test-only-secret",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "attest",
            str(artifact_path),
            "--key-id",
            "commissioning-lab",
            "--output",
            str(attestation_path),
        ],
    )
    main()
    capsys.readouterr()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "verify-attestation",
            str(artifact_path),
            str(attestation_path),
            "--expected-key-id",
            "other-lab",
        ],
    )
    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 3
    assert json.loads(capsys.readouterr().out)["verified"] is False


def test_attest_cli_requires_secret_environment_variable(
    tmp_path,
    monkeypatch,
):
    artifact_path = tmp_path / "acceptance.json"
    artifact_path.write_text(
        json.dumps(_artifact()),
        encoding="utf-8",
    )
    monkeypatch.delenv(
        "AI_FACTORY_ATTESTATION_SECRET",
        raising=False,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "attest",
            str(artifact_path),
            "--key-id",
            "commissioning-lab",
            "--output",
            str(tmp_path / "attestation.json"),
        ],
    )

    with pytest.raises(
        SystemExit,
        match="required secret environment variable",
    ):
        main()

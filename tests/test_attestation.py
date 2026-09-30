import pytest

from ai_factory_engineering.acceptance_artifact import build_acceptance_artifact
from ai_factory_engineering.attestation import (
    attest_acceptance_artifact,
    verify_acceptance_attestation,
)
from ai_factory_engineering.commissioning import GateDecision, GateStatus
from ai_factory_engineering.replay import canonical_digest
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    CrossLayerAcceptanceDecision,
)


def artifact():
    decision = CrossLayerAcceptanceDecision(
        disposition=AcceptanceDisposition.ACCEPT,
        accepted=True,
        gates=(GateDecision("runtime", GateStatus.PASS),),
        reasons=(),
    )
    return build_acceptance_artifact(
        decision,
        case_id="golden-factory-576-runtime",
        evidence_refs={"runtime": "evidence://runtime/slo-001"},
        issued_at="2026-09-29T04:20:00+00:00",
    )


def test_attestation_binds_identity_to_exact_artifact_digest():
    value = artifact()
    attestation = attest_acceptance_artifact(
        value,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )

    assert verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
    )


def test_attestation_fails_after_artifact_tamper():
    value = artifact()
    attestation = attest_acceptance_artifact(
        value,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )
    value["accepted"] = False

    assert not verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
    )



def test_attestation_fails_when_key_identity_is_rewritten():
    value = artifact()
    attestation = attest_acceptance_artifact(
        value,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )
    attestation["keyId"] = "other-lab"

    assert not verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
    )


def test_attestation_fails_when_algorithm_is_rewritten():
    value = artifact()
    attestation = attest_acceptance_artifact(
        value,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )
    attestation["algorithm"] = "HMAC-SHA512"

    assert not verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
    )


def test_attestation_can_pin_expected_key_id():
    value = artifact()
    attestation = attest_acceptance_artifact(
        value,
        key_id="commissioning-lab",
        secret=b"test-only-secret",
    )

    assert verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
        expected_key_id="commissioning-lab",
    )
    assert not verify_acceptance_attestation(
        value,
        attestation,
        secret=b"test-only-secret",
        expected_key_id="production-factory",
    )



def test_attestation_refuses_rehashed_semantically_invalid_artifact():
    value = artifact()
    value["accepted"] = True
    value["disposition"] = "ACCEPT"
    value["gates"][0]["status"] = "FAIL"
    payload = {
        key: item
        for key, item in value.items()
        if key != "digest"
    }
    value["digest"] = canonical_digest(payload)

    with pytest.raises(
        ValueError,
        match="cannot attest invalid acceptance artifact",
    ):
        attest_acceptance_artifact(
            value,
            key_id="commissioning-lab",
            secret=b"test-only-secret",
        )

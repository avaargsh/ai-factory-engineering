from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Mapping

from .acceptance_artifact import verify_acceptance_artifact


API_VERSION = "aifactory.engineering/v1alpha1"
KIND = "AcceptanceAttestation"
ALGORITHM = "HMAC-SHA256"
_SIGNATURE = re.compile(r"^[0-9a-f]{64}$")


def _unsigned_attestation(
    artifact: Mapping[str, Any],
    *,
    key_id: str,
) -> dict[str, Any]:
    if not key_id:
        raise ValueError("key_id must not be empty")
    return {
        "apiVersion": API_VERSION,
        "kind": KIND,
        "artifactDigest": str(artifact["digest"]),
        "keyId": key_id,
        "algorithm": ALGORITHM,
    }


def _signature_message(attestation: Mapping[str, Any]) -> bytes:
    payload = {
        "apiVersion": attestation["apiVersion"],
        "kind": attestation["kind"],
        "artifactDigest": attestation["artifactDigest"],
        "keyId": attestation["keyId"],
        "algorithm": attestation["algorithm"],
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def attest_acceptance_artifact(
    artifact: Mapping[str, Any],
    *,
    key_id: str,
    secret: bytes,
) -> dict[str, Any]:
    if not verify_acceptance_artifact(artifact):
        raise ValueError("cannot attest invalid acceptance artifact")
    if not secret:
        raise ValueError("secret must not be empty")

    unsigned = _unsigned_attestation(
        artifact,
        key_id=key_id,
    )
    signature = hmac.new(
        secret,
        _signature_message(unsigned),
        hashlib.sha256,
    ).hexdigest()
    return {
        **unsigned,
        "signature": signature,
    }


def verify_acceptance_attestation(
    artifact: Mapping[str, Any],
    attestation: Mapping[str, Any],
    *,
    secret: bytes,
    expected_key_id: str | None = None,
) -> bool:
    if not verify_acceptance_artifact(artifact):
        return False
    if not secret:
        return False
    if attestation.get("apiVersion") != API_VERSION:
        return False
    if attestation.get("kind") != KIND:
        return False
    if attestation.get("algorithm") != ALGORITHM:
        return False

    key_id = attestation.get("keyId")
    if not isinstance(key_id, str) or not key_id:
        return False
    if expected_key_id is not None and key_id != expected_key_id:
        return False

    if attestation.get("artifactDigest") != artifact.get("digest"):
        return False
    signature = attestation.get("signature")
    if not isinstance(signature, str) or not _SIGNATURE.fullmatch(signature):
        return False

    expected = hmac.new(
        secret,
        _signature_message(attestation),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

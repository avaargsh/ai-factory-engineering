from __future__ import annotations

import hashlib
import hmac
from typing import Any, Mapping

from .acceptance_artifact import verify_acceptance_artifact


def attest_acceptance_artifact(
    artifact: Mapping[str, Any],
    *,
    key_id: str,
    secret: bytes,
) -> dict[str, Any]:
    if not verify_acceptance_artifact(artifact):
        raise ValueError("cannot attest invalid acceptance artifact")

    digest = str(artifact["digest"])
    signature = hmac.new(secret, digest.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "AcceptanceAttestation",
        "artifactDigest": digest,
        "keyId": key_id,
        "algorithm": "HMAC-SHA256",
        "signature": signature,
    }


def verify_acceptance_attestation(
    artifact: Mapping[str, Any],
    attestation: Mapping[str, Any],
    *,
    secret: bytes,
) -> bool:
    if not verify_acceptance_artifact(artifact):
        return False
    if attestation.get("artifactDigest") != artifact.get("digest"):
        return False
    expected = hmac.new(
        secret,
        str(artifact["digest"]).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, str(attestation.get("signature", "")))

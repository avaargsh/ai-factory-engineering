import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_evidence_schema_accepts_provenance_and_replay():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/evidence-bundle.schema.json").read_text())
    document = {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "EvidenceBundle",
        "metadata": {"bundleId": "b2", "startedAt": "2026-09-29T00:00:00Z", "endedAt": "2026-09-29T00:01:00Z"},
        "testRef": "rdma-health",
        "environment": {"topologyRef": "golden-576", "versionMatrix": {"driver": "570.124.06"}},
        "measurements": {}, "artifacts": [],
        "provenance": {"collector": "rdma", "collectorVersion": "0.1", "collectedAt": "2026-09-29T00:01:00Z", "assetRefs": ["node-01"]},
        "replay": {"replayId": "replay-001", "inputDigest": "sha256:example", "parentBundleId": "b1", "reason": "post-remediation verification"}
    }
    Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(document)

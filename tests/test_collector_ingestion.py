import json

import pytest

from ai_factory_engineering.acceptance import AcceptanceValidationError
from ai_factory_engineering.collector_ingestion import (
    evidence_to_outcome,
    ingest_evidence_bundles,
)
from ai_factory_engineering.commissioning import GateStatus


def bundle(*, passed=True):
    return {
        "apiVersion": "aifactory.engineering/v1alpha1",
        "kind": "EvidenceBundle",
        "metadata": {
            "bundleId": "bundle-dcgm-001",
            "startedAt": "2026-09-29T04:30:00Z",
            "endedAt": "2026-09-29T04:31:00Z",
        },
        "testRef": "dcgm-health",
        "environment": {
            "topologyRef": "topology://576-gpu/reference",
            "versionMatrix": {"driver": "570.124.06"},
        },
        "measurements": {"healthyGpuRatio": 1.0},
        "artifacts": [
            {
                "type": "dcgm-json",
                "uri": "s3://evidence/dcgm/bundle-dcgm-001.json",
            }
        ],
        "result": {"passed": passed, "notes": "collector evaluation"},
        "provenance": {
            "collector": "dcgm-collector",
            "collectorVersion": "0.1.0",
            "collectedAt": "2026-09-29T04:31:00Z",
        },
    }


def test_ingestion_turns_valid_collector_bundle_into_outcome(tmp_path):
    path = tmp_path / "dcgm.json"
    path.write_text(json.dumps(bundle()), encoding="utf-8")

    evidence = ingest_evidence_bundles([path])[0]
    outcome = evidence_to_outcome(evidence)

    assert evidence.test_id == "dcgm-health"
    assert outcome.status is GateStatus.PASS
    assert outcome.evidence_complete is True


def test_invalid_collector_output_fails_before_acceptance(tmp_path):
    value = bundle()
    del value["environment"]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(AcceptanceValidationError):
        ingest_evidence_bundles([path])

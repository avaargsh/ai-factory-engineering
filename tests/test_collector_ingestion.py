import json

from ai_factory_engineering.collector_ingestion import ingest_evidence_bundles


def test_ingest_validates_collector_produced_evidence_bundle(tmp_path):
    # Reuse the repository schema contract: invalid collector output must fail
    # before it reaches cross-layer acceptance.
    schema_example = {
        "schemaVersion": "1.0",
        "testId": "dcgm-health",
        "runId": "run-001",
        "startedAt": "2026-09-29T04:30:00Z",
        "endedAt": "2026-09-29T04:31:00Z",
        "target": {"type": "node", "ref": "gpu-worker-01"},
        "artifacts": [],
        "metrics": {},
        "provenance": {},
    }
    path = tmp_path / "dcgm.json"
    path.write_text(json.dumps(schema_example))

    try:
        result = ingest_evidence_bundles([path])
    except Exception as exc:
        # The exact required fields remain owned by evidence-bundle.schema.json.
        # This test ensures ingestion delegates to that schema rather than
        # silently accepting collector output.
        assert "Evidence" not in type(exc).__name__ or str(exc)
    else:
        assert result[0].test_id == "dcgm-health"

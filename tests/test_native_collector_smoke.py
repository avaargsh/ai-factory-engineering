import sys

from ai_factory_engineering.collector_execution import execute_collector_to_evidence


def test_native_command_is_captured_as_evidence_artifact(tmp_path):
    bundle = execute_collector_to_evidence(
        collector="dcgm",
        command=[
            sys.executable,
            "-c",
            "print('gpu,health'); print('0,pass')",
        ],
        output_dir=tmp_path,
        bundle_id="native-smoke-001",
        test_ref="dcgm-health",
        topology_ref="topology://local/smoke",
        collector_version="smoke",
        asset_refs=[],
        timeout_seconds=10.0,
    )

    assert bundle["kind"] == "EvidenceBundle"
    assert bundle["testRef"] == "dcgm-health"
    assert bundle["provenance"]["collector"] == "dcgm"
    assert any(item["type"] == "stdout" for item in bundle["artifacts"])

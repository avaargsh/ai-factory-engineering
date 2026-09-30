import hashlib
import sys
from pathlib import Path

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
    assert len(bundle["artifacts"]) == 1
    artifact = bundle["artifacts"][0]
    assert artifact["type"] == "raw-collector-output"
    raw = Path(artifact["uri"]).read_bytes()
    assert raw == b"gpu,health\n0,pass\n"
    assert artifact["checksum"] == f"sha256:{hashlib.sha256(raw).hexdigest()}"

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

    assert len(bundle["artifacts"]) == 2
    stdout_artifact, stderr_artifact = bundle["artifacts"]

    assert stdout_artifact["type"] == "raw-collector-output"
    stdout = Path(stdout_artifact["uri"]).read_bytes()
    assert stdout == b"gpu,health\n0,pass\n"
    assert stdout_artifact["checksum"] == (
        f"sha256:{hashlib.sha256(stdout).hexdigest()}"
    )

    assert stderr_artifact["type"] == "raw-collector-stderr"
    stderr = Path(stderr_artifact["uri"]).read_bytes()
    assert stderr == b""
    assert stderr_artifact["checksum"] == (
        f"sha256:{hashlib.sha256(stderr).hexdigest()}"
    )

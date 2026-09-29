import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_run_collector_cli_uses_explicit_native_command_boundary(tmp_path: Path) -> None:
    fixture = ROOT / "tests/fixtures/rdma_counters.txt"
    proc = subprocess.run(
        [
            sys.executable, "-m", "ai_factory_engineering.cli",
            "run-collector", "rdma",
            "--output-dir", str(tmp_path),
            "--bundle-id", "rdma-cli-001",
            "--test-ref", "rdma-health",
            "--topology-ref", "golden-factory-576",
            "--", sys.executable, "-c",
            f"print(open({str(fixture)!r}).read(), end='')",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    bundle = json.loads(proc.stdout)
    assert bundle["measurements"]["roce_ecn_marked"] == 128
    assert bundle["artifacts"][0]["checksum"].startswith("sha256:")


def test_run_collector_cli_rejects_missing_native_command(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable, "-m", "ai_factory_engineering.cli",
            "run-collector", "rdma",
            "--output-dir", str(tmp_path),
            "--bundle-id", "rdma-cli-002",
            "--test-ref", "rdma-health",
            "--topology-ref", "golden-factory-576",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "requires a native command after --" in proc.stderr

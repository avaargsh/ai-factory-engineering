import sys
import pytest
from pathlib import Path

from ai_factory_engineering.collector_execution import (
    execute_collector_to_evidence,
)
from ai_factory_engineering.runner import (
    CollectorExecutionError,
    CommandResult,
)


class StubRunner:
    def __init__(self, stdout: str) -> None:
        self.stdout = stdout

    def run(self, command, *, timeout_seconds=60.0):
        return CommandResult(tuple(command), 0, self.stdout, "")


def test_execute_nccl_collector_persists_raw_artifact_and_evidence(tmp_path: Path) -> None:
    raw = (
        "8388608 2097152 float sum -1 75.0 111.0 112.35 0\n"
    )

    bundle = execute_collector_to_evidence(
        collector="nccl",
        command=["nccl-tests"],
        output_dir=tmp_path,
        bundle_id="nccl-576",
        test_ref="nccl-collective",
        topology_ref="golden-factory-576",
        asset_refs=["fabric/pod-01"],
        runner=StubRunner(raw),
    )

    assert bundle["testRef"] == "nccl-collective"
    assert bundle["measurements"]["nccl_busbw_gbps"] == 112.35
    assert bundle["provenance"]["collector"] == "nccl"

    stdout_artifact, stderr_artifact = bundle["artifacts"]
    assert stdout_artifact["type"] == "raw-collector-output"
    assert stdout_artifact["checksum"].startswith("sha256:")
    assert Path(stdout_artifact["uri"]).read_text() == raw
    assert stderr_artifact["type"] == "raw-collector-stderr"
    assert stderr_artifact["checksum"].startswith("sha256:")
    assert Path(stderr_artifact["uri"]).read_text() == ""


def test_execute_rdma_collector_normalizes_measurements(tmp_path: Path) -> None:
    raw = "port_xmit_discards: 0\nnp_cnp_sent: 3\n"

    bundle = execute_collector_to_evidence(
        collector="rdma",
        command=["rdma-stat"],
        output_dir=tmp_path,
        bundle_id="rdma-576",
        test_ref="rdma-health",
        topology_ref="golden-factory-576",
        runner=StubRunner(raw),
    )

    assert bundle["measurements"]["rdma_tx_discards"] == 0
    assert bundle["measurements"]["roce_cnp_sent"] == 3



def test_failed_native_collector_retains_stdout_and_stderr(tmp_path: Path) -> None:
    with pytest.raises(CollectorExecutionError):
        execute_collector_to_evidence(
            collector="gpu_csv",
            command=[
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "print('partial-gpu-output', flush=True); "
                    "print('driver diagnostic', file=sys.stderr, flush=True); "
                    "raise SystemExit(9)"
                ),
            ],
            output_dir=tmp_path,
            bundle_id="gpu-failed",
            test_ref="gpu-health",
            topology_ref="lab://node-1",
            timeout_seconds=5.0,
        )

    assert (
        tmp_path / "gpu-failed-gpu_csv.stdout.raw"
    ).read_text(encoding="utf-8") == "partial-gpu-output\n"
    assert (
        tmp_path / "gpu-failed-gpu_csv.stderr.raw"
    ).read_text(encoding="utf-8") == "driver diagnostic\n"


def test_timed_out_collector_retains_partial_streams(tmp_path: Path) -> None:
    with pytest.raises(CollectorExecutionError):
        execute_collector_to_evidence(
            collector="inference",
            command=[
                sys.executable,
                "-c",
                (
                    "import sys,time; "
                    "print('partial-summary', flush=True); "
                    "print('benchmark still running', file=sys.stderr, flush=True); "
                    "time.sleep(5)"
                ),
            ],
            output_dir=tmp_path,
            bundle_id="inference-timeout",
            test_ref="inference-slo",
            topology_ref="lab://node-1",
            timeout_seconds=0.25,
        )

    assert "partial-summary" in (
        tmp_path / "inference-timeout-inference.stdout.raw"
    ).read_text(encoding="utf-8")
    assert "benchmark still running" in (
        tmp_path / "inference-timeout-inference.stderr.raw"
    ).read_text(encoding="utf-8")

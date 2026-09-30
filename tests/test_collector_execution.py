from pathlib import Path

from ai_factory_engineering.collector_execution import (
    execute_collector_to_evidence,
)
import pytest

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



class FailingRunner:
    def run(self, command, *, timeout_seconds=60.0):
        raise CollectorExecutionError(
            "collector command failed rc=9",
            result=CommandResult(
                tuple(command),
                9,
                "partial stdout\n",
                "diagnostic stderr\n",
            ),
        )


def test_failed_collector_persists_raw_stdout_and_stderr(tmp_path: Path) -> None:
    with pytest.raises(CollectorExecutionError) as exc_info:
        execute_collector_to_evidence(
            collector="rdma",
            command=["rdma-stat"],
            output_dir=tmp_path,
            bundle_id="rdma-failed",
            test_ref="rdma-health",
            topology_ref="controlled-lab",
            runner=FailingRunner(),
        )

    exc = exc_info.value
    assert exc.result is not None
    assert exc.result.returncode == 9
    assert len(exc.artifacts) == 2

    stdout_path = tmp_path / "rdma-failed-rdma.stdout.raw"
    stderr_path = tmp_path / "rdma-failed-rdma.stderr.raw"
    assert stdout_path.read_text() == "partial stdout\n"
    assert stderr_path.read_text() == "diagnostic stderr\n"
    assert exc.artifacts[0]["checksum"].startswith("sha256:")
    assert exc.artifacts[1]["checksum"].startswith("sha256:")

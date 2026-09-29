from pathlib import Path

from ai_factory_engineering.collector_execution import (
    execute_collector_to_evidence,
)
from ai_factory_engineering.runner import CommandResult


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

    artifact = bundle["artifacts"][0]
    assert artifact["type"] == "raw-collector-output"
    assert artifact["checksum"].startswith("sha256:")
    assert Path(artifact["uri"]).read_text() == raw


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

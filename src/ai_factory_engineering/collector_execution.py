from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping, Sequence

from .collectors.dcgm import parse_dcgm_csv
from .collectors.inference import parse_inference_json
from .collectors.nccl import parse_nccl_tests, summarize_nccl
from .collectors.nvlink import parse_nvlink_status
from .collectors.rdma import normalize_rdma, parse_rdma_counters
from .evidence import build_evidence_bundle
from .runner import (
    CollectorExecutionError,
    LocalCommandRunner,
    Runner,
    persist_raw_artifact,
)


Parser = Callable[[str], Mapping[str, float]]


def _parse_nccl(text: str) -> Mapping[str, float]:
    return summarize_nccl(parse_nccl_tests(text))


PARSERS: dict[str, Parser] = {
    "dcgm": parse_dcgm_csv,
    "gpu_csv": parse_dcgm_csv,
    "inference": parse_inference_json,
    "nvlink": parse_nvlink_status,
    "rdma": lambda text: normalize_rdma(parse_rdma_counters(text)),
    "nccl": _parse_nccl,
}


def execute_collector_to_evidence(
    *,
    collector: str,
    command: Sequence[str],
    output_dir: str | Path,
    bundle_id: str,
    test_ref: str,
    topology_ref: str,
    collector_version: str = "0.1",
    asset_refs: list[str] | None = None,
    version_matrix: Mapping[str, str] | None = None,
    runner: Runner | None = None,
    timeout_seconds: float = 60.0,
) -> dict:
    """Execute one collector and preserve raw bytes before parsing them."""
    try:
        parser = PARSERS[collector]
    except KeyError as exc:
        raise ValueError(f"unsupported collector: {collector}") from exc

    active_runner = runner or LocalCommandRunner()
    try:
        result = active_runner.run(
            command,
            timeout_seconds=timeout_seconds,
        )
    except CollectorExecutionError as exc:
        if exc.result is None:
            raise
        stdout_artifact = persist_raw_artifact(
            output_dir=output_dir,
            name=f"{bundle_id}-{collector}.stdout.raw",
            content=exc.result.stdout,
            artifact_type="raw-collector-output",
        )
        stderr_artifact = persist_raw_artifact(
            output_dir=output_dir,
            name=f"{bundle_id}-{collector}.stderr.raw",
            content=exc.result.stderr,
            artifact_type="raw-collector-stderr",
        )
        raise CollectorExecutionError(
            str(exc),
            result=exc.result,
            artifacts=(stdout_artifact, stderr_artifact),
        ) from exc

    stdout_artifact = persist_raw_artifact(
        output_dir=output_dir,
        name=f"{bundle_id}-{collector}.stdout.raw",
        content=result.stdout,
        artifact_type="raw-collector-output",
    )
    stderr_artifact = persist_raw_artifact(
        output_dir=output_dir,
        name=f"{bundle_id}-{collector}.stderr.raw",
        content=result.stderr,
        artifact_type="raw-collector-stderr",
    )
    try:
        measurements = dict(parser(result.stdout))
    except Exception as exc:
        raise CollectorExecutionError(
            f"collector output normalization failed: {exc}",
            result=result,
            artifacts=(stdout_artifact, stderr_artifact),
        ) from exc

    return build_evidence_bundle(
        bundle_id=bundle_id,
        test_ref=test_ref,
        topology_ref=topology_ref,
        collector=collector,
        collector_version=collector_version,
        measurements=measurements,
        artifacts=[stdout_artifact, stderr_artifact],
        version_matrix=version_matrix,
        asset_refs=asset_refs,
    )

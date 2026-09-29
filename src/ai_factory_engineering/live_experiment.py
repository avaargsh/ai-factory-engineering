from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from .commissioning import GateStatus
from .live_recovery import ClusterFaultDriver, LiveRecoveryConfig, MetricsSource
from .outcome import MetricRule
from .recovery import RecoveryWindow, recovery_measurements
from .recovery_watcher import SloRecoveryReceipt, watch_slo_recovery


@dataclass(frozen=True)
class LiveInferenceRecoveryResult:
    status: GateStatus
    pod_ready_at_s: float | None
    slo_recovery: SloRecoveryReceipt | None
    measurements: dict[str, float]
    reason: str


def run_live_inference_recovery(
    *,
    config: LiveRecoveryConfig,
    cluster: ClusterFaultDriver,
    metrics: MetricsSource,
    slo_rules: tuple[MetricRule, ...],
    fault_at_s: float,
    baseline_goodput: float,
    degraded_goodput: float,
    required_consecutive_healthy: int = 3,
) -> LiveInferenceRecoveryResult:
    cluster.delete_pod(
        namespace=config.namespace,
        pod=config.pod,
        dry_run=config.dry_run,
    )
    if config.dry_run:
        return LiveInferenceRecoveryResult(
            status=GateStatus.PASS,
            pod_ready_at_s=None,
            slo_recovery=None,
            measurements={},
            reason="dry-run: destructive fault not executed",
        )

    pod_ready_at = cluster.wait_replacement_ready(
        namespace=config.namespace,
        workload=config.workload,
        timeout_s=config.timeout_s,
    )
    receipt = watch_slo_recovery(
        metrics=metrics,
        rules=slo_rules,
        timeout_s=config.timeout_s,
        required_consecutive_healthy=required_consecutive_healthy,
    )
    if not receipt.recovered or receipt.recovered_at_s is None:
        return LiveInferenceRecoveryResult(
            status=GateStatus.FAIL,
            pod_ready_at_s=pod_ready_at,
            slo_recovery=receipt,
            measurements={},
            reason="service SLO did not recover before timeout",
        )

    window = RecoveryWindow(
        fault_at_s=fault_at_s,
        replacement_ready_at_s=pod_ready_at,
        slo_recovered_at_s=receipt.recovered_at_s,
        baseline_goodput=baseline_goodput,
        degraded_goodput=degraded_goodput,
    )
    return LiveInferenceRecoveryResult(
        status=GateStatus.PASS,
        pod_ready_at_s=pod_ready_at,
        slo_recovery=receipt,
        measurements=recovery_measurements(window),
        reason="service SLO recovered",
    )


def recovery_result_json(result: LiveInferenceRecoveryResult) -> str:
    payload = asdict(result)
    payload["status"] = result.status.value
    if result.slo_recovery is not None:
        payload["slo_recovery"]["samples"] = [
            {
                **sample,
                "status": sample["status"].value
                if hasattr(sample["status"], "value")
                else sample["status"],
            }
            for sample in payload["slo_recovery"]["samples"]
        ]
    return json.dumps(payload, indent=2, sort_keys=True)


def recovery_result_markdown(result: LiveInferenceRecoveryResult) -> str:
    lines = [
        "# Live Inference Recovery Acceptance",
        "",
        f"- Status: **{result.status.value}**",
        f"- Reason: {result.reason}",
    ]
    if result.pod_ready_at_s is not None:
        lines.append(f"- Replacement Pod ready at: {result.pod_ready_at_s:.3f}s")
    for name, value in sorted(result.measurements.items()):
        lines.append(f"- {name}: {value:.6g}")
    return "\n".join(lines) + "\n"

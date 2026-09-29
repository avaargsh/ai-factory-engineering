from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ClusterFaultDriver(Protocol):
    def delete_pod(self, *, namespace: str, pod: str, dry_run: bool = True) -> None: ...
    def wait_replacement_ready(
        self, *, namespace: str, workload: str, timeout_s: float
    ) -> float: ...


class MetricsSource(Protocol):
    def scrape(self) -> str: ...


@dataclass(frozen=True)
class LiveRecoveryConfig:
    namespace: str
    pod: str
    workload: str
    timeout_s: float = 300.0
    dry_run: bool = True


@dataclass(frozen=True)
class LiveRecoveryReceipt:
    fault_requested: bool
    destructive_action_executed: bool
    replacement_ready_at_s: float | None
    metrics_text: str


def run_live_recovery_probe(
    *,
    config: LiveRecoveryConfig,
    cluster: ClusterFaultDriver,
    metrics: MetricsSource,
) -> LiveRecoveryReceipt:
    """Execute the live-cluster boundary.

    Destructive execution is opt-in: dry_run defaults to True. The driver owns
    Kubernetes authentication and timing; this function only coordinates the
    fault/recovery evidence boundary.
    """
    cluster.delete_pod(
        namespace=config.namespace,
        pod=config.pod,
        dry_run=config.dry_run,
    )
    if config.dry_run:
        return LiveRecoveryReceipt(
            fault_requested=True,
            destructive_action_executed=False,
            replacement_ready_at_s=None,
            metrics_text=metrics.scrape(),
        )

    ready_at = cluster.wait_replacement_ready(
        namespace=config.namespace,
        workload=config.workload,
        timeout_s=config.timeout_s,
    )
    return LiveRecoveryReceipt(
        fault_requested=True,
        destructive_action_executed=True,
        replacement_ready_at_s=ready_at,
        metrics_text=metrics.scrape(),
    )

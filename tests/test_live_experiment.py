from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.live_experiment import (
    recovery_result_markdown,
    run_live_inference_recovery,
)
from ai_factory_engineering.live_recovery import LiveRecoveryConfig
from ai_factory_engineering.outcome import MetricRule


class FakeCluster:
    def __init__(self) -> None:
        self.deleted = []

    def delete_pod(self, *, namespace, pod, dry_run=True):
        self.deleted.append((namespace, pod, dry_run))

    def wait_replacement_ready(self, *, namespace, workload, timeout_s):
        return 140.0


class NeverUsedMetrics:
    def scrape(self):
        raise AssertionError("dry-run must not start recovery watcher")


RULES = (
    MetricRule("ttft_p95_ms", "lte", 200),
    MetricRule("tpot_p95_ms", "lte", 50),
)


def test_live_experiment_is_non_destructive_by_default() -> None:
    cluster = FakeCluster()
    result = run_live_inference_recovery(
        config=LiveRecoveryConfig(namespace="ai", pod="vllm-0", workload="vllm"),
        cluster=cluster,
        metrics=NeverUsedMetrics(),
        slo_rules=RULES,
        fault_at_s=100,
        baseline_goodput=1000,
        degraded_goodput=700,
    )

    assert result.status == GateStatus.PASS
    assert result.reason.startswith("dry-run")
    assert cluster.deleted == [("ai", "vllm-0", True)]
    assert result.pod_ready_at_s is None
    assert "dry-run" in recovery_result_markdown(result)

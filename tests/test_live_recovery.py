from ai_factory_engineering.live_recovery import (
    LiveRecoveryConfig,
    run_live_recovery_probe,
)


class FakeCluster:
    def __init__(self) -> None:
        self.deleted = []
        self.waited = []

    def delete_pod(self, *, namespace: str, pod: str, dry_run: bool = True) -> None:
        self.deleted.append((namespace, pod, dry_run))

    def wait_replacement_ready(
        self, *, namespace: str, workload: str, timeout_s: float
    ) -> float:
        self.waited.append((namespace, workload, timeout_s))
        return 140.0


class FakeMetrics:
    def scrape(self) -> str:
        return "vllm:num_requests_running 8\n"


def test_live_recovery_defaults_to_non_destructive_dry_run() -> None:
    cluster = FakeCluster()
    receipt = run_live_recovery_probe(
        config=LiveRecoveryConfig(namespace="ai", pod="vllm-0", workload="vllm"),
        cluster=cluster,
        metrics=FakeMetrics(),
    )

    assert cluster.deleted == [("ai", "vllm-0", True)]
    assert cluster.waited == []
    assert receipt.destructive_action_executed is False
    assert receipt.replacement_ready_at_s is None


def test_destructive_mode_must_be_explicit() -> None:
    cluster = FakeCluster()
    receipt = run_live_recovery_probe(
        config=LiveRecoveryConfig(
            namespace="ai",
            pod="vllm-0",
            workload="vllm",
            dry_run=False,
        ),
        cluster=cluster,
        metrics=FakeMetrics(),
    )

    assert cluster.deleted == [("ai", "vllm-0", False)]
    assert cluster.waited == [("ai", "vllm", 300.0)]
    assert receipt.destructive_action_executed is True
    assert receipt.replacement_ready_at_s == 140.0
    assert "vllm:num_requests_running" in receipt.metrics_text

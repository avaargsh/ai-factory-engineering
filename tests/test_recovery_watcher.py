from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.outcome import MetricRule
from ai_factory_engineering.recovery_watcher import watch_slo_recovery


def histogram(ttft: float, tpot: float) -> str:
    return f"""
vllm:time_to_first_token_seconds_bucket{{le="{ttft}"}} 100
vllm:time_to_first_token_seconds_bucket{{le="+Inf"}} 100
vllm:request_time_per_output_token_seconds_bucket{{le="{tpot}"}} 100
vllm:request_time_per_output_token_seconds_bucket{{le="+Inf"}} 100
"""


class SequenceMetrics:
    def __init__(self, values: list[str]) -> None:
        self.values = iter(values)

    def scrape(self) -> str:
        return next(self.values)


RULES = (
    MetricRule("ttft_p95_ms", "lte", 200),
    MetricRule("tpot_p95_ms", "lte", 50),
)


def test_requires_consecutive_healthy_samples() -> None:
    metrics = SequenceMetrics(
        [
            histogram(0.30, 0.04),
            histogram(0.15, 0.04),
            histogram(0.25, 0.04),
            histogram(0.15, 0.04),
            histogram(0.15, 0.04),
            histogram(0.15, 0.04),
        ]
    )
    clock_values = iter(
        [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    )
    receipt = watch_slo_recovery(
        metrics=metrics,
        rules=RULES,
        timeout_s=10,
        required_consecutive_healthy=3,
        poll_interval_s=0,
        monotonic=lambda: float(next(clock_values)),
        sleep=lambda _: None,
    )

    assert receipt.recovered is True
    assert receipt.consecutive_healthy_samples == 3
    assert len(receipt.samples) == 6
    assert receipt.samples[2].status == GateStatus.FAIL


def test_timeout_returns_sample_history() -> None:
    metrics = SequenceMetrics([histogram(0.30, 0.06)] * 3)
    clock_values = iter([0, 0, 0, 1, 1, 2, 2, 3])
    receipt = watch_slo_recovery(
        metrics=metrics,
        rules=RULES,
        timeout_s=2,
        required_consecutive_healthy=2,
        poll_interval_s=0,
        monotonic=lambda: float(next(clock_values)),
        sleep=lambda _: None,
    )

    assert receipt.recovered is False
    assert receipt.recovered_at_s is None
    assert len(receipt.samples) >= 1

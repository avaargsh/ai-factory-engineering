from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from .commissioning import GateStatus
from .inference_slo import evaluate_inference_slo
from .live_recovery import MetricsSource
from .outcome import MetricRule
from .telemetry.histogram import vllm_latency_percentiles


@dataclass(frozen=True)
class RecoverySample:
    observed_at_s: float
    status: GateStatus
    measurements: dict[str, float]


@dataclass(frozen=True)
class SloRecoveryReceipt:
    recovered: bool
    recovered_at_s: float | None
    consecutive_healthy_samples: int
    samples: tuple[RecoverySample, ...]


def watch_slo_recovery(
    *,
    metrics: MetricsSource,
    rules: tuple[MetricRule, ...],
    timeout_s: float,
    required_consecutive_healthy: int = 3,
    poll_interval_s: float = 5.0,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> SloRecoveryReceipt:
    if required_consecutive_healthy < 1:
        raise ValueError("required_consecutive_healthy must be >= 1")
    if timeout_s <= 0:
        raise ValueError("timeout_s must be positive")

    started = monotonic()
    healthy = 0
    samples: list[RecoverySample] = []

    while monotonic() - started <= timeout_s:
        observed_at = monotonic()
        measurements = vllm_latency_percentiles(metrics.scrape())
        outcome = evaluate_inference_slo(measurements=measurements, rules=rules)
        samples.append(
            RecoverySample(
                observed_at_s=observed_at,
                status=outcome.status,
                measurements=measurements,
            )
        )

        if outcome.status == GateStatus.PASS:
            healthy += 1
            if healthy >= required_consecutive_healthy:
                return SloRecoveryReceipt(
                    recovered=True,
                    recovered_at_s=observed_at,
                    consecutive_healthy_samples=healthy,
                    samples=tuple(samples),
                )
        else:
            healthy = 0

        sleep(poll_interval_s)

    return SloRecoveryReceipt(
        recovered=False,
        recovered_at_s=None,
        consecutive_healthy_samples=healthy,
        samples=tuple(samples),
    )

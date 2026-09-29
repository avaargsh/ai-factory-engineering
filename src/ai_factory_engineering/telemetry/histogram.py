from __future__ import annotations

import math
import re
from dataclasses import dataclass


_BUCKET = re.compile(
    r'^(?P<name>[A-Za-z_:][A-Za-z0-9_:]*)_bucket\{(?P<labels>[^}]*)\}\s+(?P<count>[-+0-9.eE]+)$'
)
_LE = re.compile(r'(?:^|,)le="(?P<le>[^"]+)"(?:,|$)')


@dataclass(frozen=True)
class Histogram:
    buckets: tuple[tuple[float, float], ...]

    def quantile(self, q: float) -> float | None:
        if not 0 <= q <= 1:
            raise ValueError("quantile must be between 0 and 1")
        finite = [(upper, count) for upper, count in self.buckets if math.isfinite(upper)]
        total = self.buckets[-1][1] if self.buckets else 0.0
        if total <= 0 or not finite:
            return None
        rank = q * total
        previous_upper = 0.0
        previous_count = 0.0
        for upper, count in finite:
            if count >= rank:
                bucket_count = count - previous_count
                if bucket_count <= 0:
                    return upper
                fraction = (rank - previous_count) / bucket_count
                return previous_upper + fraction * (upper - previous_upper)
            previous_upper = upper
            previous_count = count
        return finite[-1][0]


def parse_prometheus_histogram(text: str, metric: str) -> Histogram:
    buckets: dict[float, float] = {}
    for raw in text.splitlines():
        match = _BUCKET.match(raw.strip())
        if not match or match.group("name") != metric:
            continue
        le_match = _LE.search(match.group("labels"))
        if not le_match:
            continue
        le = le_match.group("le")
        upper = math.inf if le == "+Inf" else float(le)
        buckets[upper] = buckets.get(upper, 0.0) + float(match.group("count"))
    return Histogram(tuple(sorted(buckets.items(), key=lambda item: item[0])))


def vllm_latency_percentiles(text: str) -> dict[str, float]:
    metrics = {
        "ttft": "vllm:time_to_first_token_seconds",
        "tpot": "vllm:request_time_per_output_token_seconds",
        "itl": "vllm:inter_token_latency_seconds",
        "queue": "vllm:request_queue_time_seconds",
        "e2e": "vllm:e2e_request_latency_seconds",
    }
    evidence: dict[str, float] = {}
    for key, metric in metrics.items():
        histogram = parse_prometheus_histogram(text, metric)
        for percentile, q in (("p50", 0.50), ("p95", 0.95), ("p99", 0.99)):
            value = histogram.quantile(q)
            if value is not None:
                evidence[f"{key}_{percentile}_ms"] = value * 1000.0
    return evidence

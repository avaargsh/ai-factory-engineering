from __future__ import annotations

import re
from dataclasses import dataclass


_SAMPLE = re.compile(
    r'^(?P<name>[A-Za-z_:][A-Za-z0-9_:]*)(?:\{[^}]*\})?\s+(?P<value>[-+0-9.eE]+)$'
)


@dataclass(frozen=True)
class VllmTelemetry:
    kv_cache_usage: float | None
    requests_running: float | None
    requests_waiting: float | None
    prompt_tokens_total: float | None
    generation_tokens_total: float | None
    prefix_cache_queries_total: float | None
    prefix_cache_hits_total: float | None

    def evidence_measurements(self) -> dict[str, float]:
        values = {
            "kv_cache_usage": self.kv_cache_usage,
            "requests_running": self.requests_running,
            "requests_waiting": self.requests_waiting,
            "prompt_tokens_total": self.prompt_tokens_total,
            "generation_tokens_total": self.generation_tokens_total,
        }
        if (
            self.prefix_cache_queries_total is not None
            and self.prefix_cache_hits_total is not None
            and self.prefix_cache_queries_total > 0
        ):
            values["prefix_cache_hit_ratio"] = (
                self.prefix_cache_hits_total / self.prefix_cache_queries_total
            )
        return {key: value for key, value in values.items() if value is not None}


def parse_vllm_prometheus(text: str) -> VllmTelemetry:
    samples: dict[str, float] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _SAMPLE.match(line)
        if match:
            samples[match.group("name")] = float(match.group("value"))

    def first(*names: str) -> float | None:
        for name in names:
            if name in samples:
                return samples[name]
        return None

    return VllmTelemetry(
        kv_cache_usage=first("vllm:kv_cache_usage_perc"),
        requests_running=first("vllm:num_requests_running"),
        requests_waiting=first("vllm:num_requests_waiting"),
        prompt_tokens_total=first("vllm:prompt_tokens_total", "vllm:prompt_tokens"),
        generation_tokens_total=first(
            "vllm:generation_tokens_total", "vllm:generation_tokens"
        ),
        prefix_cache_queries_total=first(
            "vllm:prefix_cache_queries_total", "vllm:prefix_cache_queries"
        ),
        prefix_cache_hits_total=first(
            "vllm:prefix_cache_hits_total", "vllm:prefix_cache_hits"
        ),
    )

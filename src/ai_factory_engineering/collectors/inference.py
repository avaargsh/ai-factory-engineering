from __future__ import annotations

import json


REQUIRED_METRICS = (
    "ttft_p95_ms",
    "tpot_p95_ms",
    "success_ratio",
)


def parse_inference_json(text: str) -> dict[str, float]:
    """Parse provider-neutral inference SLO JSON emitted by a benchmark command.

    Expected stdout is one JSON object containing numeric TTFT/TPOT P95 values
    and a success ratio. Benchmark-specific adapters should normalize their own
    output to this contract before invoking the collector.
    """
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("inference collector output must be a JSON object") from exc

    if not isinstance(payload, dict):
        raise ValueError("inference collector output must be a JSON object")

    metrics: dict[str, float] = {}
    for name in REQUIRED_METRICS:
        value = payload.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"inference collector requires numeric metric: {name}")
        metrics[name] = float(value)

    success_ratio = metrics["success_ratio"]
    if not 0.0 <= success_ratio <= 1.0:
        raise ValueError("success_ratio must be between 0 and 1")
    if metrics["ttft_p95_ms"] < 0 or metrics["tpot_p95_ms"] < 0:
        raise ValueError("latency metrics must be non-negative")

    return metrics

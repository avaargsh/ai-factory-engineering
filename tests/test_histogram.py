from ai_factory_engineering.telemetry.histogram import (
    parse_prometheus_histogram,
    vllm_latency_percentiles,
)


TTFT = """
vllm:time_to_first_token_seconds_bucket{le="0.1",model_name="Qwen"} 50
vllm:time_to_first_token_seconds_bucket{le="0.2",model_name="Qwen"} 90
vllm:time_to_first_token_seconds_bucket{le="0.5",model_name="Qwen"} 100
vllm:time_to_first_token_seconds_bucket{le="+Inf",model_name="Qwen"} 100
"""


def test_histogram_quantile_interpolates_cumulative_buckets() -> None:
    histogram = parse_prometheus_histogram(
        TTFT, "vllm:time_to_first_token_seconds"
    )
    assert histogram.quantile(0.50) == 0.1
    assert round(histogram.quantile(0.95), 3) == 0.35


def test_vllm_latency_evidence_keeps_tpot_and_itl_distinct() -> None:
    text = TTFT + """
vllm:request_time_per_output_token_seconds_bucket{le="0.02",model_name="Qwen"} 80
vllm:request_time_per_output_token_seconds_bucket{le="0.05",model_name="Qwen"} 100
vllm:request_time_per_output_token_seconds_bucket{le="+Inf",model_name="Qwen"} 100
vllm:inter_token_latency_seconds_bucket{le="0.01",model_name="Qwen"} 60
vllm:inter_token_latency_seconds_bucket{le="0.03",model_name="Qwen"} 100
vllm:inter_token_latency_seconds_bucket{le="+Inf",model_name="Qwen"} 100
"""
    evidence = vllm_latency_percentiles(text)

    assert evidence["ttft_p50_ms"] == 100.0
    assert round(evidence["ttft_p95_ms"], 1) == 350.0
    assert "tpot_p95_ms" in evidence
    assert "itl_p95_ms" in evidence
    assert evidence["tpot_p95_ms"] != evidence["itl_p95_ms"]


def test_empty_histogram_produces_no_percentile() -> None:
    assert parse_prometheus_histogram("", "x").quantile(0.95) is None

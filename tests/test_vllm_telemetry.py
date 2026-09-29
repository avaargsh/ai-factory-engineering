from ai_factory_engineering.telemetry.vllm import parse_vllm_prometheus


FIXTURE = """
# TYPE vllm:kv_cache_usage_perc gauge
vllm:kv_cache_usage_perc{model_name="Qwen"} 0.75
vllm:num_requests_running{model_name="Qwen"} 8
vllm:num_requests_waiting{model_name="Qwen"} 3
vllm:prompt_tokens_total{model_name="Qwen"} 12000
vllm:generation_tokens_total{model_name="Qwen"} 6000
vllm:prefix_cache_queries_total{model_name="Qwen"} 4000
vllm:prefix_cache_hits_total{model_name="Qwen"} 3000
"""


def test_vllm_metrics_normalize_into_inference_evidence() -> None:
    telemetry = parse_vllm_prometheus(FIXTURE)
    measurements = telemetry.evidence_measurements()

    assert measurements["kv_cache_usage"] == 0.75
    assert measurements["requests_running"] == 8
    assert measurements["requests_waiting"] == 3
    assert measurements["prompt_tokens_total"] == 12000
    assert measurements["generation_tokens_total"] == 6000
    assert measurements["prefix_cache_hit_ratio"] == 0.75


def test_zero_prefix_queries_do_not_invent_hit_ratio() -> None:
    telemetry = parse_vllm_prometheus(
        "vllm:prefix_cache_queries_total 0\n"
        "vllm:prefix_cache_hits_total 0\n"
    )
    assert "prefix_cache_hit_ratio" not in telemetry.evidence_measurements()

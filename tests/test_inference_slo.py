from pathlib import Path

from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.inference_slo import (
    evaluate_inference_slo,
    load_inference_slo_rules,
)
from ai_factory_engineering.telemetry.histogram import vllm_latency_percentiles


ROOT = Path(__file__).resolve().parents[1]


METRICS = """
vllm:time_to_first_token_seconds_bucket{le="0.1"} 50
vllm:time_to_first_token_seconds_bucket{le="0.2"} 100
vllm:time_to_first_token_seconds_bucket{le="+Inf"} 100
vllm:request_time_per_output_token_seconds_bucket{le="0.02"} 50
vllm:request_time_per_output_token_seconds_bucket{le="0.05"} 100
vllm:request_time_per_output_token_seconds_bucket{le="+Inf"} 100
"""


def test_vllm_histograms_flow_into_slo_pass() -> None:
    measurements = vllm_latency_percentiles(METRICS)
    rules = load_inference_slo_rules(
        ROOT / "acceptance/examples/inference-interactive-slo.json"
    )

    outcome = evaluate_inference_slo(measurements=measurements, rules=rules)

    assert outcome.status == GateStatus.PASS
    assert outcome.evidence_complete is True


def test_slo_violation_fails() -> None:
    rules = load_inference_slo_rules(
        ROOT / "acceptance/examples/inference-interactive-slo.json"
    )
    outcome = evaluate_inference_slo(
        measurements={"ttft_p95_ms": 250, "tpot_p95_ms": 40},
        rules=rules,
    )
    assert outcome.status == GateStatus.FAIL
    assert "ttft_p95_ms" in outcome.reason


def test_missing_percentile_fails_closed() -> None:
    rules = load_inference_slo_rules(
        ROOT / "acceptance/examples/inference-interactive-slo.json"
    )
    outcome = evaluate_inference_slo(
        measurements={"ttft_p95_ms": 150},
        rules=rules,
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False

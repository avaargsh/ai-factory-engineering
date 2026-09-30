import pytest

from ai_factory_engineering.collectors.inference import parse_inference_json


def test_inference_json_collector_parses_canonical_metrics():
    assert parse_inference_json(
        '{"ttft_p95_ms": 120.5, "tpot_p95_ms": 31.2, "success_ratio": 0.995}'
    ) == {
        "ttft_p95_ms": 120.5,
        "tpot_p95_ms": 31.2,
        "success_ratio": 0.995,
    }


@pytest.mark.parametrize(
    "payload",
    [
        "{}",
        '{"ttft_p95_ms": 1, "tpot_p95_ms": 2}',
        '{"ttft_p95_ms": -1, "tpot_p95_ms": 2, "success_ratio": 1}',
        '{"ttft_p95_ms": 1, "tpot_p95_ms": 2, "success_ratio": 1.1}',
    ],
)
def test_inference_json_collector_fails_closed(payload):
    with pytest.raises(ValueError):
        parse_inference_json(payload)

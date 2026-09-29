from __future__ import annotations

from dataclasses import dataclass

from .commissioning import GateStatus, TestOutcome


@dataclass(frozen=True)
class InferenceSlo:
    max_ttft_ms: float
    max_tpot_ms: float


@dataclass(frozen=True)
class InferenceRequestObservation:
    success: bool
    ttft_ms: float
    tpot_ms: float
    output_tokens: int


def summarize_inference_goodput(
    observations: tuple[InferenceRequestObservation, ...],
    slo: InferenceSlo,
) -> dict[str, float]:
    if not observations:
        return {}
    successful = [item for item in observations if item.success]
    compliant = [
        item
        for item in successful
        if item.ttft_ms <= slo.max_ttft_ms and item.tpot_ms <= slo.max_tpot_ms
    ]
    return {
        "request_success_ratio": len(successful) / len(observations),
        "slo_compliant_request_ratio": len(compliant) / len(observations),
        "slo_compliant_output_tokens": float(
            sum(item.output_tokens for item in compliant)
        ),
    }


def evaluate_inference_correctness(
    *,
    runtime_identity_recorded: bool,
    model_identity_recorded: bool,
    load_profile_recorded: bool,
    observations: tuple[InferenceRequestObservation, ...],
) -> TestOutcome:
    if not runtime_identity_recorded:
        return TestOutcome("inference-runtime", GateStatus.FAIL, False, "missing runtime identity")
    if not model_identity_recorded:
        return TestOutcome("inference-runtime", GateStatus.FAIL, False, "missing model identity")
    if not load_profile_recorded:
        return TestOutcome("inference-runtime", GateStatus.FAIL, False, "missing load profile")
    if not observations:
        return TestOutcome("inference-runtime", GateStatus.FAIL, False, "missing request observations")
    return TestOutcome("inference-runtime", GateStatus.PASS, True)

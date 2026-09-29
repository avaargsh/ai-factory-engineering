from ai_factory_engineering.commissioning import GateStatus
from ai_factory_engineering.inference import (
    InferenceRequestObservation,
    InferenceSlo,
    evaluate_inference_correctness,
    summarize_inference_goodput,
)


def test_goodput_counts_only_successful_slo_compliant_requests() -> None:
    observations = (
        InferenceRequestObservation(True, 100, 20, 100),
        InferenceRequestObservation(True, 300, 20, 200),
        InferenceRequestObservation(True, 100, 80, 300),
        InferenceRequestObservation(False, 0, 0, 400),
    )
    summary = summarize_inference_goodput(
        observations,
        InferenceSlo(max_ttft_ms=200, max_tpot_ms=50),
    )

    assert summary["request_success_ratio"] == 0.75
    assert summary["slo_compliant_request_ratio"] == 0.25
    assert summary["slo_compliant_output_tokens"] == 100.0


def test_missing_load_profile_fails_closed() -> None:
    outcome = evaluate_inference_correctness(
        runtime_identity_recorded=True,
        model_identity_recorded=True,
        load_profile_recorded=False,
        observations=(InferenceRequestObservation(True, 100, 20, 100),),
    )
    assert outcome.status == GateStatus.FAIL
    assert outcome.evidence_complete is False


def test_complete_inference_evidence_passes_correctness_gate() -> None:
    outcome = evaluate_inference_correctness(
        runtime_identity_recorded=True,
        model_identity_recorded=True,
        load_profile_recorded=True,
        observations=(InferenceRequestObservation(True, 100, 20, 100),),
    )
    assert outcome.status == GateStatus.PASS

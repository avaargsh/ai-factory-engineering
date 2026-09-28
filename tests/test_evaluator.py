from pathlib import Path

from ai_factory_engineering.acceptance import (
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)
from ai_factory_engineering.evaluator import evaluate_acceptance
from ai_factory_engineering.report import render_acceptance_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_example_bundle_passes_example_test() -> None:
    test_spec = load_and_validate_test_spec(
        ROOT / "acceptance/examples/fabric-nccl.json"
    )
    evidence = load_and_validate_evidence_bundle(
        ROOT / "acceptance/examples/fabric-nccl-evidence.json"
    )

    result = evaluate_acceptance(test_spec, evidence)

    assert result.passed is True
    assert all(item.passed for item in result.metrics)
    assert all(
        item.present
        for item in result.evidence
        if item.required
    )

    report = render_acceptance_markdown(result)
    assert "**Result:** PASS" in report
    assert "bus_bandwidth_gbps" in report


def test_missing_required_evidence_fails() -> None:
    test_spec = {
        "metadata": {"id": "T-1"},
        "spec": {
            "metrics": [
                {"name": "x", "op": "gte", "threshold": 1}
            ],
            "evidence": [
                {"source": "raw-output", "required": True}
            ],
        },
    }
    bundle = {
        "metadata": {"bundleId": "B-1"},
        "testRef": "T-1",
        "measurements": {"x": 2},
        "artifacts": [],
    }

    result = evaluate_acceptance(test_spec, bundle)

    assert result.passed is False
    assert result.evidence[0].present is False


def test_missing_measurement_fails_closed() -> None:
    test_spec = {
        "metadata": {"id": "T-1"},
        "spec": {
            "metrics": [
                {"name": "x", "op": "gte", "threshold": 1}
            ],
            "evidence": [],
        },
    }
    bundle = {
        "metadata": {"bundleId": "B-1"},
        "testRef": "T-1",
        "measurements": {},
        "artifacts": [],
    }

    result = evaluate_acceptance(test_spec, bundle)

    assert result.passed is False
    assert result.metrics[0].reason == "MISSING_MEASUREMENT"

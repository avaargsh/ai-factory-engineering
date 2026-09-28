from pathlib import Path

from ai_factory_engineering.acceptance_run import (
    evaluate_acceptance_run,
    load_acceptance_run_manifest,
)
from ai_factory_engineering.run_report import (
    render_acceptance_run_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def test_acceptance_run_manifest_passes() -> None:
    run_id, cases = load_acceptance_run_manifest(
        ROOT / "acceptance/examples/run.json"
    )
    result = evaluate_acceptance_run(
        run_id=run_id,
        cases=cases,
    )

    assert result.passed is True
    assert result.total == 1
    assert result.passed_count == 1

    report = render_acceptance_run_markdown(
        result
    )
    assert "**Result:** PASS" in report
    assert "FAB-NCCL-001" in report


def test_any_failed_case_fails_whole_run() -> None:
    passing_test = {
        "metadata": {
            "id": "T-1",
            "layer": "fabric",
        },
        "spec": {
            "metrics": [
                {
                    "name": "x",
                    "op": "gte",
                    "threshold": 1,
                }
            ],
            "evidence": [],
        },
    }
    passing_bundle = {
        "metadata": {"bundleId": "B-1"},
        "testRef": "T-1",
        "measurements": {"x": 2},
        "artifacts": [],
    }

    failing_test = {
        "metadata": {
            "id": "T-2",
            "layer": "runtime",
        },
        "spec": {
            "metrics": [
                {
                    "name": "y",
                    "op": "lte",
                    "threshold": 10,
                }
            ],
            "evidence": [],
        },
    }
    failing_bundle = {
        "metadata": {"bundleId": "B-2"},
        "testRef": "T-2",
        "measurements": {"y": 20},
        "artifacts": [],
    }

    result = evaluate_acceptance_run(
        run_id="run-1",
        cases=[
            (passing_test, passing_bundle),
            (failing_test, failing_bundle),
        ],
    )

    assert result.passed is False
    assert result.passed_count == 1
    assert result.failed_count == 1

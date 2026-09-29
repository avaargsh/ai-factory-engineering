from pathlib import Path

from ai_factory_engineering.acceptance import load_and_validate_test_spec
from ai_factory_engineering.collector_execution import execute_collector_to_evidence
from ai_factory_engineering.evaluator import evaluate_acceptance
from ai_factory_engineering.outcome_adapter import acceptance_result_to_outcome
from ai_factory_engineering.runner import CommandResult
from ai_factory_engineering.commissioning import GateStatus

ROOT = Path(__file__).resolve().parents[1]


class FixtureRunner:
    def run(self, command, *, timeout_seconds=60.0):
        raw = (ROOT / "tests/fixtures/dcgm.csv").read_text()
        return CommandResult(tuple(command), 0, raw, "")


def test_dcgm_evidence_drives_executable_acceptance_and_gate_outcome(tmp_path):
    bundle = execute_collector_to_evidence(
        collector="dcgm", command=["dcgmi", "diag"], output_dir=tmp_path,
        bundle_id="dcgm-live-001", test_ref="dcgm-health", topology_ref="golden-factory-576",
        runner=FixtureRunner(),
    )
    spec = load_and_validate_test_spec(ROOT / "acceptance/tests/dcgm-health.json")
    result = evaluate_acceptance(spec, bundle)
    outcome = acceptance_result_to_outcome(result)
    assert result.passed is True
    assert outcome.status == GateStatus.PASS

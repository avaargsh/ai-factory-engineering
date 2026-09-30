from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .baseline_binding import bind_typed_baselines
from .collector_execution import execute_collector_to_evidence
from .commissioning import GateDecision, GateSpec, TestOutcome, evaluate_plan
from .evaluator import AcceptanceResult, evaluate_acceptance
from .outcome_adapter import acceptance_result_to_outcome
from .runner import Runner
from .typed_baseline import TypedBaseline


@dataclass(frozen=True)
class LiveTest:
    collector: str
    command: tuple[str, ...]
    test_spec: dict[str, Any]
    baselines: tuple[TypedBaseline, ...]
    gate_id: str
    bundle_id: str


@dataclass(frozen=True)
class LiveCommissioningResult:
    evidence: tuple[dict[str, Any], ...]
    acceptance: tuple[AcceptanceResult, ...]
    outcomes: tuple[TestOutcome, ...]
    gates: tuple[GateDecision, ...]


def run_live_commissioning(*, tests: Sequence[LiveTest], gates: Sequence[GateSpec], runner: Runner, output_dir: str | Path, topology_ref: str) -> LiveCommissioningResult:
    evidence=[]; acceptance=[]; outcomes=[]; by_gate: dict[str,list[TestOutcome]]={}
    for test in tests:
        executable = (
            bind_typed_baselines(test.test_spec, test.baselines)
            if test.baselines
            else test.test_spec
        )
        bundle = execute_collector_to_evidence(collector=test.collector, command=test.command, output_dir=output_dir, bundle_id=test.bundle_id, test_ref=executable["metadata"]["id"], topology_ref=topology_ref, runner=runner)
        result = evaluate_acceptance(executable, bundle)
        outcome = acceptance_result_to_outcome(result)
        evidence.append(bundle); acceptance.append(result); outcomes.append(outcome)
        by_gate.setdefault(test.gate_id, []).append(outcome)
    decisions=evaluate_plan(gates, by_gate)
    return LiveCommissioningResult(tuple(evidence), tuple(acceptance), tuple(outcomes), decisions)

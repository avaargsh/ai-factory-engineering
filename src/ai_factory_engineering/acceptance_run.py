from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .acceptance import (
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)
from .evaluator import AcceptanceResult, evaluate_acceptance


@dataclass(frozen=True)
class AcceptanceCaseResult:
    layer: str
    result: AcceptanceResult


@dataclass(frozen=True)
class AcceptanceRunResult:
    run_id: str
    passed: bool
    total: int
    passed_count: int
    failed_count: int
    cases: tuple[AcceptanceCaseResult, ...]


def evaluate_acceptance_run(
    *,
    run_id: str,
    cases: Sequence[
        tuple[
            dict[str, Any],
            dict[str, Any],
        ]
    ],
) -> AcceptanceRunResult:
    if not cases:
        raise ValueError(
            "acceptance run requires at least one case"
        )

    results: list[AcceptanceCaseResult] = []

    for test_spec, evidence_bundle in cases:
        results.append(
            AcceptanceCaseResult(
                layer=test_spec["metadata"]["layer"],
                result=evaluate_acceptance(
                    test_spec,
                    evidence_bundle,
                ),
            )
        )

    passed_count = sum(
        1
        for item in results
        if item.result.passed
    )
    failed_count = len(results) - passed_count

    return AcceptanceRunResult(
        run_id=run_id,
        passed=failed_count == 0,
        total=len(results),
        passed_count=passed_count,
        failed_count=failed_count,
        cases=tuple(results),
    )


def load_acceptance_run_manifest(
    path: str | Path,
) -> tuple[
    str,
    list[
        tuple[
            dict[str, Any],
            dict[str, Any],
        ]
    ],
]:
    manifest_path = Path(path)
    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    run_id = str(manifest["runId"])
    root = manifest_path.parent
    cases = []

    for item in manifest["cases"]:
        test_path = (
            root / item["test"]
        ).resolve()
        evidence_path = (
            root / item["evidence"]
        ).resolve()

        cases.append(
            (
                load_and_validate_test_spec(
                    test_path
                ),
                load_and_validate_evidence_bundle(
                    evidence_path
                ),
            )
        )

    return run_id, cases

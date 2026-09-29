from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .acceptance import load_and_validate_evidence_bundle
from .commissioning import GateStatus, TestOutcome


@dataclass(frozen=True)
class CollectedEvidence:
    test_id: str
    bundle: Mapping[str, Any]
    source: str


def ingest_evidence_bundles(
    paths: Iterable[str | Path],
) -> tuple[CollectedEvidence, ...]:
    collected = []
    for path in paths:
        bundle = load_and_validate_evidence_bundle(path)
        collected.append(
            CollectedEvidence(
                test_id=str(bundle["testRef"]),
                bundle=bundle,
                source=str(path),
            )
        )
    return tuple(collected)


def evidence_to_outcome(item: CollectedEvidence) -> TestOutcome:
    result = item.bundle.get("result")
    if not isinstance(result, Mapping) or "passed" not in result:
        return TestOutcome(
            test_id=item.test_id,
            status=GateStatus.PENDING,
            evidence_complete=False,
            reason="validated EvidenceBundle has no collector result",
        )

    passed = bool(result["passed"])
    return TestOutcome(
        test_id=item.test_id,
        status=GateStatus.PASS if passed else GateStatus.FAIL,
        evidence_complete=True,
        reason=str(result.get("notes", "")),
    )

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
        test_id = str(
            bundle.get("testId")
            or bundle.get("test_id")
            or bundle.get("metadata", {}).get("testId")
            or Path(path).stem
        )
        collected.append(
            CollectedEvidence(test_id=test_id, bundle=bundle, source=str(path))
        )
    return tuple(collected)


def evidence_to_outcome(
    item: CollectedEvidence,
    *,
    status: GateStatus,
) -> TestOutcome:
    return TestOutcome(
        test_id=item.test_id,
        status=status,
        evidence_complete=True,
        reason=f"validated EvidenceBundle from {item.source}",
    )

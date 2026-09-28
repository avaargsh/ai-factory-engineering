from pathlib import Path

import pytest

from ai_factory_engineering.acceptance import (
    AcceptanceValidationError,
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)


ROOT = Path(__file__).resolve().parents[1]


def test_example_acceptance_spec_validates() -> None:
    doc = load_and_validate_test_spec(
        ROOT / "acceptance/examples/fabric-nccl.json"
    )
    assert doc["metadata"]["id"] == "FAB-NCCL-001"


def test_example_evidence_bundle_validates() -> None:
    doc = load_and_validate_evidence_bundle(
        ROOT / "acceptance/examples/fabric-nccl-evidence.json"
    )
    assert doc["testRef"] == "FAB-NCCL-001"


def test_invalid_acceptance_spec_fails(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(
        '{"apiVersion":"aifactory.engineering/v1alpha1","kind":"AcceptanceTest"}',
        encoding="utf-8",
    )

    with pytest.raises(AcceptanceValidationError):
        load_and_validate_test_spec(path)

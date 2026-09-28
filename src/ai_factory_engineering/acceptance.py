from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class AcceptanceValidationError(ValueError):
    pass


def _schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _validate(document: dict[str, Any], schema_name: str) -> dict[str, Any]:
    schema = _load_json(_schema_dir() / schema_name)
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.path),
    )

    if errors:
        details = "; ".join(
            f"{'/'.join(str(item) for item in error.path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )
        raise AcceptanceValidationError(details)

    return document


def load_and_validate_test_spec(path: str | Path) -> dict[str, Any]:
    return _validate(
        _load_json(path),
        "acceptance-test.schema.json",
    )


def load_and_validate_evidence_bundle(path: str | Path) -> dict[str, Any]:
    return _validate(
        _load_json(path),
        "evidence-bundle.schema.json",
    )

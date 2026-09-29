from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .outcome import MetricRule


@dataclass(frozen=True)
class TypedBaseline:
    id: str
    metric: str
    operator: str
    value: float
    unit: str
    scope: str
    reference: str | None = None
    source: str | None = None

    def to_rule(self) -> MetricRule:
        return MetricRule(self.metric, self.operator, self.value)


def load_typed_baseline(path: str | Path) -> TypedBaseline:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ("id", "metric", "operator", "value", "unit", "scope")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"baseline missing field: {missing[0]}")
    if payload["operator"] not in {"eq", "lte", "gte", "lt", "gt"}:
        raise ValueError(f"unsupported baseline operator: {payload['operator']}")
    if not isinstance(payload["value"], (int, float)):
        raise ValueError("baseline value must be numeric")
    for key in ("id", "metric", "unit", "scope"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError(f"baseline {key} must be non-empty")
    return TypedBaseline(
        id=payload["id"],
        metric=payload["metric"],
        operator=payload["operator"],
        value=float(payload["value"]),
        unit=payload["unit"],
        scope=payload["scope"],
        reference=payload.get("reference"),
        source=payload.get("source"),
    )

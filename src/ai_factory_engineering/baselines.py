from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .outcome import MetricRule


@dataclass(frozen=True)
class AcceptanceBaseline:
    test_id: str
    metric: str
    rule: MetricRule | None
    evidence: str

    @property
    def is_declared(self) -> bool:
        return self.rule is not None


def _parse_threshold(metric: str, threshold: str) -> MetricRule | None:
    value = threshold.strip()
    if not value or value.upper() == "TBD":
        return None
    try:
        numeric = float(value)
    except ValueError as exc:
        raise ValueError(
            f"unsupported threshold for {metric}: {threshold}"
        ) from exc

    # The current acceptance matrix only declares zero-tolerance health
    # counters numerically. Rich bandwidth/SLO baselines remain TBD and must
    # not be guessed here.
    if numeric == 0:
        return MetricRule(metric=metric, op="eq", value=0.0)
    raise ValueError(
        f"numeric threshold requires explicit operator semantics: {metric}={threshold}"
    )


def load_acceptance_baselines(path: str | Path) -> dict[str, AcceptanceBaseline]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        baselines: dict[str, AcceptanceBaseline] = {}
        for row in rows:
            test_id = row["test_id"].strip()
            if not test_id:
                raise ValueError("acceptance matrix contains empty test_id")
            if test_id in baselines:
                raise ValueError(f"duplicate acceptance test_id: {test_id}")
            metric = row["metric"].strip()
            baselines[test_id] = AcceptanceBaseline(
                test_id=test_id,
                metric=metric,
                rule=_parse_threshold(metric, row["threshold"]),
                evidence=row["evidence"].strip(),
            )
    return baselines


def unresolved_baselines(
    baselines: dict[str, AcceptanceBaseline],
) -> tuple[str, ...]:
    return tuple(
        test_id
        for test_id, baseline in baselines.items()
        if not baseline.is_declared
    )

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from .typed_baseline import TypedBaseline


class BaselineBindingError(ValueError):
    pass


def bind_typed_baselines(test_spec: dict[str, Any], baselines: Iterable[TypedBaseline]) -> dict[str, Any]:
    """Materialize external typed baselines into an executable AcceptanceTest."""
    materialized = deepcopy(test_spec)
    metrics = materialized["spec"]["metrics"]
    by_name = {metric["name"]: metric for metric in metrics}

    seen: set[str] = set()
    for baseline in baselines:
        if baseline.metric in seen:
            raise BaselineBindingError(f"duplicate baseline metric: {baseline.metric}")
        seen.add(baseline.metric)
        metric = by_name.get(baseline.metric)
        if metric is None:
            raise BaselineBindingError(f"baseline metric not declared by test: {baseline.metric}")
        metric["op"] = baseline.operator
        metric["threshold"] = baseline.value
        metric["unit"] = baseline.unit

    missing = [metric["name"] for metric in metrics if metric["name"] not in seen]
    if missing:
        raise BaselineBindingError(f"missing baseline for metric: {missing[0]}")
    return materialized

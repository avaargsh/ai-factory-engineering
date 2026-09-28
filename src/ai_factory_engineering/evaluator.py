from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricResult:
    name: str
    op: str
    threshold: float
    actual: float | None
    passed: bool
    reason: str


@dataclass(frozen=True)
class EvidenceRequirementResult:
    source: str
    present: bool
    required: bool


@dataclass(frozen=True)
class AcceptanceResult:
    test_id: str
    bundle_id: str
    passed: bool
    metrics: tuple[MetricResult, ...]
    evidence: tuple[EvidenceRequirementResult, ...]


def _compare(actual: float, op: str, threshold: float) -> bool:
    if op == "lt":
        return actual < threshold
    if op == "lte":
        return actual <= threshold
    if op == "gt":
        return actual > threshold
    if op == "gte":
        return actual >= threshold
    if op == "eq":
        return actual == threshold
    raise ValueError(f"unsupported operator: {op}")


def evaluate_acceptance(
    test_spec: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> AcceptanceResult:
    test_id = test_spec["metadata"]["id"]
    bundle_id = evidence_bundle["metadata"]["bundleId"]

    if evidence_bundle["testRef"] != test_id:
        raise ValueError(
            f"EvidenceBundle testRef {evidence_bundle['testRef']!r} "
            f"does not match AcceptanceTest {test_id!r}"
        )

    measurements = dict(evidence_bundle.get("measurements", {}))
    metric_results: list[MetricResult] = []

    for metric in test_spec["spec"]["metrics"]:
        name = metric["name"]
        op = metric["op"]
        threshold = float(metric["threshold"])

        if name not in measurements:
            metric_results.append(
                MetricResult(
                    name=name,
                    op=op,
                    threshold=threshold,
                    actual=None,
                    passed=False,
                    reason="MISSING_MEASUREMENT",
                )
            )
            continue

        actual = float(measurements[name])
        passed = _compare(actual, op, threshold)
        metric_results.append(
            MetricResult(
                name=name,
                op=op,
                threshold=threshold,
                actual=actual,
                passed=passed,
                reason="PASS" if passed else "THRESHOLD_FAILED",
            )
        )

    artifact_types = {
        artifact["type"]
        for artifact in evidence_bundle.get("artifacts", [])
    }

    evidence_results = tuple(
        EvidenceRequirementResult(
            source=requirement["source"],
            present=requirement["source"] in artifact_types,
            required=bool(requirement["required"]),
        )
        for requirement in test_spec["spec"]["evidence"]
    )

    metrics_pass = all(item.passed for item in metric_results)
    evidence_pass = all(
        item.present or not item.required
        for item in evidence_results
    )

    return AcceptanceResult(
        test_id=test_id,
        bundle_id=bundle_id,
        passed=metrics_pass and evidence_pass,
        metrics=tuple(metric_results),
        evidence=evidence_results,
    )

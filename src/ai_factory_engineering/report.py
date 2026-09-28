from __future__ import annotations

from .evaluator import AcceptanceResult


def render_acceptance_markdown(result: AcceptanceResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [
        f"# Acceptance Report — {result.test_id}",
        "",
        f"**Bundle:** {result.bundle_id}",
        f"**Result:** {status}",
        "",
        "## Metrics",
        "",
        "| Metric | Actual | Operator | Threshold | Result |",
        "| --- | ---: | :---: | ---: | :---: |",
    ]

    for item in result.metrics:
        actual = "missing" if item.actual is None else str(item.actual)
        lines.append(
            f"| {item.name} | {actual} | {item.op} | "
            f"{item.threshold} | {'PASS' if item.passed else 'FAIL'} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Requirements",
            "",
            "| Source | Required | Present |",
            "| --- | :---: | :---: |",
        ]
    )

    for item in result.evidence:
        lines.append(
            f"| {item.source} | "
            f"{'yes' if item.required else 'no'} | "
            f"{'yes' if item.present else 'no'} |"
        )

    return "\n".join(lines) + "\n"

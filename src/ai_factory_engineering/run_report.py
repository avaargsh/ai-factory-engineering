from __future__ import annotations

from .acceptance_run import AcceptanceRunResult


def render_acceptance_run_markdown(
    result: AcceptanceRunResult,
) -> str:
    status = "PASS" if result.passed else "FAIL"

    lines = [
        f"# Acceptance Run — {result.run_id}",
        "",
        f"**Result:** {status}",
        f"**Tests:** {result.total}",
        f"**Passed:** {result.passed_count}",
        f"**Failed:** {result.failed_count}",
        "",
        "## Test Results",
        "",
        "| Test | Layer | Result |",
        "| --- | --- | :---: |",
    ]

    for item in result.cases:
        lines.append(
            f"| {item.result.test_id} | "
            f"{item.layer} | "
            f"{'PASS' if item.result.passed else 'FAIL'} |"
        )

    return "\n".join(lines) + "\n"

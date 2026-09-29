from .commissioning import GateDecision


def render_gate_report(plan_id: str, decisions: tuple[GateDecision, ...]) -> str:
    lines = [f"# Commissioning Gate Report: {plan_id}", "", "| Gate | Status | Reasons |", "|---|---|---|"]
    for decision in decisions:
        reasons = "; ".join(decision.reasons) if decision.reasons else "-"
        lines.append(f"| {decision.gate_id} | {decision.status.value} | {reasons} |")
    return "\n".join(lines) + "\n"

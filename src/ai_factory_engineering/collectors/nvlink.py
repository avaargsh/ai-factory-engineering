from __future__ import annotations

import re


_LINK = re.compile(
    r"GPU(?P<gpu>\d+)\s+Link\s+(?P<link>\d+)\s*:\s*"
    r"(?P<state>Active|Inactive)\s+"
    r"tx_errors\s+(?P<tx>\d+)\s+"
    r"rx_errors\s+(?P<rx>\d+)",
    re.I,
)


def parse_nvlink_status(text: str) -> dict[str, float]:
    total = active = tx = rx = 0
    for line in text.splitlines():
        match = _LINK.search(line)
        if not match:
            continue
        total += 1
        active += match.group("state").lower() == "active"
        tx += int(match.group("tx"))
        rx += int(match.group("rx"))
    if not total:
        return {}
    return {
        "nvlink_links_total": float(total),
        "nvlink_links_active": float(active),
        "nvlink_tx_errors": float(tx),
        "nvlink_rx_errors": float(rx),
    }

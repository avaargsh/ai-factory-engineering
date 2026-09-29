from __future__ import annotations

import re

_COUNTER = re.compile(r"^\s*([A-Za-z0-9_]+)\s*[:=]\s*([0-9]+)\s*$")


def parse_rdma_counters(text: str) -> dict[str, float]:
    """Parse normalized key:value RDMA/RoCE counters into observations."""
    result={}
    for line in text.splitlines():
        match=_COUNTER.match(line)
        if match:
            result[match.group(1)]=float(match.group(2))
    return result


def normalize_rdma(counters: dict[str,float]) -> dict[str,float]:
    aliases={"port_xmit_discards":"rdma_tx_discards","port_rcv_errors":"rdma_rx_errors","np_ecn_marked_roce_packets":"roce_ecn_marked","np_cnp_sent":"roce_cnp_sent","rx_prio3_pause_duration":"pfc_rx_pause_duration"}
    return {aliases.get(k,k):v for k,v in counters.items()}

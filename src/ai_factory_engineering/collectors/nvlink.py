from __future__ import annotations
import re

_LINK=re.compile(r"GPU(?P<gpu>\d+)\s+Link\s+(?P<link>\d+)\s*:\s*(?P<state>Active|Inactive).*?(?P<tx>\d+)\s+(?P<rx>\d+)",re.I)

def parse_nvlink_status(text:str)->dict[str,float]:
    total=active=tx=rx=0
    for line in text.splitlines():
        m=_LINK.search(line)
        if not m: continue
        total+=1; active+=m.group("state").lower()=="active"; tx+=int(m.group("tx")); rx+=int(m.group("rx"))
    return {"nvlink_links_total":float(total),"nvlink_links_active":float(active),"nvlink_tx_errors":float(tx),"nvlink_rx_errors":float(rx)} if total else {}

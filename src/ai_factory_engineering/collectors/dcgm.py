from __future__ import annotations
import csv, io

def parse_dcgm_csv(text:str)->dict[str,float]:
    """Parse a small normalized DCGM CSV export into aggregate observations."""
    rows=list(csv.DictReader(io.StringIO(text)))
    if not rows: return {}
    def vals(k): return [float(r[k]) for r in rows if r.get(k) not in (None,"")]
    out={}
    for src,dst,fn in [("gpu_temp","gpu_temp_max_c",max),("power_w","gpu_power_max_w",max),("sm_clock_mhz","gpu_sm_clock_min_mhz",min),("ecc_uncorrected","gpu_ecc_uncorrected_total",sum)]:
        v=vals(src)
        if v: out[dst]=fn(v)
    return out

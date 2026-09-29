from pathlib import Path
from ai_factory_engineering.collectors.dcgm import parse_dcgm_csv
from ai_factory_engineering.collectors.nvlink import parse_nvlink_status
FIX=Path(__file__).parent/"fixtures"

def test_dcgm_observations():
    m=parse_dcgm_csv((FIX/"dcgm.csv").read_text())
    assert m["gpu_temp_max_c"]==63
    assert m["gpu_sm_clock_min_mhz"]==1815
    assert m["gpu_ecc_uncorrected_total"]==0

def test_nvlink_observations_include_degraded_link():
    m=parse_nvlink_status((FIX/"nvlink.txt").read_text())
    assert m["nvlink_links_total"]==4
    assert m["nvlink_links_active"]==3
    assert m["nvlink_tx_errors"]==1

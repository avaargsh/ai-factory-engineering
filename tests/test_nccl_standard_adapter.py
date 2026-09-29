from pathlib import Path
from ai_factory_engineering.collectors.nccl import parse_nccl_tests, summarize_nccl
FIX=Path(__file__).parent/"fixtures"

def test_standard_nccl_perf_row_preserves_oop_and_inplace_groups():
    samples=parse_nccl_tests((FIX/"nccl_all_reduce_standard.txt").read_text())
    metrics=summarize_nccl(samples)
    assert metrics["nccl_busbw_gbps"] == 112.35
    assert metrics["nccl_inplace_busbw_gbps"] == 111.2
    assert metrics["nccl_wrong_total"] == 0.0

def test_inplace_wrong_is_included_in_correctness_total():
    raw="8388608 2097152 float sum -1 75 111 112 0 76 110 111 3\n"
    assert summarize_nccl(parse_nccl_tests(raw))["nccl_wrong_total"] == 3.0

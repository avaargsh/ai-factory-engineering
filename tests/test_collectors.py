from pathlib import Path
from ai_factory_engineering.collectors.nccl import parse_nccl_tests, summarize_nccl
from ai_factory_engineering.collectors.rdma import normalize_rdma, parse_rdma_counters
from ai_factory_engineering.evidence import build_evidence_bundle

FIX=Path(__file__).parent/"fixtures"

def test_nccl_parser_extracts_largest_message_bandwidth():
    samples=parse_nccl_tests((FIX/"nccl_all_reduce.txt").read_text())
    metrics=summarize_nccl(samples)
    assert metrics["nccl_busbw_gbps"] == 112.35
    assert metrics["nccl_largest_message_bytes"] == 8388608.0


def test_rdma_counter_normalization():
    counters=normalize_rdma(parse_rdma_counters((FIX/"rdma_counters.txt").read_text()))
    assert counters["rdma_tx_discards"] == 0
    assert counters["roce_ecn_marked"] == 128
    assert counters["pfc_rx_pause_duration"] == 2048


def test_collector_output_can_be_wrapped_as_evidence():
    metrics=summarize_nccl(parse_nccl_tests((FIX/"nccl_all_reduce.txt").read_text()))
    bundle=build_evidence_bundle(bundle_id="nccl-001",test_ref="nccl-collective",topology_ref="golden-576",collector="nccl-tests",collector_version="0.1",measurements=metrics,asset_refs=["rack-a/node-01"])
    assert bundle["testRef"] == "nccl-collective"
    assert bundle["provenance"]["collector"] == "nccl-tests"

from pathlib import Path

from ai_factory_engineering.acceptance import load_and_validate_test_spec
from ai_factory_engineering.baseline_binding import bind_typed_baselines
from ai_factory_engineering.typed_baseline import TypedBaseline

ROOT = Path(__file__).resolve().parents[1]


def test_fabric_reference_templates_validate_and_require_external_binding():
    rdma = load_and_validate_test_spec(ROOT / "acceptance/tests/rdma-health.json")
    nccl = load_and_validate_test_spec(ROOT / "acceptance/tests/nccl-collective.json")
    rdma_bound = bind_typed_baselines(rdma, [
        TypedBaseline("DEMO-RDMA-TX", "rdma_tx_discards", "lte", 0, "count", "demo reference run"),
        TypedBaseline("DEMO-RDMA-RX", "rdma_rx_errors", "lte", 0, "count", "demo reference run"),
    ])
    nccl_bound = bind_typed_baselines(nccl, [
        TypedBaseline("DEMO-NCCL", "nccl_busbw_gbps", "gte", 1, "GB/s", "demo reference run"),
        TypedBaseline("DEMO-NCCL-WRONG", "nccl_wrong_total", "eq", 0, "count", "demo reference run"),
    ])
    assert rdma_bound["spec"]["metrics"][0]["threshold"] == 0
    assert nccl_bound["spec"]["metrics"][0]["threshold"] == 1

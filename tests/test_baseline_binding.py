import pytest

from ai_factory_engineering.baseline_binding import BaselineBindingError, bind_typed_baselines
from ai_factory_engineering.typed_baseline import TypedBaseline


SPEC = {
    "apiVersion": "aifactory.engineering/v1alpha1", "kind": "AcceptanceTest",
    "metadata": {"id": "nccl-collective", "name": "NCCL", "layer": "fabric"},
    "spec": {"objective": "test", "metrics": [{"name": "nccl_busbw_gbps", "op": "gte", "threshold": 0, "unit": "GB/s"}], "evidence": [{"source": "raw-collector-output", "required": True}]},
}


def baseline(metric="nccl_busbw_gbps", value=100.0):
    return TypedBaseline("SITE-NCCL-001", metric, "gte", value, "GB/s", "8xHGX reference run", source="site commissioning baseline")


def test_binding_materializes_external_threshold_without_mutating_template():
    bound = bind_typed_baselines(SPEC, [baseline(value=123.4)])
    assert bound["spec"]["metrics"][0]["threshold"] == 123.4
    assert SPEC["spec"]["metrics"][0]["threshold"] == 0


def test_binding_fails_closed_on_metric_mismatch():
    with pytest.raises(BaselineBindingError, match="not declared"):
        bind_typed_baselines(SPEC, [baseline(metric="wrong_metric")])


def test_binding_fails_closed_when_metric_has_no_baseline():
    with pytest.raises(BaselineBindingError, match="missing baseline"):
        bind_typed_baselines(SPEC, [])

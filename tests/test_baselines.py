from pathlib import Path

from ai_factory_engineering.baselines import (
    load_acceptance_baselines,
    unresolved_baselines,
)


ROOT = Path(__file__).resolve().parents[1]


def test_repository_acceptance_matrix_exposes_unresolved_baselines() -> None:
    baselines = load_acceptance_baselines(ROOT / "acceptance/test-matrix.csv")

    gpu = baselines["GPU-001"]
    assert gpu.metric == "xid_ecc_errors"
    assert gpu.rule is not None
    assert gpu.rule.op == "eq"
    assert gpu.rule.value == 0.0

    unresolved = unresolved_baselines(baselines)
    assert "FAC-PWR-001" in unresolved
    assert "FAB-RDMA-001" in unresolved
    assert "FAB-NCCL-001" in unresolved
    assert "GPU-001" not in unresolved


def test_nonzero_numeric_threshold_requires_operator_semantics(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.csv"
    matrix.write_text(
        "test_id,layer,test,metric,threshold,evidence\n"
        "INF-001,workload,inference,goodput,0.95,metrics\n"
    )

    try:
        load_acceptance_baselines(matrix)
    except ValueError as exc:
        assert "explicit operator semantics" in str(exc)
    else:
        raise AssertionError("ambiguous numeric threshold must fail closed")

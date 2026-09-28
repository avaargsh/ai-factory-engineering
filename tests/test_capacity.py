import pytest

from ai_factory_engineering.capacity import (
    CapacityInputs,
    calculate_capacity,
)


def test_capacity_waterfall() -> None:
    result = calculate_capacity(
        CapacityInputs(
            contract_mw=10.0,
            pue=1.2,
            rack_kw=120.0,
            gpus_per_rack=72,
            facility_usable_factor=0.96,
            healthy_gpu_factor=0.99,
            schedulable_factor=0.95,
            productive_factor=0.80,
            hours=8760,
            tokens_per_productive_gpu_hour=1_000_000,
        )
    )

    assert result.facility_usable_mw == pytest.approx(9.6)
    assert result.it_mw == pytest.approx(8.0)
    assert result.rack_count == 66
    assert result.installed_gpus == 4752
    assert result.productive_gpu_hours > 0
    assert result.total_tokens is not None
    assert result.tokens_per_kwh is not None


def test_invalid_factor_rejected() -> None:
    with pytest.raises(ValueError):
        CapacityInputs(
            contract_mw=1,
            pue=1.2,
            rack_kw=100,
            gpus_per_rack=8,
            productive_factor=1.1,
        )

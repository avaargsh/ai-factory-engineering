from pathlib import Path

import pytest

from ai_factory_engineering.economics import (
    EconomicsInputs,
    TimeSlice,
    evaluate_time_series,
)
from ai_factory_engineering.economics_csv import (
    load_time_slices_csv,
)


def test_time_series_economics() -> None:
    result = evaluate_time_series(
        EconomicsInputs(
            it_capacity_mw=8.0,
            productive_gpu_capacity=4000,
            tokens_per_productive_gpu_hour=1_000_000,
            revenue_per_million_tokens=1.5,
        ),
        [
            TimeSlice(
                duration_hours=1.0,
                electricity_price_per_kwh=0.05,
                it_load_factor=0.5,
                productive_utilization=0.4,
                pue=1.2,
            ),
            TimeSlice(
                duration_hours=1.0,
                electricity_price_per_kwh=0.10,
                it_load_factor=1.0,
                productive_utilization=0.8,
                pue=1.2,
            ),
        ],
    )

    assert result.interval_count == 2
    assert result.total_hours == pytest.approx(2.0)
    assert result.it_mwh == pytest.approx(12.0)
    assert result.facility_mwh == pytest.approx(14.4)
    assert result.electricity_cost == pytest.approx(1200.0)
    assert result.productive_gpu_hours == pytest.approx(4800)
    assert result.tokens == pytest.approx(4.8e9)
    assert result.revenue == pytest.approx(7200.0)
    assert result.margin_after_electricity == pytest.approx(6000.0)


def test_15_minute_csv_loads() -> None:
    root = Path(__file__).resolve().parents[1]
    slices = load_time_slices_csv(
        root / "economics/examples/day-15m.csv"
    )

    assert len(slices) == 8
    assert sum(item.duration_hours for item in slices) == 2.0


def test_invalid_utilization_is_rejected() -> None:
    with pytest.raises(ValueError):
        TimeSlice(
            duration_hours=0.25,
            electricity_price_per_kwh=0.1,
            it_load_factor=1.2,
            productive_utilization=0.8,
            pue=1.2,
        )

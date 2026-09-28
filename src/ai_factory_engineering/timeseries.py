from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def _factor(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class TimeSlice:
    duration_hours: float
    electricity_price_per_kwh: float
    it_load_factor: float
    productive_utilization: float
    pue: float

    def __post_init__(self) -> None:
        if self.duration_hours <= 0:
            raise ValueError("duration_hours must be > 0")
        if self.electricity_price_per_kwh < 0:
            raise ValueError(
                "electricity_price_per_kwh must be >= 0"
            )
        if self.pue < 1.0:
            raise ValueError("pue must be >= 1.0")
        _factor("it_load_factor", self.it_load_factor)
        _factor(
            "productive_utilization",
            self.productive_utilization,
        )


@dataclass(frozen=True)
class TimeSeriesInputs:
    it_capacity_mw: float
    productive_gpu_capacity: float
    tokens_per_productive_gpu_hour: float

    def __post_init__(self) -> None:
        if self.it_capacity_mw <= 0:
            raise ValueError("it_capacity_mw must be > 0")
        if self.productive_gpu_capacity < 0:
            raise ValueError(
                "productive_gpu_capacity must be >= 0"
            )
        if self.tokens_per_productive_gpu_hour < 0:
            raise ValueError(
                "tokens_per_productive_gpu_hour must be >= 0"
            )


@dataclass(frozen=True)
class SliceResult:
    duration_hours: float
    it_mwh: float
    facility_mwh: float
    energy_cost: float
    productive_gpu_hours: float
    tokens: float


@dataclass(frozen=True)
class TimeSeriesResult:
    interval_count: int
    total_hours: float
    it_mwh: float
    facility_mwh: float
    energy_cost: float
    productive_gpu_hours: float
    tokens: float
    tokens_per_kwh: float | None
    energy_cost_per_million_tokens: float | None
    slices: tuple[SliceResult, ...]


def evaluate_time_series(
    inputs: TimeSeriesInputs,
    slices: Iterable[TimeSlice],
) -> TimeSeriesResult:
    results: list[SliceResult] = []

    for item in slices:
        it_mw = (
            inputs.it_capacity_mw
            * item.it_load_factor
        )
        facility_mw = it_mw * item.pue

        it_mwh = it_mw * item.duration_hours
        facility_mwh = (
            facility_mw
            * item.duration_hours
        )
        energy_cost = (
            facility_mwh
            * 1000.0
            * item.electricity_price_per_kwh
        )

        productive_gpu_hours = (
            inputs.productive_gpu_capacity
            * item.productive_utilization
            * item.duration_hours
        )
        tokens = (
            productive_gpu_hours
            * inputs.tokens_per_productive_gpu_hour
        )

        results.append(
            SliceResult(
                duration_hours=item.duration_hours,
                it_mwh=it_mwh,
                facility_mwh=facility_mwh,
                energy_cost=energy_cost,
                productive_gpu_hours=productive_gpu_hours,
                tokens=tokens,
            )
        )

    if not results:
        raise ValueError("at least one time slice is required")

    total_hours = sum(
        item.duration_hours
        for item in results
    )
    it_mwh = sum(item.it_mwh for item in results)
    facility_mwh = sum(
        item.facility_mwh
        for item in results
    )
    energy_cost = sum(
        item.energy_cost
        for item in results
    )
    productive_gpu_hours = sum(
        item.productive_gpu_hours
        for item in results
    )
    tokens = sum(item.tokens for item in results)

    facility_kwh = facility_mwh * 1000.0

    return TimeSeriesResult(
        interval_count=len(results),
        total_hours=total_hours,
        it_mwh=it_mwh,
        facility_mwh=facility_mwh,
        energy_cost=energy_cost,
        productive_gpu_hours=productive_gpu_hours,
        tokens=tokens,
        tokens_per_kwh=(
            tokens / facility_kwh
            if facility_kwh > 0
            else None
        ),
        energy_cost_per_million_tokens=(
            energy_cost / (tokens / 1_000_000.0)
            if tokens > 0
            else None
        ),
        slices=tuple(results),
    )

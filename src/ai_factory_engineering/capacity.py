from __future__ import annotations

import math
from dataclasses import dataclass


def _factor(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class CapacityInputs:
    contract_mw: float
    pue: float
    rack_kw: float
    gpus_per_rack: int
    facility_usable_factor: float = 0.95
    healthy_gpu_factor: float = 0.99
    schedulable_factor: float = 0.97
    productive_factor: float = 0.85
    hours: float = 8760.0
    tokens_per_productive_gpu_hour: float | None = None

    def __post_init__(self) -> None:
        if self.contract_mw <= 0:
            raise ValueError("contract_mw must be > 0")
        if self.pue < 1.0:
            raise ValueError("pue must be >= 1.0")
        if self.rack_kw <= 0:
            raise ValueError("rack_kw must be > 0")
        if self.gpus_per_rack <= 0:
            raise ValueError("gpus_per_rack must be > 0")
        if self.hours <= 0:
            raise ValueError("hours must be > 0")

        _factor("facility_usable_factor", self.facility_usable_factor)
        _factor("healthy_gpu_factor", self.healthy_gpu_factor)
        _factor("schedulable_factor", self.schedulable_factor)
        _factor("productive_factor", self.productive_factor)

        if (
            self.tokens_per_productive_gpu_hour is not None
            and self.tokens_per_productive_gpu_hour < 0
        ):
            raise ValueError(
                "tokens_per_productive_gpu_hour must be >= 0"
            )


@dataclass(frozen=True)
class CapacityResult:
    contract_mw: float
    facility_usable_mw: float
    it_mw: float
    rack_count: int
    installed_gpus: int
    healthy_gpus: float
    schedulable_gpus: float
    productive_gpus: float
    productive_gpu_hours: float
    total_tokens: float | None
    tokens_per_kwh: float | None


def calculate_capacity(inputs: CapacityInputs) -> CapacityResult:
    facility_usable_mw = (
        inputs.contract_mw
        * inputs.facility_usable_factor
    )
    it_mw = facility_usable_mw / inputs.pue

    rack_count = math.floor(
        (it_mw * 1000.0) / inputs.rack_kw
    )
    installed_gpus = rack_count * inputs.gpus_per_rack

    healthy_gpus = (
        installed_gpus
        * inputs.healthy_gpu_factor
    )
    schedulable_gpus = (
        healthy_gpus
        * inputs.schedulable_factor
    )
    productive_gpus = (
        schedulable_gpus
        * inputs.productive_factor
    )
    productive_gpu_hours = productive_gpus * inputs.hours

    total_tokens = None
    tokens_per_kwh = None

    if inputs.tokens_per_productive_gpu_hour is not None:
        total_tokens = (
            productive_gpu_hours
            * inputs.tokens_per_productive_gpu_hour
        )
        facility_kwh = (
            inputs.contract_mw
            * 1000.0
            * inputs.hours
        )
        tokens_per_kwh = (
            total_tokens / facility_kwh
            if facility_kwh > 0
            else None
        )

    return CapacityResult(
        contract_mw=inputs.contract_mw,
        facility_usable_mw=facility_usable_mw,
        it_mw=it_mw,
        rack_count=rack_count,
        installed_gpus=installed_gpus,
        healthy_gpus=healthy_gpus,
        schedulable_gpus=schedulable_gpus,
        productive_gpus=productive_gpus,
        productive_gpu_hours=productive_gpu_hours,
        total_tokens=total_tokens,
        tokens_per_kwh=tokens_per_kwh,
    )

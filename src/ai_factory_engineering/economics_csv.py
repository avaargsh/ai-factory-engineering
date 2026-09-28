from __future__ import annotations

import csv
from pathlib import Path

from .economics import TimeSlice


def load_time_slices_csv(
    path: str | Path,
) -> list[TimeSlice]:
    slices: list[TimeSlice] = []

    with Path(path).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        required = {
            "duration_hours",
            "electricity_price_per_kwh",
            "it_load_factor",
            "productive_utilization",
            "pue",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "missing CSV columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            slices.append(
                TimeSlice(
                    duration_hours=float(
                        row["duration_hours"]
                    ),
                    electricity_price_per_kwh=float(
                        row["electricity_price_per_kwh"]
                    ),
                    it_load_factor=float(
                        row["it_load_factor"]
                    ),
                    productive_utilization=float(
                        row["productive_utilization"]
                    ),
                    pue=float(row["pue"]),
                )
            )

    return slices

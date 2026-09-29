from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NcclSample:
    size_bytes: int
    time_us: float
    algbw_gbps: float
    busbw_gbps: float
    wrong: int = 0
    inplace_time_us: float | None = None
    inplace_algbw_gbps: float | None = None
    inplace_busbw_gbps: float | None = None
    inplace_wrong: int = 0


def parse_nccl_tests(text: str) -> tuple[NcclSample, ...]:
    """Parse nccl-tests perf rows without applying acceptance thresholds.

    Supports the repository's normalized 9-column rows and standard perf rows
    containing both out-of-place and in-place result groups.
    """
    samples: list[NcclSample] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens = stripped.split()
        if len(tokens) < 9:
            continue
        try:
            size = int(tokens[0])
            time = float(tokens[5])
            algbw = float(tokens[6])
            busbw = float(tokens[7])
            wrong = int(float(tokens[8]))
        except ValueError:
            continue

        kwargs: dict[str, float | int | None] = {}
        if len(tokens) >= 13:
            try:
                kwargs = {
                    "inplace_time_us": float(tokens[9]),
                    "inplace_algbw_gbps": float(tokens[10]),
                    "inplace_busbw_gbps": float(tokens[11]),
                    "inplace_wrong": int(float(tokens[12])),
                }
            except ValueError:
                continue

        samples.append(NcclSample(size, time, algbw, busbw, wrong, **kwargs))
    return tuple(samples)


def summarize_nccl(samples: tuple[NcclSample, ...]) -> dict[str, float]:
    if not samples:
        return {}
    largest = max(samples, key=lambda sample: sample.size_bytes)
    metrics = {
        "nccl_largest_message_bytes": float(largest.size_bytes),
        "nccl_algbw_gbps": largest.algbw_gbps,
        "nccl_busbw_gbps": largest.busbw_gbps,
        "nccl_wrong_total": float(sum(s.wrong + s.inplace_wrong for s in samples)),
    }
    if largest.inplace_busbw_gbps is not None:
        metrics["nccl_inplace_algbw_gbps"] = float(largest.inplace_algbw_gbps)
        metrics["nccl_inplace_busbw_gbps"] = largest.inplace_busbw_gbps
    return metrics

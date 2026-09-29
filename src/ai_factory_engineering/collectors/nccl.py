from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NcclSample:
    size_bytes: int
    time_us: float
    algbw_gbps: float
    busbw_gbps: float


# Normalized nccl-tests fixture columns:
# size count type redop root time algbw busbw errors
_ROW = re.compile(
    r"^\\s*(?P<size>\\d+)\\s+\\d+\\s+\\S+\\s+\\S+\\s+\\S+\\s+"
    r"(?P<time>[0-9.]+)\\s+(?P<algbw>[0-9.]+)\\s+(?P<busbw>[0-9.]+)"
)


def parse_nccl_tests(text: str) -> tuple[NcclSample, ...]:
    """Parse normalized nccl-tests observations without applying thresholds."""
    samples: list[NcclSample] = []
    for line in text.splitlines():
        match = _ROW.match(line)
        if match:
            samples.append(
                NcclSample(
                    size_bytes=int(match.group("size")),
                    time_us=float(match.group("time")),
                    algbw_gbps=float(match.group("algbw")),
                    busbw_gbps=float(match.group("busbw")),
                )
            )
    return tuple(samples)


def summarize_nccl(samples: tuple[NcclSample, ...]) -> dict[str, float]:
    if not samples:
        return {}
    largest = max(samples, key=lambda sample: sample.size_bytes)
    return {
        "nccl_largest_message_bytes": float(largest.size_bytes),
        "nccl_algbw_gbps": largest.algbw_gbps,
        "nccl_busbw_gbps": largest.busbw_gbps,
    }

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NcclSample:
    size_bytes: int
    time_us: float
    algbw_gbps: float
    busbw_gbps: float


_ROW = re.compile(r"^\s*(?P<size>\d+)\s+\d+\s+\S+\s+\S+\s+(?P<time>[0-9.]+)\s+(?P<algbw>[0-9.]+)\s+(?P<busbw>[0-9.]+)")


def parse_nccl_tests(text: str) -> tuple[NcclSample, ...]:
    """Parse the out-of-place numeric columns emitted by nccl-tests.

    The collector deliberately returns observations only. Acceptance thresholds
    belong to DesignIntent/reference profiles.
    """
    samples=[]
    for line in text.splitlines():
        match=_ROW.match(line)
        if match:
            samples.append(NcclSample(int(match.group("size")), float(match.group("time")), float(match.group("algbw")), float(match.group("busbw"))))
    return tuple(samples)


def summarize_nccl(samples: tuple[NcclSample, ...]) -> dict[str, float]:
    if not samples:
        return {}
    largest=max(samples, key=lambda s:s.size_bytes)
    return {"nccl_largest_message_bytes":float(largest.size_bytes),"nccl_algbw_gbps":largest.algbw_gbps,"nccl_busbw_gbps":largest.busbw_gbps}

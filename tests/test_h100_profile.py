import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_h100_profile_separates_vendor_reference_from_site_acceptance() -> None:
    profile = json.loads(
        (ROOT / "acceptance/profiles/platform/h100-sxm-80gb.json").read_text()
    )

    vendor = profile["references"][0]["facts"]
    assert vendor["gpu_memory_bandwidth_tb_s"] == 3.35
    assert vendor["nvlink_max_bandwidth_gb_s"] == 900

    declared = profile["acceptance"]["declared"]
    assert declared == [
        {
            "baseline_ref": "acceptance/baselines/gpu-health.json",
            "purpose": "zero-tolerance GPU health error gate",
        }
    ]

    pending = {
        item["test"]
        for item in profile["acceptance"]["pending_site_baselines"]
    }
    assert pending == {
        "memory-bandwidth",
        "nvlink-bandwidth",
        "nccl-scale-out",
    }

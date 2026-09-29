import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fabric_profile_requires_transport_before_collectives() -> None:
    profile = json.loads(
        (ROOT / "acceptance/profiles/platform/h100-rocev2-fabric.json").read_text()
    )
    stages = {stage["id"]: stage for stage in profile["stages"]}

    assert stages["collective-performance"]["depends_on"] == ["transport-health"]
    assert "rdma_tx_discards" in stages["transport-health"]["required_measurements"]
    assert "nccl_busbw_gbps" in stages["collective-performance"]["required_measurements"]


def test_congestion_signals_are_not_encoded_as_unconditional_failures() -> None:
    profile = json.loads(
        (ROOT / "acceptance/profiles/platform/h100-rocev2-fabric.json").read_text()
    )
    semantics = profile["stages"][0]["semantics"]

    assert "not an unconditional failure" in semantics["roce_ecn_marked"]
    assert "not an unconditional failure" in semantics["roce_cnp_sent"]
    assert len(profile["pending_site_baselines"]) == 4

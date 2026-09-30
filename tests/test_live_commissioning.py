import json
from pathlib import Path

from ai_factory_engineering.commissioning import GateSpec, GateStatus
from ai_factory_engineering.live_commissioning import LiveTest, run_live_commissioning
from ai_factory_engineering.runner import CommandResult
from ai_factory_engineering.typed_baseline import TypedBaseline

ROOT=Path(__file__).resolve().parents[1]

class RoutedRunner:
    def run(self, command, *, timeout_seconds=60.0):
        if command[0]=="rdma-stat": return CommandResult(tuple(command),0,"port_xmit_discards: 0\nport_rcv_errors: 0\n","")
        if command[0]=="nccl-tests": return CommandResult(tuple(command),0,"8388608 2097152 float sum -1 75.0 111.0 112.35 0\n","")
        raise AssertionError(command)

def spec(name): return json.loads((ROOT/f"acceptance/tests/{name}.json").read_text())

def live_tests(nccl_threshold=100.0):
    return [
      LiveTest("rdma",("rdma-stat",),spec("rdma-health"),(
        TypedBaseline("D-RX","rdma_rx_errors","lte",0,"count","demo"),TypedBaseline("D-TX","rdma_tx_discards","lte",0,"count","demo")), "fabric-gate","rdma-1"),
      LiveTest("nccl",("nccl-tests",),spec("nccl-collective"),(
        TypedBaseline("D-NCCL","nccl_busbw_gbps","gte",nccl_threshold,"GB/s","demo"), TypedBaseline("D-NCCL-WRONG","nccl_wrong_total","eq",0,"count","demo")), "fabric-gate","nccl-1")]

def test_live_commissioning_passes_only_after_evidence_evaluation(tmp_path):
    result=run_live_commissioning(tests=live_tests(),gates=[GateSpec("fabric-gate","fabric",("rdma-health","nccl-collective"))],runner=RoutedRunner(),output_dir=tmp_path,topology_ref="demo")
    assert result.gates[0].status == GateStatus.PASS
    assert len(result.evidence)==2

def test_successful_command_still_fails_gate_when_nccl_misses_baseline(tmp_path):
    result=run_live_commissioning(tests=live_tests(120.0),gates=[GateSpec("fabric-gate","fabric",("rdma-health","nccl-collective"))],runner=RoutedRunner(),output_dir=tmp_path,topology_ref="demo")
    assert result.gates[0].status == GateStatus.FAIL
    assert "actual=112.35" in result.gates[0].reasons[0]



class FixedThresholdRunner:
    def run(self, command, *, timeout_seconds=60.0):
        return CommandResult(
            tuple(command),
            0,
            "gpu_id,gpu_temp,power_w,sm_clock_mhz,ecc_uncorrected\n"
            "0,61,650,1830,0\n",
            "",
        )


def test_live_commissioning_allows_fixed_threshold_test_without_baseline(tmp_path):
    test_spec = json.loads(
        (ROOT / "acceptance/tests/gpu-health.json").read_text()
    )
    result = run_live_commissioning(
        tests=[
            LiveTest(
                "gpu_csv",
                ("gpu-health",),
                test_spec,
                (),
                "compute",
                "gpu-live",
                version_matrix={"driver": "test-driver"},
                asset_refs=("asset://gpu-0",),
            )
        ],
        gates=[
            GateSpec(
                "compute",
                "compute",
                ("gpu-health",),
            )
        ],
        runner=FixedThresholdRunner(),
        output_dir=tmp_path,
        topology_ref="lab://node-1",
    )

    assert result.gates[0].status == GateStatus.PASS
    bundle = result.evidence[0]
    assert bundle["environment"]["versionMatrix"]["driver"] == "test-driver"
    assert bundle["provenance"]["assetRefs"] == ["asset://gpu-0"]
    assert bundle["artifacts"][0]["checksum"].startswith("sha256:")

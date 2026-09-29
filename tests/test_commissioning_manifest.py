from pathlib import Path
from ai_factory_engineering.commissioning_manifest import load_live_manifest
ROOT=Path(__file__).resolve().parents[1]

def test_demo_live_manifest_resolves_tests_baselines_and_gates():
    run_id, topology, gates, tests=load_live_manifest(ROOT/"acceptance/examples/live-fabric-run.json")
    assert run_id=="demo-fabric-001"
    assert topology=="golden-factory-576"
    assert gates[0].tests==("rdma-health","nccl-collective")
    assert tests[0].baselines[0].source=="synthetic CI fixture"
    assert tests[1].baselines[0].metric=="nccl_busbw_gbps"

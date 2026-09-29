import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_run_collector_executes_and_hashes_raw_output(tmp_path):
    fixture=ROOT/"tests/fixtures/rdma_counters.txt"
    proc=subprocess.run([sys.executable,"-m","ai_factory_engineering.cli","run-collector","rdma","--command",sys.executable,"-c",f"print(open({str(fixture)!r}).read(), end='')","--output-dir",str(tmp_path),"--bundle-id","rdma-run-001","--test-ref","rdma-health","--topology-ref","golden-factory-576"],capture_output=True,text=True,check=True)
    bundle=json.loads(proc.stdout)
    assert bundle["measurements"]["roce_ecn_marked"] == 128
    assert bundle["artifacts"][0]["checksum"].startswith("sha256:")
    assert Path(bundle["artifacts"][0]["uri"]).exists()

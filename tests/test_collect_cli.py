import json
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]

def test_collect_cli_emits_schema_valid_nccl_evidence():
    proc=subprocess.run([sys.executable,"-m","ai_factory_engineering.cli","collect","nccl",str(ROOT/"tests/fixtures/nccl_all_reduce.txt"),"--bundle-id","golden-nccl-001","--test-ref","nccl-collective","--topology-ref","golden-factory-576","--asset-ref","rack-a/node-01"],capture_output=True,text=True,check=True)
    bundle=json.loads(proc.stdout)
    schema=json.loads((ROOT/"schemas/evidence-bundle.schema.json").read_text())
    Draft202012Validator(schema,format_checker=Draft202012Validator.FORMAT_CHECKER).validate(bundle)
    assert bundle["measurements"]["nccl_busbw_gbps"] == 112.35
    assert bundle["provenance"]["assetRefs"] == ["rack-a/node-01"]

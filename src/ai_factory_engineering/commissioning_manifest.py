from __future__ import annotations
import json
from pathlib import Path
from .acceptance import load_and_validate_test_spec
from .commissioning import GateSpec
from .live_commissioning import LiveTest
from .typed_baseline import load_typed_baseline

def load_live_manifest(path: str | Path):
    path=Path(path); doc=json.loads(path.read_text(encoding="utf-8")); base=path.parent
    gates=tuple(GateSpec(g["id"],g["layer"],tuple(g["tests"]),tuple(g.get("dependsOn",())),g.get("failClosed",True)) for g in doc["gates"])
    tests=[]
    for item in doc["tests"]:
        tests.append(LiveTest(item["collector"],tuple(item["command"]),load_and_validate_test_spec(base/item["test"]),tuple(load_typed_baseline(base/p) for p in item["baselines"]),item["gateId"],item["bundleId"]))
    return doc["runId"],doc["topologyRef"],gates,tuple(tests)

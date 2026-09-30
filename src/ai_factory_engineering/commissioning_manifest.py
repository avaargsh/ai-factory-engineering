from __future__ import annotations

import json
from pathlib import Path

from .acceptance import load_and_validate_test_spec
from .commissioning import GateSpec
from .live_commissioning import LiveTest
from .typed_baseline import load_typed_baseline


def load_live_manifest(path: str | Path):
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent

    gates = tuple(
        GateSpec(
            g["id"],
            g["layer"],
            tuple(g["tests"]),
            tuple(g.get("dependsOn", ())),
            g.get("failClosed", True),
        )
        for g in doc["gates"]
    )

    global_version_matrix = {
        str(key): str(value)
        for key, value in doc.get("versionMatrix", {}).items()
    }
    global_asset_refs = tuple(
        str(value)
        for value in doc.get("assetRefs", ())
    )
    global_collector_version = str(
        doc.get("collectorVersion", "0.1")
    )
    global_timeout = float(
        doc.get("timeoutSeconds", 60.0)
    )

    tests = []
    for item in doc["tests"]:
        version_matrix = {
            **global_version_matrix,
            **{
                str(key): str(value)
                for key, value in item.get("versionMatrix", {}).items()
            },
        }
        asset_refs = (
            global_asset_refs
            + tuple(str(value) for value in item.get("assetRefs", ()))
        )
        tests.append(
            LiveTest(
                collector=item["collector"],
                command=tuple(item["command"]),
                test_spec=load_and_validate_test_spec(
                    base / item["test"]
                ),
                baselines=tuple(
                    load_typed_baseline(base / baseline)
                    for baseline in item.get("baselines", ())
                ),
                gate_id=item["gateId"],
                bundle_id=item["bundleId"],
                collector_version=str(
                    item.get(
                        "collectorVersion",
                        global_collector_version,
                    )
                ),
                asset_refs=asset_refs,
                version_matrix=version_matrix,
                timeout_seconds=float(
                    item.get(
                        "timeoutSeconds",
                        global_timeout,
                    )
                ),
            )
        )

    return (
        doc["runId"],
        doc["topologyRef"],
        gates,
        tuple(tests),
    )


def load_manifest_annotations(
    path: str | Path,
) -> dict:
    """Return reporting-only manifest annotations without changing execution."""
    doc = json.loads(
        Path(path).read_text(encoding="utf-8")
    )
    not_evaluated = doc.get("notEvaluated", [])
    if not isinstance(not_evaluated, list):
        raise ValueError("notEvaluated must be an array")
    return {
        "notEvaluated": not_evaluated,
        "versionMatrix": dict(
            doc.get("versionMatrix", {})
        ),
        "assetRefs": list(
            doc.get("assetRefs", [])
        ),
    }



def validate_controlled_lab_manifest(
    path: str | Path,
) -> None:
    """Fail closed until a controlled-lab manifest is explicitly site-bound."""
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                yield from walk(item)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item)
        elif isinstance(value, str):
            yield value

    placeholders = [
        value
        for value in walk(doc)
        if "CHANGE-ME" in value
    ]
    if placeholders:
        raise ValueError(
            "controlled-lab manifest contains CHANGE-ME placeholders"
        )

    version_matrix = doc.get("versionMatrix")
    if not isinstance(version_matrix, dict) or not version_matrix:
        raise ValueError(
            "controlled-lab manifest requires versionMatrix"
        )
    asset_refs = doc.get("assetRefs")
    if not isinstance(asset_refs, list) or not asset_refs:
        raise ValueError(
            "controlled-lab manifest requires assetRefs"
        )

    gate_layers = {
        gate.get("layer")
        for gate in doc.get("gates", [])
        if isinstance(gate, dict)
    }
    for required in ("compute", "runtime"):
        if required not in gate_layers:
            raise ValueError(
                f"controlled-lab manifest requires {required} gate"
            )

    base = path.parent
    for item in doc.get("tests", []):
        for baseline in item.get("baselines", []):
            baseline_path = base / baseline
            payload = json.loads(
                baseline_path.read_text(
                    encoding="utf-8"
                )
            )
            source = str(payload.get("source", ""))
            scope = str(payload.get("scope", ""))
            if (
                "FAIL-CLOSED PLACEHOLDER" in source
                or "CHANGE-ME" in source
                or "CHANGE-ME" in scope
            ):
                raise ValueError(
                    f"baseline is still a template: {baseline_path}"
                )

    load_live_manifest(path)

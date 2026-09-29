from __future__ import annotations

import json
from pathlib import Path

from ai_factory_engineering.acceptance_artifact import (
    build_acceptance_artifact,
    verify_acceptance_artifact,
)
from ai_factory_engineering.attestation import (
    attest_acceptance_artifact,
    verify_acceptance_attestation,
)
from ai_factory_engineering.commissioning import GateSpec, GateStatus, TestOutcome
from ai_factory_engineering.cross_layer_acceptance import decide_cross_layer_acceptance


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    plan = json.loads(
        (ROOT / "acceptance/examples/576-gpu-runtime-commissioning-plan.json").read_text()
    )
    raw = json.loads(
        (ROOT / "acceptance/examples/576-gpu-runtime-golden-outcomes.json").read_text()
    )
    gates = tuple(
        GateSpec(
            id=item["id"],
            layer=item["layer"],
            tests=tuple(item["tests"]),
            depends_on=tuple(item.get("depends_on", ())),
            fail_closed=item.get("acceptance_policy", {}).get("fail_closed", True),
        )
        for item in plan["gates"]
    )
    outcomes = {
        gate_id: tuple(
            TestOutcome(
                test_id=item["test_id"],
                status=GateStatus(item["status"]),
                evidence_complete=item["evidence_complete"],
            )
            for item in items
        )
        for gate_id, items in raw.items()
    }

    decision = decide_cross_layer_acceptance(gates, outcomes)
    artifact = build_acceptance_artifact(
        decision,
        case_id=plan["id"],
        evidence_refs={
            "gpu": "evidence://dcgm/golden-576",
            "fabric": "evidence://nccl/golden-576",
            "runtime": "evidence://inference/golden-576",
        },
    )
    attestation = attest_acceptance_artifact(
        artifact,
        key_id="demo-commissioning-key",
        secret=b"demo-only-secret",
    )

    print(json.dumps({
        "decision": decision.disposition.value,
        "artifactDigest": artifact["digest"],
        "artifactVerified": verify_acceptance_artifact(artifact),
        "attestationVerified": verify_acceptance_attestation(
            artifact, attestation, secret=b"demo-only-secret"
        ),
        "gates": [
            {"id": gate.gate_id, "status": gate.status.value}
            for gate in decision.gates
        ],
    }, indent=2))


if __name__ == "__main__":
    main()

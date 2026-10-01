#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from ai_factory_engineering.acceptance_artifact import (
    build_acceptance_artifact,
    replay_acceptance_artifact,
    verify_acceptance_artifact,
)
from ai_factory_engineering.collector_execution import (
    execute_collector_to_evidence,
)
from ai_factory_engineering.commissioning import (
    GateSpec,
    GateStatus,
    TestOutcome,
)
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    decide_cross_layer_acceptance,
)
from ai_factory_engineering.runner import (
    CollectorExecutionError,
    CommandResult,
)


class MalformedInferenceRunner:
    def run(self, command, *, timeout_seconds=60.0):
        return CommandResult(
            tuple(command),
            0,
            "{not-valid-json}\n",
            "collector produced malformed inference payload\n",
        )


def build_failure_fixture(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        execute_collector_to_evidence(
            collector="inference",
            command=["controlled-malformed-inference"],
            output_dir=output_dir,
            bundle_id="inference-normalization-failure",
            test_ref="inference-slo",
            topology_ref="controlled-lab://failure-fixture",
            runner=MalformedInferenceRunner(),
        )
    except CollectorExecutionError as exc:
        artifacts = tuple(exc.artifacts)
        if len(artifacts) != 2:
            raise RuntimeError(
                "failure fixture must preserve stdout and stderr artifacts"
            ) from exc
        failure = {
            "schemaVersion": 1,
            "caseId": "controlled-normalization-failure",
            "failureType": "NORMALIZATION_ERROR",
            "collector": "inference",
            "testRef": "inference-slo",
            "topologyRef": "controlled-lab://failure-fixture",
            "error": str(exc),
            "evidenceComplete": False,
            "artifacts": list(artifacts),
        }
    else:
        raise RuntimeError(
            "failure fixture unexpectedly normalized malformed collector output"
        )

    outcome = TestOutcome(
        test_id="inference-slo",
        status=GateStatus.ERROR,
        evidence_complete=False,
        reason=failure["error"],
    )
    decision = decide_cross_layer_acceptance(
        (
            GateSpec(
                id="runtime",
                layer="runtime",
                tests=("inference-slo",),
                fail_closed=True,
            ),
        ),
        {"runtime": (outcome,)},
    )
    if decision.disposition is not AcceptanceDisposition.REJECT:
        raise RuntimeError(
            "incomplete normalization evidence must reject acceptance"
        )

    evidence_refs = {
        f"failure.{artifact['type']}": artifact["checksum"]
        for artifact in failure["artifacts"]
    }
    artifact = build_acceptance_artifact(
        decision,
        case_id=failure["caseId"],
        evidence_refs=evidence_refs,
        issued_at="2026-10-01T00:00:00Z",
    )
    if not verify_acceptance_artifact(artifact):
        raise RuntimeError("failure AcceptanceArtifact failed verification")

    replayed = replay_acceptance_artifact(artifact)
    if replayed != decision:
        raise RuntimeError(
            "failure AcceptanceArtifact replay changed the decision"
        )

    failure["acceptanceArtifactDigest"] = artifact["digest"]
    failure["disposition"] = artifact["disposition"]

    (output_dir / "failure-evidence.json").write_text(
        json.dumps(failure, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "acceptance-artifact.json").write_text(
        json.dumps(artifact, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS",
        "fixture": failure["caseId"],
        "expectedDisposition": "REJECT",
        "rawArtifactCount": len(failure["artifacts"]),
        "acceptanceArtifactDigest": artifact["digest"],
        "replayVerified": True,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    output = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else ".artifacts/release/failure-fixture"
    )
    print(json.dumps(build_failure_fixture(output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import json
from pathlib import Path
import subprocess
import sys

from ai_factory_engineering.acceptance_artifact import (
    replay_acceptance_artifact,
    verify_acceptance_artifact,
)
from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
)


ROOT = Path(__file__).parents[1]


def test_release_failure_fixture_preserves_raw_evidence_and_replays_reject(
    tmp_path,
):
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/generate_failure_fixture.py",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["status"] == "PASS"
    assert summary["expectedDisposition"] == "REJECT"
    assert summary["rawArtifactCount"] == 2
    assert summary["replayVerified"] is True

    failure = json.loads(
        (tmp_path / "failure-evidence.json").read_text()
    )
    assert failure["failureType"] == "NORMALIZATION_ERROR"
    assert failure["evidenceComplete"] is False
    assert len(failure["artifacts"]) == 2
    for raw in failure["artifacts"]:
        assert raw["checksum"].startswith("sha256:")
        assert Path(raw["uri"]).exists()

    artifact = json.loads(
        (tmp_path / "acceptance-artifact.json").read_text()
    )
    assert verify_acceptance_artifact(artifact)
    replayed = replay_acceptance_artifact(artifact)
    assert replayed.disposition is AcceptanceDisposition.REJECT
    assert replayed.accepted is False

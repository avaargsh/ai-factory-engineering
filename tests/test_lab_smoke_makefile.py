import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_lab_smoke_requires_real_secret_environment_variable(tmp_path):
    env = os.environ.copy()
    env.pop("AI_FACTORY_ATTESTATION_SECRET", None)
    completed = subprocess.run(
        [
            "make", "lab-smoke",
            "MANIFEST=unused.json",
            "ATTESTATION_KEY_ID=commissioning-lab",
            f"LAB_ARTIFACTS={tmp_path / 'lab'}",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "AI_FACTORY_ATTESTATION_SECRET is required" in (
        completed.stdout + completed.stderr
    )


def test_lab_smoke_never_removes_existing_evidence(tmp_path):
    lab_dir = tmp_path / "existing-lab"
    lab_dir.mkdir()
    sentinel = lab_dir / "raw-evidence.txt"
    sentinel.write_text("retain-me", encoding="utf-8")

    env = os.environ.copy()
    env["AI_FACTORY_ATTESTATION_SECRET"] = "test-only-secret"
    completed = subprocess.run(
        [
            "make", "lab-smoke",
            "MANIFEST=unused.json",
            "ATTESTATION_KEY_ID=commissioning-lab",
            f"LAB_ARTIFACTS={lab_dir}",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "already exists" in (completed.stdout + completed.stderr)
    assert sentinel.read_text(encoding="utf-8") == "retain-me"

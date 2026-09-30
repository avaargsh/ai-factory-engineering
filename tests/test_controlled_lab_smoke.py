import json
from pathlib import Path
import sys

import pytest

from ai_factory_engineering.acceptance_artifact import (
    verify_acceptance_artifact,
)
from ai_factory_engineering.cli import main
from ai_factory_engineering.commissioning_manifest import (
    validate_controlled_lab_manifest,
)


ROOT = Path(__file__).parents[1]


def _write_baseline(path, *, metric, operator, value, unit):
    path.write_text(
        json.dumps(
            {
                "id": f"lab-{metric}",
                "metric": metric,
                "operator": operator,
                "value": value,
                "unit": unit,
                "scope": "controlled lab test workload",
                "source": "approved test baseline",
            }
        ),
        encoding="utf-8",
    )


def test_repository_lab_template_is_intentionally_unbound():
    with pytest.raises(
        ValueError,
        match="CHANGE-ME",
    ):
        validate_controlled_lab_manifest(
            ROOT
            / "acceptance"
            / "examples"
            / "controlled-lab-minimum.template.json"
        )


def test_controlled_lab_commission_emits_acceptance_artifact(
    tmp_path,
    monkeypatch,
    capsys,
):
    ttft = tmp_path / "ttft.json"
    tpot = tmp_path / "tpot.json"
    success = tmp_path / "success.json"
    _write_baseline(
        ttft,
        metric="ttft_p95_ms",
        operator="lte",
        value=200,
        unit="ms",
    )
    _write_baseline(
        tpot,
        metric="tpot_p95_ms",
        operator="lte",
        value=50,
        unit="ms/token",
    )
    _write_baseline(
        success,
        metric="success_ratio",
        operator="gte",
        value=0.99,
        unit="ratio",
    )

    gpu_test = ROOT / "acceptance" / "tests" / "gpu-health.json"
    inference_test = (
        ROOT
        / "acceptance"
        / "tests"
        / "inference-slo.json"
    )
    manifest = tmp_path / "lab.json"
    manifest.write_text(
        json.dumps(
            {
                "runId": "lab-001",
                "topologyRef": "lab://node-01",
                "versionMatrix": {
                    "gpu": "test-gpu",
                    "driver": "test-driver",
                    "runtime": "test-runtime",
                    "model": "test-model",
                    "benchmark": "test-benchmark",
                },
                "assetRefs": ["asset://gpu-node-01"],
                "notEvaluated": [
                    {
                        "layer": "fabric",
                        "reason": "single-node lab",
                    }
                ],
                "gates": [
                    {
                        "id": "compute",
                        "layer": "compute",
                        "tests": ["gpu-health"],
                        "failClosed": True,
                    },
                    {
                        "id": "runtime",
                        "layer": "runtime",
                        "tests": ["inference-slo"],
                        "dependsOn": ["compute"],
                        "failClosed": True,
                    },
                ],
                "tests": [
                    {
                        "collector": "gpu_csv",
                        "command": [
                            sys.executable,
                            "-c",
                            (
                                "print('gpu_id,gpu_temp,power_w,"
                                "sm_clock_mhz,ecc_uncorrected\\n"
                                "0,61,650,1830,0')"
                            ),
                        ],
                        "test": str(gpu_test),
                        "baselines": [],
                        "gateId": "compute",
                        "bundleId": "gpu-live",
                    },
                    {
                        "collector": "inference",
                        "command": [
                            sys.executable,
                            "-c",
                            (
                                "print('{\"ttft_p95_ms\":120,"
                                "\"tpot_p95_ms\":30,"
                                "\"success_ratio\":0.995}')"
                            ),
                        ],
                        "test": str(inference_test),
                        "baselines": [
                            str(ttft),
                            str(tpot),
                            str(success),
                        ],
                        "gateId": "runtime",
                        "bundleId": "inference-live",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    validate_controlled_lab_manifest(manifest)
    output_dir = tmp_path / "out"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "commission",
            str(manifest),
            "--output-dir",
            str(output_dir),
        ],
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 0
    capsys.readouterr()

    artifact = json.loads(
        (output_dir / "acceptance-artifact.json").read_text(
            encoding="utf-8"
        )
    )
    assert artifact["accepted"] is True
    assert verify_acceptance_artifact(artifact)
    assert set(artifact["evidenceRefs"]) == {
        "gpu-live.bundle",
        "gpu-live.raw-collector-output",
        "gpu-live.raw-collector-stderr",
        "inference-live.bundle",
        "inference-live.raw-collector-output",
        "inference-live.raw-collector-stderr",
    }
    assert all(
        value.startswith("sha256:")
        for value in artifact["evidenceRefs"].values()
    )

    run = json.loads(
        (output_dir / "commissioning-run.json").read_text(
            encoding="utf-8"
        )
    )
    assert run["status"] == "PASS"
    assert run["acceptanceArtifactDigest"] == artifact["digest"]
    assert run["annotations"]["notEvaluated"][0]["layer"] == "fabric"
    assert run["evidence"][0]["environment"]["versionMatrix"][
        "driver"
    ] == "test-driver"

    report = (
        output_dir / "commissioning-report.md"
    ).read_text(encoding="utf-8")
    assert "## Not Evaluated" in report
    assert "fabric" in report

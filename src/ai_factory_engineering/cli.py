from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from .acceptance import (
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)
from .acceptance_run import (
    evaluate_acceptance_run,
    load_acceptance_run_manifest,
)
from .attestation import (
    attest_acceptance_artifact,
    verify_acceptance_attestation,
)
from .capacity import CapacityInputs, calculate_capacity
from .collector_execution import execute_collector_to_evidence
from .collectors.dcgm import parse_dcgm_csv
from .collectors.nccl import parse_nccl_tests, summarize_nccl
from .collectors.nvlink import parse_nvlink_status
from .collectors.rdma import normalize_rdma, parse_rdma_counters
from .evidence import build_evidence_bundle
from .evaluator import evaluate_acceptance
from .report import render_acceptance_markdown
from .run_report import render_acceptance_run_markdown
from .timeseries import TimeSeriesInputs, evaluate_time_series
from .timeseries_csv import load_time_slices_csv
from .recovery_cli import add_recovery_parser, run_recovery_cli
from .commissioning_manifest import load_live_manifest
from .live_commissioning import run_live_commissioning
from .commissioning_report import commissioning_run_document, render_commissioning_markdown


def main() -> None:
    parser = argparse.ArgumentParser(prog="ai-factory")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    validate_test = subparsers.add_parser("validate-test")
    validate_test.add_argument("path")

    validate_evidence = subparsers.add_parser("validate-evidence")
    validate_evidence.add_argument("path")

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("test")
    evaluate.add_argument("evidence")

    evaluate_run = subparsers.add_parser("evaluate-run")
    evaluate_run.add_argument("manifest")

    collect = subparsers.add_parser("collect")
    collect.add_argument("collector", choices=["dcgm", "nvlink", "rdma", "nccl"])
    collect.add_argument("input")
    collect.add_argument("--bundle-id", required=True)
    collect.add_argument("--test-ref", required=True)
    collect.add_argument("--topology-ref", required=True)
    collect.add_argument("--collector-version", default="0.1")
    collect.add_argument("--asset-ref", action="append", default=[])

    run_collector = subparsers.add_parser("run-collector")
    run_collector.add_argument("collector", choices=["dcgm", "nvlink", "rdma", "nccl"])
    run_collector.add_argument("--output-dir", required=True)
    run_collector.add_argument("--bundle-id", required=True)
    run_collector.add_argument("--test-ref", required=True)
    run_collector.add_argument("--topology-ref", required=True)
    run_collector.add_argument("--collector-version", default="0.1")
    run_collector.add_argument("--asset-ref", action="append", default=[])
    run_collector.add_argument("--timeout", type=float, default=60.0)

    commission = subparsers.add_parser("commission")
    commission.add_argument("manifest")
    commission.add_argument("--output-dir", required=True)

    attest = subparsers.add_parser("attest")
    attest.add_argument("artifact")
    attest.add_argument("--key-id", required=True)
    attest.add_argument("--output", required=True)
    attest.add_argument(
        "--secret-env",
        default="AI_FACTORY_ATTESTATION_SECRET",
    )

    verify_attestation = subparsers.add_parser(
        "verify-attestation"
    )
    verify_attestation.add_argument("artifact")
    verify_attestation.add_argument("attestation")
    verify_attestation.add_argument(
        "--expected-key-id",
        required=False,
    )
    verify_attestation.add_argument(
        "--secret-env",
        default="AI_FACTORY_ATTESTATION_SECRET",
    )

    capacity = subparsers.add_parser("capacity")
    capacity.add_argument("--contract-mw", type=float, required=True)
    capacity.add_argument("--pue", type=float, required=True)
    capacity.add_argument("--rack-kw", type=float, required=True)
    capacity.add_argument("--gpus-per-rack", type=int, required=True)
    capacity.add_argument("--facility-usable-factor", type=float, default=0.95)
    capacity.add_argument("--healthy-gpu-factor", type=float, default=0.99)
    capacity.add_argument("--schedulable-factor", type=float, default=0.97)
    capacity.add_argument("--productive-factor", type=float, default=0.85)
    capacity.add_argument("--hours", type=float, default=8760.0)
    capacity.add_argument("--tokens-per-productive-gpu-hour", type=float)

    add_recovery_parser(subparsers)

    timeseries = subparsers.add_parser("timeseries")
    timeseries.add_argument("csv")
    timeseries.add_argument("--it-capacity-mw", type=float, required=True)
    timeseries.add_argument(
        "--productive-gpu-capacity",
        type=float,
        required=True,
    )
    timeseries.add_argument(
        "--tokens-per-productive-gpu-hour",
        type=float,
        required=True,
    )

    argv = None
    import sys
    raw_argv = sys.argv[1:]
    collector_tail = []
    if raw_argv[:1] == ["run-collector"] and "--" in raw_argv:
        boundary = raw_argv.index("--")
        collector_tail = raw_argv[boundary + 1:]
        raw_argv = raw_argv[:boundary]
    args = parser.parse_args(raw_argv)
    if args.command == "run-collector":
        args.collector_command = collector_tail

    if args.command in {"attest", "verify-attestation"}:
        secret_value = os.environ.get(args.secret_env)
        if not secret_value:
            raise SystemExit(
                f"required secret environment variable is not set: {args.secret_env}"
            )
        secret = secret_value.encode("utf-8")
        artifact = json.loads(
            Path(args.artifact).read_text(encoding="utf-8")
        )

        if args.command == "attest":
            attestation = attest_acceptance_artifact(
                artifact,
                key_id=args.key_id,
                secret=secret,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(attestation, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                json.dumps(
                    {
                        "artifactDigest": attestation["artifactDigest"],
                        "keyId": attestation["keyId"],
                        "algorithm": attestation["algorithm"],
                        "output": str(output),
                    },
                    indent=2,
                )
            )
            return

        attestation = json.loads(
            Path(args.attestation).read_text(encoding="utf-8")
        )
        verified = verify_acceptance_attestation(
            artifact,
            attestation,
            secret=secret,
            expected_key_id=args.expected_key_id,
        )
        print(
            json.dumps(
                {
                    "verified": verified,
                    "artifactDigest": artifact.get("digest"),
                    "keyId": attestation.get("keyId"),
                },
                indent=2,
            )
        )
        raise SystemExit(0 if verified else 3)

    if args.command == "validate-test":
        doc = load_and_validate_test_spec(args.path)
        print(f"valid AcceptanceTest: {doc['metadata']['id']}")
        return

    if args.command == "validate-evidence":
        doc = load_and_validate_evidence_bundle(args.path)
        print(f"valid EvidenceBundle: {doc['metadata']['bundleId']}")
        return

    if args.command == "evaluate":
        test_spec = load_and_validate_test_spec(args.test)
        evidence_bundle = load_and_validate_evidence_bundle(args.evidence)
        result = evaluate_acceptance(test_spec, evidence_bundle)
        print(render_acceptance_markdown(result), end="")
        raise SystemExit(0 if result.passed else 2)

    if args.command == "evaluate-run":
        run_id, cases = load_acceptance_run_manifest(
            args.manifest
        )
        result = evaluate_acceptance_run(
            run_id=run_id,
            cases=cases,
        )
        print(
            render_acceptance_run_markdown(result),
            end="",
        )
        raise SystemExit(0 if result.passed else 2)

    if args.command == "run-collector":
        command = args.collector_command
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            parser.error("run-collector requires a native command after --")
        bundle = execute_collector_to_evidence(
            collector=args.collector,
            command=command,
            output_dir=args.output_dir,
            bundle_id=args.bundle_id,
            test_ref=args.test_ref,
            topology_ref=args.topology_ref,
            collector_version=args.collector_version,
            asset_refs=args.asset_ref,
            timeout_seconds=args.timeout,
        )
        print(json.dumps(bundle, indent=2))
        return

    if args.command == "collect":
        text = Path(args.input).read_text(encoding="utf-8")
        if args.collector == "dcgm":
            measurements = parse_dcgm_csv(text)
        elif args.collector == "nvlink":
            measurements = parse_nvlink_status(text)
        elif args.collector == "rdma":
            measurements = normalize_rdma(parse_rdma_counters(text))
        else:
            measurements = summarize_nccl(parse_nccl_tests(text))
        bundle = build_evidence_bundle(
            bundle_id=args.bundle_id,
            test_ref=args.test_ref,
            topology_ref=args.topology_ref,
            collector=args.collector,
            collector_version=args.collector_version,
            measurements=measurements,
            asset_refs=args.asset_ref,
        )
        print(json.dumps(bundle, indent=2))
        return

    if args.command == "commission":
        run_id, topology_ref, gates, tests = load_live_manifest(args.manifest)
        output_dir = Path(args.output_dir); output_dir.mkdir(parents=True, exist_ok=True)
        result = run_live_commissioning(tests=tests, gates=gates, runner=__import__("ai_factory_engineering.runner", fromlist=["LocalCommandRunner"]).LocalCommandRunner(), output_dir=output_dir, topology_ref=topology_ref)
        document = commissioning_run_document(run_id, topology_ref, result)
        (output_dir / "commissioning-run.json").write_text(json.dumps(document, indent=2, default=str) + "\n", encoding="utf-8")
        (output_dir / "commissioning-report.md").write_text(render_commissioning_markdown(run_id, topology_ref, result), encoding="utf-8")
        print(render_commissioning_markdown(run_id, topology_ref, result), end="")
        raise SystemExit(0 if document["status"] == "PASS" else 2)

    if args.command == "recovery":
        raise SystemExit(run_recovery_cli(args))

    if args.command == "timeseries":
        result = evaluate_time_series(
            TimeSeriesInputs(
                it_capacity_mw=args.it_capacity_mw,
                productive_gpu_capacity=(
                    args.productive_gpu_capacity
                ),
                tokens_per_productive_gpu_hour=(
                    args.tokens_per_productive_gpu_hour
                ),
            ),
            load_time_slices_csv(args.csv),
        )
        print(json.dumps(asdict(result), indent=2))
        return

    result = calculate_capacity(
        CapacityInputs(
            contract_mw=args.contract_mw,
            pue=args.pue,
            rack_kw=args.rack_kw,
            gpus_per_rack=args.gpus_per_rack,
            facility_usable_factor=args.facility_usable_factor,
            healthy_gpu_factor=args.healthy_gpu_factor,
            schedulable_factor=args.schedulable_factor,
            productive_factor=args.productive_factor,
            hours=args.hours,
            tokens_per_productive_gpu_hour=(
                args.tokens_per_productive_gpu_hour
            ),
        )
    )
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()

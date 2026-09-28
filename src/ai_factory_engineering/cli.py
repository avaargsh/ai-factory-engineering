from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .acceptance import (
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)
from .acceptance_run import (
    evaluate_acceptance_run,
    load_acceptance_run_manifest,
)
from .capacity import CapacityInputs, calculate_capacity
from .evaluator import evaluate_acceptance
from .report import render_acceptance_markdown
from .run_report import render_acceptance_run_markdown
from .timeseries import TimeSeriesInputs, evaluate_time_series
from .timeseries_csv import load_time_slices_csv


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

    args = parser.parse_args()

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

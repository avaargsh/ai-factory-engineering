from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .acceptance import (
    load_and_validate_evidence_bundle,
    load_and_validate_test_spec,
)
from .capacity import CapacityInputs, calculate_capacity
from .evaluator import evaluate_acceptance
from .report import render_acceptance_markdown


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

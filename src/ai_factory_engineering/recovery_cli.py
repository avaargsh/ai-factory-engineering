from __future__ import annotations

import argparse
from pathlib import Path

from .inference_slo import load_inference_slo_rules
from .live_experiment import (
    recovery_result_json,
    recovery_result_markdown,
    run_live_inference_recovery,
)
from .live_recovery import LiveRecoveryConfig
from .providers import HttpMetricsSource, KubernetesPodFaultDriver


def add_recovery_parser(subparsers: argparse._SubParsersAction) -> None:
    recovery = subparsers.add_parser("recovery")
    recovery_sub = recovery.add_subparsers(dest="recovery_command", required=True)
    run = recovery_sub.add_parser("run")
    run.add_argument("--namespace", required=True)
    run.add_argument("--workload", required=True)
    run.add_argument("--pod", required=True)
    run.add_argument("--metrics-url", required=True)
    run.add_argument("--slo-profile", required=True)
    run.add_argument("--output-dir", default="artifacts/recovery")
    run.add_argument("--timeout-s", type=float, default=300.0)
    run.add_argument("--healthy-samples", type=int, default=3)
    run.add_argument("--fault-at-s", type=float, default=0.0)
    run.add_argument("--baseline-goodput", type=float, default=1.0)
    run.add_argument("--degraded-goodput", type=float, default=1.0)
    run.add_argument(
        "--execute",
        action="store_true",
        help="execute the destructive Pod deletion; omitted means server-side dry-run",
    )


def run_recovery_cli(args: argparse.Namespace) -> int:
    try:
        from kubernetes import client, config
    except ImportError as exc:
        raise SystemExit(
            "live recovery requires the optional 'kubernetes' package"
        ) from exc

    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()

    result = run_live_inference_recovery(
        config=LiveRecoveryConfig(
            namespace=args.namespace,
            pod=args.pod,
            workload=args.workload,
            timeout_s=args.timeout_s,
            dry_run=not args.execute,
        ),
        cluster=KubernetesPodFaultDriver(client.CoreV1Api()),
        metrics=HttpMetricsSource(args.metrics_url),
        slo_rules=load_inference_slo_rules(args.slo_profile),
        fault_at_s=args.fault_at_s,
        baseline_goodput=args.baseline_goodput,
        degraded_goodput=args.degraded_goodput,
        required_consecutive_healthy=args.healthy_samples,
    )

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "recovery-result.json").write_text(
        recovery_result_json(result), encoding="utf-8"
    )
    (output / "recovery-report.md").write_text(
        recovery_result_markdown(result), encoding="utf-8"
    )
    print(recovery_result_markdown(result), end="")
    return 0 if result.status.value == "PASS" else 2

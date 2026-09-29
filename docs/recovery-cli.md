# Recovery CLI

The operator-facing entry point is part of the existing `ai-factory` command:

```bash
ai-factory recovery run \
  --namespace inference \
  --workload vllm \
  --pod vllm-0 \
  --metrics-url http://vllm:8000/metrics \
  --slo-profile acceptance/examples/inference-interactive-slo.json \
  --output-dir artifacts/recovery
```

This is a Kubernetes server-side dry-run by default.

A destructive experiment requires the explicit `--execute` flag:

```bash
ai-factory recovery run ... --execute
```

The command writes `recovery-result.json` and `recovery-report.md`. The Kubernetes Python client is an optional runtime dependency for this command; other toolkit commands remain usable without it.

The example SLO profile in this repository is a test fixture, not a universal production threshold. Real acceptance runs should supply workload/site-specific SLO and goodput values.

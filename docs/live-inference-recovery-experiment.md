# Live inference recovery experiment

The first end-to-end experiment orchestrator composes the existing boundaries rather than reimplementing them.

```text
explicit fault request
      ↓
Kubernetes Pod deletion
      ↓
replacement Pod Ready
      ↓
stable vLLM SLO recovery watcher
      ↓
RecoveryWindow
      ↓
pod recovery time / SLO recovery time / goodput loss
      ↓
JSON + Markdown acceptance receipt
```

## Safety

The default configuration remains dry-run. A dry-run records the Kubernetes server-side dry-run request and returns before waiting for a replacement Pod or claiming recovery measurements.

A destructive experiment requires an explicit `dry_run=False` configuration and appropriately scoped Kubernetes credentials.

## Evidence boundary

The orchestrator does not redefine Kubernetes readiness, Prometheus parsing, histogram percentiles, SLO evaluation, or recovery math. Those remain in their existing modules. This layer only composes them into one experiment result suitable for report persistence.

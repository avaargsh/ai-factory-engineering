# Kubernetes + vLLM live providers

The live recovery boundary now has concrete provider implementations without making destructive execution the default.

## Kubernetes

`KubernetesPodFaultDriver` accepts an already-configured CoreV1 API client. Authentication remains the responsibility of the official Kubernetes client configuration, so callers can use kubeconfig outside the cluster or a ServiceAccount in-cluster.

Dry-run Pod deletion is mapped to Kubernetes server-side `dryRun=All`. Real deletion is only requested when the caller explicitly sets `dry_run=False`.

Replacement readiness is observed from Pod Ready conditions for the declared workload selector. This is still only the Kubernetes recovery clock; service SLO recovery remains a separate inference metric.

## vLLM

`HttpMetricsSource` fetches the Prometheus-compatible metrics endpoint. The returned text is intentionally raw so the existing vLLM telemetry and histogram adapters remain the single normalization path.

A production wrapper should supply an explicit metrics URL such as the serving endpoint's `/metrics`, network policy/TLS/auth as required by the deployment, and an appropriately scoped Kubernetes client.

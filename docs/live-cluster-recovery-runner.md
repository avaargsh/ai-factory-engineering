# Live cluster recovery runner

This module is the boundary between deterministic acceptance semantics and a real Kubernetes/vLLM environment.

The runner coordinates two provider interfaces:

- `ClusterFaultDriver`: request Pod deletion and wait for replacement readiness.
- `MetricsSource`: scrape the serving runtime telemetry.

Destructive behavior is opt-in. `LiveRecoveryConfig.dry_run` defaults to `true`; dry-run records fault intent and telemetry but does not wait for a replacement Pod because no fault was executed.

A concrete Kubernetes driver may use kubeconfig/in-cluster authentication and the CoreV1 Pod API. A concrete vLLM source should read the Prometheus-compatible `/metrics` endpoint. Provider credentials and cluster mutation permissions stay outside the acceptance evaluator.

The next integration step is to feed the receipt's metrics text through the existing vLLM histogram adapter and combine Kubernetes timestamps with the existing inference recovery Golden Run.

# v0.1.0 Release Notes

## AI Factory Engineering v0.1.0

The first release candidate establishes an executable cross-layer commissioning contract for AI infrastructure.

### Highlights

- Normalize DCGM, NVLink, RDMA, NCCL and inference-SLO observations into EvidenceBundles.
- Preserve raw command artifacts and provenance.
- Evaluate a fail-closed Compute -> Fabric -> Runtime gate DAG.
- Produce content-addressed AcceptanceArtifacts.
- Verify deterministic replay and reference attestations.
- Run a zero-hardware deterministic demo with `make demo`.
- Expose an explicit operator-controlled real-command path with `make smoke MANIFEST=...`.

### Important boundaries

This release does not claim a live 576-GPU commissioning result, universal performance thresholds, or production-grade KMS/Sigstore signing. It is a reference engineering toolkit for building repeatable cross-layer acceptance.

### Upgrade policy

v0.x contracts may evolve. Changes that affect evidence schemas, gate semantics or artifact digests should be treated as compatibility-sensitive.

# 576-GPU Cross-Layer Commissioning Demo

This demo exercises the reference vertical slice rather than individual helpers:

```text
DCGM / NVLink -> RDMA / NCCL -> Inference SLO
              -> Gate DAG -> AcceptanceDecision
              -> AcceptanceArtifact -> Attestation -> Verification
```

Run from the repository root:

```bash
python examples/576_gpu_commissioning_demo.py
```

The checked-in outcomes are a deterministic golden fixture. They are not claimed to be measurements from a live 576-GPU cluster. Replace the evidence references and outcomes with collector-produced EvidenceBundles for a real commissioning run.

The demo key is intentionally test-only. Production attestation should use an external signer such as KMS or Sigstore/Cosign while preserving the artifact digest contract.

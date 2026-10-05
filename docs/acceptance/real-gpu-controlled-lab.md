# Real GPU controlled-lab

The next AI Factory acceptance milestone is a **real hardware run**, not another
synthetic fixture.

## Boundary

This path is intentionally manual and runs only on a trusted self-hosted runner
labelled:

```text
self-hosted
gpu-controlled-lab
```

It is **not** triggered by pull requests. A public-repository PR must never gain
automatic execution on a GPU host.

The site-owned manifest must set:

```json
"evidenceMode": "real-hardware"
```

and include both:

- a GPU telemetry collector (`gpu_csv` or `dcgm`);
- an `inference` collector backed by the actual runtime benchmark.

The repository template remains provider-neutral: NVIDIA, MetaX, or another GPU
stack may use a site-owned wrapper that emits the canonical GPU CSV contract.
Do not add fake vendor support by parsing an unverified CLI format in this
repository.

## Local execution on the GPU host

```bash
export MANIFEST=/opt/ai-factory/site-lab.json
export ATTESTATION_KEY_ID=commissioning-lab
export AI_FACTORY_ATTESTATION_SECRET='...'
export LAB_ARTIFACTS=.artifacts/real-gpu-$(date -u +%Y%m%dT%H%M%SZ)

bash scripts/run_real_gpu_controlled_lab.sh
```

In addition to the existing raw collector bytes, EvidenceBundles,
AcceptanceArtifact and AcceptanceAttestation, the runner writes:

- `host-provenance.json` — source commit, manifest digest, host platform and
  resolved collector executables;
- `real-hardware-receipt.json` — source/manifest/provenance digests plus the
  accepted run identity.

These records make the claim explicit: the acceptance artifact came from a
declared real-hardware run. They still do not magically prove the operator's
hardware identity; the retained raw collector output and site asset references
remain the evidence that reviewers must inspect.

## GitHub manual run

Use the `real-gpu-controlled-lab` workflow only after registering a trusted GPU
runner and configuring the protected `controlled-lab` environment with:

- variable `AI_FACTORY_ATTESTATION_KEY_ID`;
- secret `AI_FACTORY_ATTESTATION_SECRET`.

The manifest should be site-owned. Do not commit production credentials or
private topology secrets to this public repository.

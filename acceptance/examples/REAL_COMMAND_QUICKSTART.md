# Controlled-lab commissioning quick start

The default real-command template is now the minimum evidence path required for a
controlled lab:

```text
real GPU telemetry
  -> Compute Gate
real inference benchmark summary
  -> Runtime Gate
  -> AcceptanceArtifact
  -> AcceptanceAttestation
```

Fabric is explicitly listed as **Not Evaluated** in the minimum template. If the
lab supports multi-node RDMA/NCCL validation, add the existing RDMA/NCCL
AcceptanceTests and site-bound baselines as a Fabric gate. Do not silently mark an
unavailable layer PASS.

## 1. Copy and bind the template

Copy:

`controlled-lab-minimum.template.json`

or the compatibility alias:

`real-command-commissioning.template.json`

to a site-owned manifest. Replace every `CHANGE-ME` value.

The GPU command in the template uses `nvidia-smi --query-gpu` and normalizes it
to the repository's canonical GPU CSV contract.

The inference command is intentionally provider-neutral. Your benchmark wrapper
must print exactly one JSON object to stdout containing numeric:

```json
{
  "ttft_p95_ms": 120.5,
  "tpot_p95_ms": 31.2,
  "success_ratio": 0.995
}
```

It may wrap vLLM, SGLang, GenAI-Perf, a custom load generator, or another approved
runtime benchmark. The AI Factory collector consumes the normalized metrics, not
a vendor-specific CLI format.

## 2. Replace fail-closed SLO baselines

The files under `controlled-lab-baselines/*.template.json` intentionally cannot
pass a real run. Copy them to site-owned baseline files and set the approved
workload-specific thresholds for:

- TTFT P95
- TPOT P95
- request success ratio

Do not copy thresholds from another topology.

## 3. Preflight

```bash
ai-factory validate-lab-manifest /path/to/lab.json
```

Preflight rejects:

- any remaining `CHANGE-ME`
- placeholder SLO baselines
- missing Compute or Runtime gates
- missing version matrix
- missing asset references

## 4. Run, seal and verify

```bash
export AI_FACTORY_ATTESTATION_SECRET='...'

make lab-smoke \
  MANIFEST=/path/to/lab.json \
  ATTESTATION_KEY_ID=commissioning-lab \
  LAB_ARTIFACTS=.artifacts/lab-20260930T160000Z
```

Outputs under `.artifacts/lab/` include:

- per-test raw stdout and stderr with SHA-256 checksums
- EvidenceBundles with version/asset provenance
- `commissioning-run.json`
- `commissioning-report.md`
- `acceptance-artifact.json`
- `acceptance-attestation.json`

The command fails closed on collector errors, missing evidence, threshold
failures, invalid artifact replay, or attestation verification failure.

This is a controlled-lab path, not fleet-scale certification.


## Evidence retention

Use a new `LAB_ARTIFACTS` directory for every controlled-lab execution. The
`lab-smoke` target refuses to reuse an existing path and never removes prior
lab evidence automatically.

Collector process failures and timeouts remain fail-closed, but any stdout and
stderr captured before the failure are written to the selected run directory
before the error is returned. This preserves diagnostic evidence from failed
hardware/runtime runs instead of retaining only successful runs.

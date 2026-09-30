# AI Factory Engineering

Cross-layer commissioning and acceptance for AI infrastructure: prove that **Compute -> Fabric -> Runtime** can sustain declared workload SLOs, then seal the result as replayable evidence.

The project focuses on the engineering gap between "the hardware is installed" and "the AI factory is actually delivering useful, measurable output."

## Why this exists

A modern GPU cluster can look healthy at one layer and still fail as a system:

- GPUs pass basic health checks while NVLink/NVSwitch underperform.
- RDMA links are up while retry/symbol errors destroy collective performance.
- NCCL bandwidth is acceptable while inference TTFT/TPOT misses the workload SLO.
- Individual checks pass, but there is no signed cross-layer acceptance artifact tying evidence to a decision.

This repository turns those checks into one acceptance chain.

## Golden path

```text
Native collector commands
  -> raw stdout/stderr artifacts
  -> EvidenceBundle
  -> schema validation
  -> TestOutcome
  -> Compute Gate
  -> Fabric Gate
  -> Runtime Gate
  -> AcceptanceDecision
  -> AcceptanceArtifact
  -> attestation
  -> verification / replay
```

Reference evidence adapters currently cover:

- DCGM GPU health
- NVLink health/bandwidth
- RDMA port/error health
- NCCL collective bandwidth/correctness
- Inference SLO: TTFT P99, TPOT P99, success ratio

Thresholds are declared inputs. The framework does not hard-code a universal "good" NCCL bandwidth or latency target.

## Five-minute demo

Requirements: Python 3.11+.

```bash
make setup
make test
make demo
```

The deterministic demo requires no GPU hardware and writes:

```text
.artifacts/demo/acceptance.json
```

It demonstrates the complete acceptance contract using repository fixtures.

## Real-command smoke path

Copy the commissioning template and replace every site-specific placeholder:

```bash
cp acceptance/examples/real-command-commissioning.template.json \
   acceptance/examples/my-site-commissioning.json
```

Then run:

```bash
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

The manifest can invoke approved site commands such as `dcgmi`, `nvidia-smi nvlink`, RDMA tooling and `nccl-tests`. Raw command output is retained as evidence.

## Architecture

```text
                    AI Factory Acceptance Plane

  Compute                    Fabric                     Runtime
┌────────────┐            ┌────────────┐            ┌──────────────┐
│ DCGM       │            │ RDMA       │            │ Inference SLO│
│ NVLink     │            │ NCCL       │            │ TTFT / TPOT  │
└─────┬──────┘            └─────┬──────┘            └──────┬───────┘
      │                         │                          │
      └──────────────┬──────────┴──────────────┬──────────┘
                     ▼                         ▼
               EvidenceBundle            Gate DAG
                     │                         │
                     └──────────────┬──────────┘
                                    ▼
                           AcceptanceDecision
                                    ▼
                           AcceptanceArtifact
                                    ▼
                               Attestation
                                    ▼
                         Verification / Replay
```

## Design principles

- **Fail closed.** Missing or incomplete evidence must not silently become PASS.
- **Evidence first.** Preserve raw artifacts and provenance before deriving acceptance.
- **Cross-layer, not device-only.** The acceptance unit is the delivered system/workload path.
- **Thresholds are explicit.** Site topology and contractual SLOs define acceptance floors.
- **Portable runner boundary.** Native commands stay outside domain logic.
- **Replayable decision.** Acceptance artifacts are content-addressed and verifiable.

## Repository map

```text
src/ai_factory_engineering/   acceptance, collectors, runner, reports, replay
acceptance/tests/             AcceptanceTest specs
acceptance/examples/          plans, templates and reference manifests
examples/                     runnable demos
tests/                        unit, contract and integration tests
casebook/                     reference engineering cases
docs/                         architecture and AI Factory engineering notes
```

## External acceptance contract

`AcceptanceArtifact` is the portable output boundary for consumers outside this
repository. Its JSON contract is published at
`schemas/acceptance-artifact.schema.json`.

External control planes should consume the sealed artifact rather than re-run
AI Factory threshold logic:

```text
raw evidence
  -> AI Factory Gate DAG
  -> AcceptanceArtifact
       + caseId
       + disposition / accepted
       + per-gate status
       + evidenceRefs
       + content digest
  -> external evidence binding
```

Schema validation establishes the artifact shape; the artifact digest establishes
content integrity. Production trust/authenticity remains a separate attestation
concern and is not implied by digest verification alone.

## Current status

v0.1 release candidate.

Implemented:

- native collector execution boundary
- EvidenceBundle schema/validation
- DCGM/NVLink/RDMA/NCCL/inference adapters
- fail-closed cross-layer Gate DAG
- deterministic 576-GPU reference acceptance demo
- AcceptanceArtifact digest + reference attestation
- real-command commissioning manifest template
- `make demo` / `make smoke` developer workflow

Not yet claimed:

- a live 576-GPU production commissioning run
- universal performance thresholds
- production KMS/Sigstore/Cosign signing
- hardware-specific parser coverage for every vendor/version
- replacement for vendor diagnostics or site commissioning procedures

See [DEVELOPMENT.md](DEVELOPMENT.md) and [RELEASE_READINESS.md](RELEASE_READINESS.md).

## Scope

The broader engineering model remains:

```text
MW -> Facility -> Rack/Pod -> GPU -> Fabric -> Cluster
   -> Runtime -> Model -> Token / Model Progress -> SLO / Economics
```

This repository currently concentrates executable code around the cross-layer commissioning and acceptance portion of that chain.

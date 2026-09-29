# AI Factory Engineering

**Cross-layer commissioning and acceptance toolkit for AI factories — from facility power and GPU fabric to Kubernetes scheduling, LLM inference SLOs, and failure recovery.**

This repository asks one engineering question:

> Can the designed infrastructure continuously turn power, cooling, GPUs and network capacity into **measurable, SLO-compliant AI output**?

It combines design intent, collectors, evidence, acceptance rules and recovery experiments instead of treating Facility, GPU, Fabric, Kubernetes and inference as unrelated silos.

## Engineering spine

```text
MW / Facility
    ↓
Rack / Power / Cooling
    ↓
GPU / HBM / NVLink
    ↓
RoCE / IB / RDMA / NCCL
    ↓
Kubernetes GPU Scheduling
    ↓
vLLM Inference Runtime
    ↓
TTFT / TPOT / Goodput
    ↓
Failure Recovery
    ↓
Acceptance Evidence
```

The acceptance loop is:

```text
DesignIntent
   ↓
CommissioningPlan
   ↓
Collector → Raw Artifact → SHA-256
   ↓
EvidenceBundle
   ↓
MetricRule / SLO
   ↓
TestOutcome
   ↓
Acceptance / Re-validation
```

## What is implemented

| Layer | Executable evidence / acceptance |
| --- | --- |
| Facility / capacity | MW → IT capacity → GPU capacity → productive GPU-hours / tokens |
| GPU | DCGM evidence and H100 SXM acceptance profile |
| Fabric | NVLink, RDMA counters, NCCL scale-out evidence |
| Kubernetes | GPU scheduling / gang-admission acceptance |
| Inference | vLLM Prometheus telemetry, TTFT / TPOT percentile SLO evaluation |
| Reliability | Pod-loss injection, replacement readiness, stable SLO recovery, recovery-time / goodput-loss evidence |
| Reporting | JSON evidence plus Markdown acceptance reports |

## 576-GPU commissioning Golden Run

The repository includes a deterministic 576-GPU reference scenario:

- `acceptance/examples/576-gpu-design-intent.json`
- `acceptance/examples/576-gpu-commissioning-plan.json`
- `acceptance/examples/576-gpu-golden-outcomes.json`

These files are **fixtures for exercising the acceptance contract**. They are not claimed as measurements from a production 576-GPU cluster.

The important boundary is:

```text
vendor theoretical peak ≠ site acceptance threshold
fixture evidence        ≠ measured production evidence
Pod Ready               ≠ inference SLO recovered
raw token throughput    ≠ SLO-compliant goodput
```

## Quick start

Requires Python 3.11+.

```bash
python -m pip install -e ".[dev]"
pytest -q
```

The package installs the `ai-factory` CLI.

### Capacity model

```bash
ai-factory capacity \
  --contract-mw 8 \
  --pue 1.2 \
  --rack-kw 100 \
  --gpus-per-rack 8
```

### Evaluate acceptance evidence

```bash
ai-factory evaluate \
  acceptance/examples/fabric-nccl.json \
  acceptance/examples/fabric-nccl-evidence.json
```

### Live Kubernetes + vLLM recovery — safe default

The recovery command is **non-destructive by default** and sends a Kubernetes server-side dry-run request:

```bash
ai-factory recovery run \
  --namespace inference \
  --workload vllm \
  --pod vllm-0 \
  --metrics-url http://vllm:8000/metrics \
  --slo-profile acceptance/examples/inference-interactive-slo.json \
  --output-dir artifacts/recovery
```

A real Pod deletion requires explicit opt-in:

```bash
ai-factory recovery run ... --execute
```

The command persists:

```text
artifacts/recovery/
├── recovery-result.json
└── recovery-report.md
```

A destructive run is intended to measure two different clocks:

```text
fault
  ↓
replacement Pod Ready       ← Kubernetes recovery
  ↓
TTFT / TPOT healthy
  ↓
N consecutive healthy samples
  ↓
Service SLO Recovered       ← workload recovery
```

## Architecture

The project intentionally keeps responsibilities narrow:

- **Collectors** acquire raw DCGM / NVLink / RDMA / NCCL / Prometheus evidence.
- **Evidence adapters** normalize measurements without embedding acceptance policy.
- **Profiles / DesignIntent** define site- or workload-specific expectations.
- **Evaluators** produce deterministic PASS / FAIL / ERROR outcomes.
- **Recovery runner** composes Kubernetes fault injection and vLLM SLO observation; it is not a chaos platform or orchestrator.
- **Reports** make the result replayable and reviewable.

## Safety and evidence rules

The repository follows several fail-closed rules:

1. Missing or `TBD` acceptance baselines do not silently pass.
2. Numeric thresholds require explicit comparison semantics and scope.
3. Different Prometheus histogram labelsets must not be silently treated as one workload.
4. Kubernetes Pod readiness is not sufficient evidence of inference recovery.
5. Destructive fault injection is opt-in; dry-run is the default.
6. Recovery thresholds come from workload/site profiles, not universal constants.
7. Golden fixtures are labeled fixtures rather than represented as production measurements.

## Repository map

```text
acceptance/             baselines, profiles, examples and test matrix
src/ai_factory_engineering/
                        collectors, evidence, evaluators, recovery and CLI
docs/                   architecture and engineering notes
casebook/               reference designs / cases
checklists/             design, go-live and expansion checks
tests/                  deterministic contract and regression tests
```

Useful implementation notes:

- `docs/inference-recovery-golden-run.md`
- `docs/live-inference-recovery-experiment.md`
- `docs/recovery-cli.md`
- `docs/slo-recovery-watcher.md`
- `docs/live-providers.md`

## Scope / non-goals

This is an engineering acceptance framework, not a replacement for Kubernetes, Prometheus, DCGM, NCCL, vLLM, a scheduler, a benchmark suite, or a chaos platform.

The project is strongest when it answers cross-layer questions such as:

- Did the GPU fabric deliver the expected workload envelope?
- Did Kubernetes place the workload correctly?
- Did inference stay inside TTFT / TPOT SLOs?
- After a Pod loss, when was compute ready versus when was the service actually healthy?
- How much productive GPU time or goodput was lost?

## Project direction

Current work is intentionally focused on **evidence-backed GPU / inference commissioning** rather than adding more architecture layers. The next meaningful step is running the existing live recovery path against controlled Kubernetes + vLLM environments and replacing fixtures with clearly provenance-tagged measured evidence.

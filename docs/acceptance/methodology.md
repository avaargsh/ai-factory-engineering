# Cross-Layer Acceptance Methodology

## Objective

Prove that real AI workloads can sustainably deliver contractual performance **inside the designed power and thermal envelope**.

## Acceptance stack

```text
Facility
 -> Rack
 -> Server
 -> GPU
 -> Fabric
 -> Storage
 -> Cluster
 -> Runtime
 -> Model
 -> Real Workload
 -> SLO / Goodput
```

## Test pyramid

1. Component Test
2. Subsystem Test
3. Integrated System Test
4. AI Compute Test
5. Runtime Test
6. Real Workload Acceptance
7. Fault Injection / Recovery
8. Sustained Run

## Workload coverage

A serious acceptance plan should include representative:

- dense-model workloads,
- MoE,
- long context,
- multimodal where relevant,
- multi-node collectives,
- training and/or inference,
- sustained rather than only burst runs.

## Evidence package

Every pass/fail should link to:

- topology snapshot,
- firmware / driver / runtime versions,
- configuration snapshot,
- raw benchmark data,
- telemetry,
- logs / traces,
- test window,
- retest evidence.

## Principle

The deliverable is not "N GPUs installed."

The deliverable is an independently reproducible statement of **Usable / Productive AI Capacity**.

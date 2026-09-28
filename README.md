# AI Factory Engineering

A docs-first engineering knowledge base and reference architecture for turning **MW of power into sustainable, measurable AI output**.

The organizing question is:

> How does Energy / MW flow through Facility, GPU, Fabric, Runtime and Model layers to become Productive GPU Hours, Model Progress, Useful Tokens, SLO and economics?

## Engineering spine

```text
Energy / MW
  -> Facility
  -> Rack / Pod
  -> GPU
  -> Fabric / Storage
  -> Cluster
  -> Runtime
  -> Model
  -> Token / Model Progress
  -> SLO
  -> Economics
```

Lifecycle:

```text
Planning -> Design -> Build -> Commissioning -> Operations / SRE
         -> Upgrade / Expansion -> Continuous Re-validation
```

## Five-layer model

1. **Facility** — power, cooling, rack, structure and failure domains
2. **Compute** — GPU, HBM, PCIe, NUMA, NVLink / NVSwitch
3. **Fabric** — InfiniBand / RoCE, RDMA, NCCL and storage data paths
4. **Runtime** — Kubernetes, scheduling, training / inference runtime and KV
5. **Workload** — training, inference, MoE, long context, multimodal and Agent workloads

## Core engineering models

- **Capacity Waterfall** — Installed -> Design -> Usable -> Allocatable -> Productive
- **Multi-Roof Capacity** — capacity is bounded by the tightest Power / Cooling / Fabric / Storage / Runtime / Workload roof
- **Fault-to-Token / Fault-to-Progress** — map infrastructure faults to lost productive output
- **Engineering Digital Thread** — requirement -> design -> config -> test -> telemetry -> incident -> change -> re-validation
- **Cross-Layer Acceptance** — prove real workloads can sustain contractual performance inside the designed power/thermal envelope

## Repository scope

```text
docs/architecture/      system architecture and cross-layer models
docs/facility/          power, cooling, rack and retrofit
docs/compute/           GPU, topology and accelerator stack
docs/fabric/            RoCE / IB / RDMA / NCCL
docs/runtime/           Kubernetes, training and inference
docs/reliability/       SRE, fault models and observability
docs/acceptance/        commissioning and workload acceptance
docs/economics/         capacity and unit economics
casebook/               reference designs and field cases
checklists/              design / go-live / expansion checklists
```

## Status

Private incubation repository. The current phase converts long-form research into canonical engineering notes, checklists, test matrices and reference architectures before public release.

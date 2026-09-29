# Roadmap

## v0.1 — Canonical engineering model
- [x] engineering spine
- [x] Capacity Waterfall
- [x] Multi-Roof model
- [x] Fault-to-Token / Fault-to-Progress
- [x] Cross-Layer Acceptance methodology
- [x] design and go-live checklists
- [x] initial acceptance test matrix

## v0.2 — Reference architectures
- [ ] power/cooling scalable-unit diagram
- [ ] GPU/NVLink/scale-out fabric diagram
- [ ] Kubernetes training platform diagram
- [ ] large-scale inference P/D/EPD diagram
- [ ] 576-GPU casebook expansion

## v0.3 — Acceptance toolkit
- [x] machine-readable AcceptanceTest specification
- [x] EvidenceBundle schema
- [x] schema validator
- [x] fail-closed threshold/evidence evaluator
- [x] markdown acceptance report
- [x] multi-test Acceptance Run
- [x] fail-closed run aggregation
- [x] run-level markdown report
- [ ] NCCL/RDMA collection scripts
- [ ] DCGM / Kubernetes evidence collectors
- [ ] workload benchmark adapters

## v0.4 — Time-series capacity and energy
- [x] first-order MW -> Rack -> GPU -> Productive GPUh model
- [x] optional Tokens/GPU-hour and Tokens/kWh projection
- [x] generic time-slice engine
- [x] 8760 hourly model support
- [x] 35040 15-minute model support
- [x] variable electricity price / load / PUE inputs
- [x] energy cost per 1M Tokens
- [ ] brownfield retrofit model
- [ ] broader unit-economics cost layers


## v0.5 — Cross-Layer Commissioning
- [x] Gate schema and runtime contract
- [x] dependency-aware Gate evaluation
- [x] distinguish FAIL / ERROR / BLOCKED
- [x] fail-closed missing evidence semantics
- [x] Facility Gate Golden Path profiles
- [x] negative regression tests for threshold miss, collector error, missing evidence and dependency failure
- [x] CommissioningPlan execution DAG
- [x] DesignIntent schema
- [x] evidence provenance and replay metadata
- [x] Gate-level report aggregation

## v0.6 — GPU + Fabric Commissioning
- [ ] DCGM / PCIe / NVLink evidence collectors
- [ ] RDMA / RoCE collector
- [ ] NCCL benchmark adapter
- [ ] topology evidence
- [ ] collective efficiency model

## v0.7 — Workload Commissioning
- [ ] Kubernetes placement evidence
- [ ] gang / topology acceptance
- [ ] distributed runtime acceptance
- [ ] training and inference workload adapters
- [ ] Token SLO Gate

## v0.8 — Capacity × Reliability
- [ ] fault-domain model
- [ ] fault -> blast radius
- [ ] fault -> lost productive GPU-hours
- [ ] fault -> lost tokens / model progress
- [ ] Effective Compute Efficiency

## v0.9 — AI Factory Control Plane
- [ ] Desired State -> Commission -> Observe -> Evaluate -> Decide -> Remediate -> Replay

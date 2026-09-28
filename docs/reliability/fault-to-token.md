# Fault-to-Token / Fault-to-Progress

## Why

A device alarm is not an operational outcome.

AI Factory reliability should answer:

> How much productive capacity did this fault remove, for how long, and what workload/SLO/economic impact followed?

## Failure domains

```text
Grid / Utility
 -> Power Block
 -> Cooling Loop
 -> Rack / Pod
 -> Server / GPU / NIC
 -> Leaf / Spine / Rail
 -> Storage
 -> Kubernetes
 -> Runtime
 -> Model / Workload
```

## Fault record

Each fault should capture:

- trigger,
- detection signal,
- affected entities,
- blast radius,
- degradation mode,
- Productive Capacity loss,
- recovery path,
- evidence,
- re-validation result.

## Example

```text
PFC / congestion anomaly
 -> RDMA retry / pause
 -> NCCL tail
 -> step-time increase
 -> straggler amplification
 -> MFU / Goodput loss
```

## Reliability metrics

- MTTD
- MTTR
- MTBF
- lost GPU hours
- straggler rate
- recovery time
- error-budget burn
- recurrence rate

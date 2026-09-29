# Inference Pod-loss recovery acceptance

The first reliability fault is intentionally narrow and reproducible: delete one serving Pod while a declared steady inference load is running.

```text
steady-state goodput baseline
          ↓
      delete Pod
          ↓
Kubernetes replacement / readiness
          ↓
vLLM queue + TTFT/TPOT + request success
          ↓
SLO-compliant goodput recovers
```

Two recovery clocks are retained:

1. **Pod recovery time** — fault to replacement Pod Ready.
2. **SLO recovery time** — fault to the point at which the serving workload again satisfies its declared SLO.

The second is the service-level recovery metric. A Pod can be Ready while model warmup, cache state, queue backlog, or traffic redistribution still leaves user-visible latency degraded.

The profile also records goodput loss relative to the pre-fault baseline. Numeric recovery-time and loss thresholds are intentionally left to a workload/site reliability profile.

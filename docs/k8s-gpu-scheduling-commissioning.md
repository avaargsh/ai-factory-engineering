# Kubernetes GPU scheduling commissioning

Scheduling acceptance sits between fabric health and workload SLO validation.

```text
GPU health
   ↓
Fabric health / NCCL
   ↓
GPU scheduling admission + topology placement
   ↓
Distributed workload ready
   ↓
Training / inference SLO
```

The first contract validates correctness before performance:

- requested GPU count equals scheduled GPU count;
- all declared workload members become ready;
- topology placement is captured as evidence;
- partial placement is never reported as a successful gang admission.

Admission latency and complete-workload startup latency are measured but are not given repository-wide pass thresholds. Those envelopes must be declared for the installed cluster and workload class.

The profile is intentionally provider-neutral. Kueue Topology Aware Scheduling is a concrete implementation target, but any scheduler that can provide equivalent gang/admission/topology evidence can satisfy the contract.

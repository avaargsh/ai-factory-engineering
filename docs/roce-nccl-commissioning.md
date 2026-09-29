# H100 RoCEv2 / NCCL fabric commissioning

Fabric commissioning is staged rather than reduced to one bandwidth number.

```text
NIC / RoCE counters
        ↓
transport health
        ↓
NCCL collective tests
        ↓
topology/reference comparison
        ↓
fabric acceptance
```

## Transport signals

The collector normalizes transmit discards, receive errors, ECN-marked packets, CNPs, and PFC pause duration. Error/discard counters and congestion-control counters are intentionally not treated as the same semantic class.

ECN/CNP activity can show congestion control operating under load; it is not automatically a failure. PFC pause duration similarly needs a declared observation window and workload envelope. Site acceptance must therefore declare the relevant operator/value/unit/scope rather than hard-code a generic zero for every counter.

## Collective performance

NCCL acceptance must retain the dimensions that materially change performance: collective, message size, node/GPU count, topology/rail, and placement. The repository records algbw/busbw measurements but does not invent a universal 576-GPU pass line.

The transport-health stage must pass before collective performance is accepted. This prevents a high aggregate benchmark number from masking unhealthy loss/congestion behavior.

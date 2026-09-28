# Training and Inference Runtime

## Training objective

Training should be optimized for **Model Progress / Time**, not GPU utilization alone.

Useful metrics:

- step time
- tokens/s or samples/s
- MFU
- scaling efficiency
- checkpoint duration
- restart duration
- lost GPU hours

## Inference objective

Inference should be optimized for **SLO-compliant Goodput**.

Core metrics:

- TTFT
- TPOT
- end-to-end latency
- queueing delay
- tokens/s
- Goodput
- error rate
- availability

## Three scheduling layers

```text
Cluster Scheduler
    |
Request Router
    |
Runtime Scheduler
```

Examples:

- Kubernetes/Kueue/Volcano/Kai decide placement and admission.
- a request router selects a serving replica or P/D pool.
- vLLM/SGLang performs continuous batching and KV-aware scheduling.

Local optimization at one layer can damage the system if the other layers are ignored.

## P/D and EPD

Prefill and Decode have different resource profiles. Disaggregation can improve efficiency but introduces:

- KV transfer,
- additional network roofs,
- more queues,
- more lifecycle states,
- more failure modes.

Use a release gate: adopt the added complexity only if real workloads improve SLO Goodput, GPU efficiency or isolation.

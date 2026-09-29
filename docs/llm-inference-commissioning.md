# LLM inference runtime commissioning

Inference acceptance answers a different question from pod health or GPU utilization:

> Does the admitted serving workload produce useful tokens within the declared user-facing SLO?

```text
Kubernetes admission
        ↓
model/runtime ready
        ↓
declared load profile
        ↓
request observations
        ├── success
        ├── TTFT
        ├── TPOT
        └── output tokens
        ↓
SLO filter
        ↓
SLO-compliant requests / tokens
        ↓
goodput evidence
```

## Comparable evidence

Every run must retain runtime/model identity and the load profile. Concurrency and request/input/output-token distributions materially affect TTFT, TPOT, queueing, throughput, and KV-cache pressure, so latency results without workload context are not acceptance evidence.

## Throughput is not goodput

Raw output tokens per second can increase while user-visible latency degrades. The first executable goodput primitive therefore counts only successful requests whose TTFT and TPOT satisfy the declared workload SLO.

The repository does not declare universal TTFT/TPOT targets. Those belong to a workload/site profile and can differ by model, context length, hardware, parallelism strategy, and service tier.

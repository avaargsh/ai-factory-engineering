# Inference recovery golden run

This repository-level fixture proves the reliability contract without pretending to be measured production hardware data.

```text
baseline TTFT/TPOT SLO PASS
        ↓
fault timestamp
        ↓
replacement Pod Ready
        ↓
service SLO restored
        ↓
recovery measurements
        ↓
Golden Run PASS
```

A run cannot pass when:

- the pre-fault baseline was already outside SLO;
- recovery evidence is incomplete or inconsistent;
- the replacement Pod is Ready but recovered TTFT/TPOT still violates the declared workload SLO.

The deterministic fixture exists to lock evaluation semantics. A live-cluster runner can later replace the fixture inputs with Kubernetes events and vLLM telemetry without changing the acceptance contract.

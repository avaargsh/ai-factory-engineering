# Inference SLO outcome

The first executable normal-state inference acceptance path is:

```text
vLLM /metrics
   ↓
Prometheus histogram buckets
   ↓
TTFT / TPOT percentile evidence
   ↓
explicit workload SLO rules
   ↓
TestOutcome PASS / FAIL
```

The example 200 ms TTFT p95 and 50 ms/token TPOT p95 values are deterministic test-fixture values only. They are not repository-wide production recommendations.

Production profiles must bind thresholds to model/runtime identity and a declared load profile. Missing percentile evidence fails closed.

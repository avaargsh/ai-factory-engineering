# vLLM histogram evidence

Request-level latency SLOs are derived from Prometheus histogram buckets rather than from gauges or ad-hoc averages.

The normalized evidence keeps these distributions distinct:

- TTFT: `vllm:time_to_first_token_seconds`
- request-level TPOT: `vllm:request_time_per_output_token_seconds`
- ITL: `vllm:inter_token_latency_seconds`
- queue time: `vllm:request_queue_time_seconds`
- E2E latency: `vllm:e2e_request_latency_seconds`

For each available histogram the adapter emits p50/p95/p99 in milliseconds. Quantiles are estimated from cumulative Prometheus buckets using the same linear-within-bucket model as Prometheus histogram quantiles.

This is evidence normalization, not an SLO declaration. Workload profiles still own acceptable TTFT/TPOT/queue/E2E thresholds.

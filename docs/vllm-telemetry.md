# vLLM telemetry adapter

The adapter normalizes serving-runtime telemetry into commissioning evidence without embedding SLO thresholds.

Initial server-level evidence:

- KV-cache usage
- running/waiting requests
- prompt and generation token counters
- prefix-cache hit ratio derived from hit/query counters

Latency distributions remain a separate concern because Prometheus histograms require bucket-aware aggregation. In particular, inter-token latency and request-level TPOT are not interchangeable measurement points. A later histogram adapter should preserve TTFT, request-level TPOT, ITL, queue time, and E2E latency as distinct distributions.

The adapter deliberately does not decide whether 75% KV usage, a cache-hit ratio, or a queue depth is good or bad. Those observations become evidence; workload/site SLO profiles own acceptance thresholds.

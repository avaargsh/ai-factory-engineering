# Stable inference SLO recovery watcher

A live recovery experiment must not declare service recovery from one lucky metrics scrape.

The watcher repeatedly:

1. scrapes raw vLLM Prometheus metrics;
2. derives request-level TTFT/TPOT percentile evidence;
3. evaluates the declared workload SLO;
4. requires a configurable number of consecutive healthy samples.

Any failed or incomplete SLO sample resets the consecutive-health counter. The receipt preserves every sample, its observation time, normalized measurements, and PASS/FAIL state.

Default semantics require three consecutive healthy samples at five-second polling intervals. These defaults are execution-stability settings, not workload SLO thresholds.

The recovery timestamp is the observation time of the final sample that completes the required healthy sequence. Timeout returns a non-recovered receipt with the sample history rather than inventing a recovery time.

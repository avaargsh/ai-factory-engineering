# Acceptance baseline status

The commissioning pipeline intentionally fails closed when an acceptance threshold has not been declared.

The current repository matrix contains one machine-actionable numeric health threshold:

- `GPU-001 / xid_ecc_errors = 0`

Facility, RDMA, NCCL, runtime, training, inference, and recovery thresholds remain `TBD`. They are specification gaps, not implicit passes.

A non-zero numeric value is also insufficient on its own because the comparison operator and baseline semantics must be explicit. For example, `goodput = 0.95` does not say whether the requirement is `>= 0.95`, a target band, or a normalized ratio against a reference run.

This keeps the path honest:

```text
DesignIntent / reference baseline
        ↓
explicit metric + operator + value
        ↓
MetricRule
        ↓
EvidenceBundle
        ↓
TestOutcome
        ↓
Commissioning Gate
```

# Multi-Test Acceptance Run

A single component test is not enough to accept an AI Factory.

The toolkit can aggregate multiple test/evidence pairs into one fail-closed Acceptance Run.

```text
Facility Tests
Compute Tests
Fabric Tests
Storage Tests
Cluster Tests
Runtime Tests
Workload Tests
Reliability Tests
       |
       v
Acceptance Run
       |
       +-- all pass -> PASS
       |
       +-- any fail -> FAIL
```

## Manifest

```json
{
  "runId": "site-a-go-live",
  "cases": [
    {
      "test": "fabric-nccl.json",
      "evidence": "fabric-nccl-evidence.json"
    }
  ]
}
```

Paths are resolved relative to the manifest.

## Principle

The run result is intentionally strict:

- one failed threshold fails that test,
- missing required evidence fails that test,
- one failed test fails the overall run.

A later policy layer may distinguish mandatory and advisory tests, but the reference implementation defaults to fail-closed.

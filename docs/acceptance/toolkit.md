# Acceptance Toolkit

The acceptance toolkit converts cross-layer engineering claims into reproducible test contracts.

## Flow

```text
AcceptanceTest
      |
      v
Real workload / fault test
      |
      v
EvidenceBundle
      |
      v
Schema validation
      |
      v
Threshold + evidence evaluation
      |
      v
PASS / FAIL
      |
      v
Acceptance Report
```

## AcceptanceTest

Defines:

- test identity and layer,
- objective and preconditions,
- workload,
- duration,
- measurable thresholds,
- required evidence,
- changes that trigger re-test.

## EvidenceBundle

Captures the exact execution environment:

- topology reference,
- version matrix,
- configuration references,
- numeric measurements,
- raw artifacts,
- test window.

## Fail closed

The evaluator fails when:

- a configured measurement is missing,
- a threshold is violated,
- required evidence is absent,
- the evidence bundle references the wrong test.

This is deliberate. "No data" is not treated as a pass.

## Example

```bash
ai-factory validate-test acceptance/examples/fabric-nccl.json
ai-factory validate-evidence acceptance/examples/fabric-nccl-evidence.json
```

The next step is to feed collected NCCL/RDMA/DCGM/Kubernetes evidence into the same bundle format rather than hand-editing measurements.

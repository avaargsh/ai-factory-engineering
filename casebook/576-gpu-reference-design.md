# 576-GPU Reference Design Casebook

This is a **learning/reference case**, not a procurement recommendation for a specific region or vendor.

## Purpose

Use a large multi-rack GPU system to force all layers onto one engineering drawing:

- compute racks,
- network racks,
- management/OOB,
- A/B power,
- CDU / cooling loops,
- NVLink/NVSwitch domains,
- dual-plane scale-out fabric,
- storage,
- workload placement.

## Questions the design must answer

### Capacity
- What is the usable IT MW?
- What is the continuous rack power and thermal envelope?
- How many GPUs remain Productive after fault/maintenance reserve?

### Failure
- What is lost when a leaf, rack PDU, CDU or power block fails?
- Does a single domain remove one rack, one Pod, or the whole cluster?

### Fabric
- Where are rail/plane boundaries?
- Which GPU/NIC links are topology-critical?
- What collective is used to validate scale?

### Operations
- How is OOB separated?
- How are firmware/config baselines captured?
- What is the safe maintenance and replacement path?

### Acceptance
- Which real workload proves the integrated design?
- What SLO/Goodput threshold defines pass/fail?
- Which telemetry forms the evidence package?

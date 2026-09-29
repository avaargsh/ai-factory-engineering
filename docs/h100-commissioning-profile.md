# H100 SXM 80GB commissioning profile

The H100 profile separates three concepts that must not be conflated:

1. **Vendor specification** — hardware capability context such as 80 GB HBM3, 3.35 TB/s memory bandwidth, 900 GB/s NVLink, and up to 700 W TDP.
2. **Vendor diagnostic result** — DCGM readiness/stress/bandwidth tests and their SKU-aware diagnostic semantics.
3. **Site acceptance baseline** — an explicit metric/operator/value/unit/scope requirement approved for the installed topology and workload.

A theoretical maximum is not automatically a commissioning pass threshold.

The initial profile therefore declares only the repository's existing zero-tolerance GPU health baseline. Memory bandwidth, NVLink bandwidth, and scale-out NCCL remain pending site/reference baselines until they are tied to measured topology-specific evidence.

For H100, DCGM can exercise PCIe/NVLink, memory, memory bandwidth, stress, power, NVBandwidth, and NCCL diagnostics. NVBandwidth is single-host. Scale-out NCCL acceptance remains a separate fabric-level workload.

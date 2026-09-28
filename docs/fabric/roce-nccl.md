# GPU Fabric: RoCE, RDMA and NCCL

## Fabric path

```text
GPU -> PCIe -> NIC -> Leaf -> Spine -> Leaf -> NIC -> GPU
```

Node-local communication may use NVLink/NVSwitch. Scale-out communication enters InfiniBand or Ethernet/RoCE.

## RoCE engineering

Typical mechanisms:

- RDMA
- PFC
- ECN
- DCQCN
- QoS
- ECMP
- queue / buffer engineering

The target is not "lossless everywhere." The target is predictable workload behavior under congestion and failure.

## NCCL

Acceptance must cover:

- AllReduce
- AllGather
- ReduceScatter
- All-to-All
- topology discovery
- rail / plane behavior
- tail latency
- retry / timeout
- scale efficiency

## MoE

Expert Parallelism turns network capacity into part of the model's compute path. All-to-All traffic can become a primary roof rather than a secondary concern.

## Test ladder

1. physical link / optics
2. L2/L3
3. RDMA
4. pairwise bandwidth
5. NCCL collective
6. multi-node scale
7. real training / inference workload

The last step cannot be replaced by iperf or ping.

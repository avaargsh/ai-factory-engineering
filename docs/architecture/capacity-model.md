# Capacity Engineering

## Capacity is layered

Installed capacity is not productive capacity.

```text
Installed
   |
Design
   |
Usable
   |
Allocatable
   |
Productive
```

Definitions:

- **Installed** — physically present hardware.
- **Design** — capacity allowed by engineering constraints.
- **Usable** — after redundancy, maintenance and health derating.
- **Allocatable** — actually schedulable under topology, quota and fragmentation constraints.
- **Productive** — capacity producing useful model progress or SLO-compliant tokens.

## Capacity Waterfall

```text
Contract MW
 -> Facility Usable MW
 -> IT MW
 -> Powered+Cooled Rack
 -> Installed GPU
 -> Healthy GPU
 -> Schedulable GPU
 -> Allocated GPU
 -> Productive GPU Hours
 -> Token Goodput / Model Progress
```

Every stage should have an explicit loss term.

## Multi-Roof model

The system is bounded by its tightest roof:

```text
Capacity = min(
  Power,
  Cooling,
  Space/Weight,
  Fabric,
  Storage,
  Runtime,
  Workload
)
```

This prevents misleading statements such as "we still have free GPUs" when the actual bottleneck is fabric topology, KV capacity or thermal headroom.

## Reverse planning

A useful capacity plan starts from demand:

```text
Token / Training Demand
 -> Required Goodput / Model Progress
 -> Parallelism + Runtime Efficiency
 -> Productive GPU
 -> Allocatable / Healthy GPU
 -> Rack / Pod
 -> IT MW
 -> Facility MW
```

## Headroom

Track at least:

- power headroom,
- thermal headroom,
- fabric headroom,
- storage/checkpoint headroom,
- scheduling headroom,
- SLO headroom,
- growth headroom.

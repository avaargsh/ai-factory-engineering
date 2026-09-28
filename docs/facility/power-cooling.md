# Facility: Power and Cooling

## Grid-to-Chip

```text
Grid
 -> Substation
 -> MV/LV
 -> UPS / HVDC / BESS
 -> Busway / PDU
 -> PSU / Power Shelf
 -> GPU / CPU / NIC
```

The engineering goal is not simply electrical continuity. It is a stable **GPU power envelope** with known fault, maintenance and growth boundaries.

## Thermal path

```text
GPU / CPU
 -> Cold Plate
 -> Technology Cooling System
 -> CDU
 -> Facility Water System
 -> Heat Rejection
```

Useful variables:

- supply / return temperature,
- flow,
- delta-T,
- differential pressure,
- heat load,
- water quality,
- pump / heat-exchanger state.

## Cross-layer failure

A thermal problem may not create an outage:

```text
Low flow / high inlet temperature
 -> GPU temperature rises
 -> power / clock throttling
 -> step time or TPOT worsens
 -> Productive Capacity falls
 -> SLO / revenue impact
```

That is why facility telemetry must correlate with GPU and workload metrics.

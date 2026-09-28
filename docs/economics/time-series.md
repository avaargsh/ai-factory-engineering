# Time-Series Economics: 8760 / 35040

A yearly AI Factory model should not assume one average power price and one average utilization.

The same engine can consume:

- 8760 hourly intervals, or
- 35040 fifteen-minute intervals.

## Input per interval

```text
duration
electricity price
IT load factor
productive utilization
PUE
```

Global capacity inputs:

```text
IT capacity MW
productive GPU capacity
tokens / productive GPU-hour
optional revenue / 1M tokens
```

## Per interval

```text
IT MW
   |
   x PUE
   v
Facility MW
   |
   x duration
   v
Energy kWh
   |
   x electricity price
   v
Electricity Cost

Productive GPU Capacity
   |
   x productive utilization
   x duration
   v
Productive GPU Hours
   |
   x tokens/GPU-hour
   v
Useful Tokens
```

## Outputs

- IT MWh
- Facility MWh
- electricity cost
- Productive GPU Hours
- Tokens
- Tokens/kWh
- electricity cost / 1M Tokens
- optional token revenue
- margin after electricity

## Boundary

This is currently an **energy-side contribution model**, not a full P&L.

It does not yet include:

- depreciation,
- financing,
- network/storage cost,
- software licenses,
- staffing,
- maintenance,
- tax,
- demand charges,
- BESS cycle degradation.

Those should remain separate cost layers rather than being hidden inside an electricity-rate assumption.

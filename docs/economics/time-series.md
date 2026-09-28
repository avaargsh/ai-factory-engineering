# Time-Series Capacity and Energy: 8760 / 35040

A yearly AI Factory model should not assume one average power price and one average utilization.

The same engine can consume:

- **8760** hourly intervals, or
- **35040** fifteen-minute intervals.

## Input per interval

```text
duration_hours
electricity_price_per_kwh
it_load_factor
productive_utilization
pue
```

Global inputs:

```text
IT capacity MW
Productive GPU capacity
Tokens / Productive GPU-hour
```

## Per interval

```text
IT Capacity MW
    x IT Load Factor
    = IT MW
        |
        x PUE
        v
Facility MW
        |
        x Duration
        v
Facility Energy
        |
        x Electricity Price
        v
Energy Cost
```

In parallel:

```text
Productive GPU Capacity
        |
        x Productive Utilization
        x Duration
        v
Productive GPU Hours
        |
        x Tokens / GPU-hour
        v
Useful Tokens
```

## Outputs

The current implementation reports:

- IT MWh
- Facility MWh
- Energy Cost
- Productive GPU Hours
- Useful Tokens
- Tokens / kWh
- Energy Cost / 1M Tokens

## CLI

```bash
ai-factory timeseries economics/examples/day-15m.csv \
  --it-capacity-mw 8 \
  --productive-gpu-capacity 4000 \
  --tokens-per-productive-gpu-hour 1000000
```

The example CSV demonstrates the contract only; it is not a claim about a particular tariff, GPU generation or facility.

## Boundary

This is an energy-side production model, not a full P&L.

It does not yet include:

- depreciation,
- financing,
- network/storage cost,
- software licenses,
- staffing,
- maintenance,
- tax,
- demand charges,
- BESS cycle degradation,
- business revenue.

Those should be explicit future cost/value layers rather than hidden inside an average power price.

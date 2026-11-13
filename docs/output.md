# Output and exit codes

## Table (default)

One row per sensor with `n`, `min`, `max`, `mean` and the number of breaches,
followed by the list of breaches in timestamp order.

## JSON (`--json`)

```json
{
  "sensors": {"TT-101": {"n": 12, "min": 61.0, "max": 84.5, "mean": 71.9, "breaches": 2}},
  "breaches": [{"timestamp": "2026-11-12T03:00", "sensor": "TT-101", "value": 84.5, "limit": 80.0, "kind": "high"}],
  "skipped_rows": 0
}
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | No breaches |
| `1` | At least one breach |
| `2` | Invalid input (missing columns, unreadable file, bad thresholds) |

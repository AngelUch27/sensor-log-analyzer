# Input CSV format

A header row followed by one reading per row:

```csv
timestamp,sensor,value
2026-11-12T00:00,TT-101,62.1
2026-11-12T00:00,PT-205,4.1
```

| Column | Meaning |
|---|---|
| `timestamp` | ISO-8601 date-time, kept as text and used to order breaches |
| `sensor` | Sensor tag; any string |
| `value` | Decimal number; rows with a non-numeric value are skipped and counted in `skipped_rows` |

Column order does not matter; column names do (case-insensitive). Extra columns
are ignored.

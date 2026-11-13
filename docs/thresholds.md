# Thresholds file

A JSON object keyed by sensor tag. Each entry may set `low`, `high` or both:

```json
{
  "TT-101": {"high": 80.0},
  "PT-205": {"low": 3.5, "high": 5.0},
  "FT-310": {"low": 120.0}
}
```

A reading is a **breach** when `value < low` or `value > high` (strict). Sensors
missing from the file are analysed for statistics only. Values must be numbers;
anything else stops the run with exit code `2` and the offending tag.

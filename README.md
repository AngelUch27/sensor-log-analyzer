# sensor-log-analyzer

Reads a CSV of sensor readings, computes per-sensor statistics and flags every
reading outside its allowed range. Built for the kind of log a PLC or a data
historian exports: one row per reading, one column per field.

```bash
python -m sensor_log_analyzer examples/readings.csv --thresholds examples/thresholds.json
```

```
sensor        n     min     max    mean   breaches
FT-310       12   118.0   142.0   130.4   1 (low)
PT-205       12     3.9     4.6     4.2   0
TT-101       12    61.0    84.5    71.9   2 (high)

breaches:
2026-11-12T03:00  TT-101  84.5 > 80 (high)
2026-11-12T03:15  TT-101  83.9 > 80 (high)
2026-11-12T07:30  FT-310  118 < 120 (low)
```

## Features

- Statistics per sensor: count, min, max, mean.
- Threshold breaches (`low` / `high`) from a JSON thresholds file; sensors
  without thresholds are reported without breaches.
- `--json` for machine-readable output; exit code `1` when any breach exists.
- Standard library only (Python 3.10+).

## Install and test

```bash
git clone https://github.com/AngelUch27/sensor-log-analyzer.git
cd sensor-log-analyzer
python -m pytest -q
```

## Documentation

- [Input CSV format](docs/csv-format.md)
- [Thresholds file](docs/thresholds.md)
- [Output and exit codes](docs/output.md)

## License

MIT

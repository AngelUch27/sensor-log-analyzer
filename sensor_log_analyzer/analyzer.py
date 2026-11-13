from __future__ import annotations

import csv
from dataclasses import dataclass, field
import json
from pathlib import Path


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Reading:
    timestamp: str
    sensor: str
    value: float


@dataclass(frozen=True)
class Breach:
    timestamp: str
    sensor: str
    value: float
    limit: float
    kind: str  # "low" | "high"

    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp, "sensor": self.sensor, "value": self.value, "limit": self.limit, "kind": self.kind}


@dataclass
class Analysis:
    sensors: dict[str, dict] = field(default_factory=dict)
    breaches: list[Breach] = field(default_factory=list)
    skipped_rows: int = 0

    def to_dict(self) -> dict:
        return {"sensors": self.sensors, "breaches": [b.to_dict() for b in self.breaches], "skipped_rows": self.skipped_rows}


def read_readings(path: str | Path) -> tuple[list[Reading], int]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputError("the CSV file is empty")
        columns = {name.lower(): name for name in reader.fieldnames}
        missing = [c for c in ("timestamp", "sensor", "value") if c not in columns]
        if missing:
            raise InputError(f"missing column(s): {', '.join(missing)}")
        readings, skipped = [], 0
        for row in reader:
            try:
                value = float(row[columns["value"]])
            except (TypeError, ValueError):
                skipped += 1
                continue
            readings.append(Reading(row[columns["timestamp"]].strip(), row[columns["sensor"]].strip(), value))
    return readings, skipped


def load_thresholds(path: str | Path | None) -> dict[str, dict[str, float]]:
    if path is None:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InputError("thresholds must be a JSON object keyed by sensor")
    out: dict[str, dict[str, float]] = {}
    for sensor, limits in data.items():
        if not isinstance(limits, dict):
            raise InputError(f"{sensor}: thresholds must be an object with 'low' and/or 'high'")
        parsed = {}
        for kind in ("low", "high"):
            if kind in limits:
                try:
                    parsed[kind] = float(limits[kind])
                except (TypeError, ValueError) as exc:
                    raise InputError(f"{sensor}: '{kind}' must be a number") from exc
        out[sensor] = parsed
    return out


def analyze(readings: list[Reading], thresholds: dict[str, dict[str, float]], skipped_rows: int = 0) -> Analysis:
    analysis = Analysis(skipped_rows=skipped_rows)
    grouped: dict[str, list[Reading]] = {}
    for r in readings:
        grouped.setdefault(r.sensor, []).append(r)
    for sensor in sorted(grouped):
        values = [r.value for r in grouped[sensor]]
        limits = thresholds.get(sensor, {})
        count = 0
        for r in grouped[sensor]:
            if "low" in limits and r.value < limits["low"]:
                analysis.breaches.append(Breach(r.timestamp, sensor, r.value, limits["low"], "low")); count += 1
            elif "high" in limits and r.value > limits["high"]:
                analysis.breaches.append(Breach(r.timestamp, sensor, r.value, limits["high"], "high")); count += 1
        analysis.sensors[sensor] = {"n": len(values), "min": min(values), "max": max(values), "mean": round(sum(values) / len(values), 2), "breaches": count}
    analysis.breaches.sort(key=lambda b: (b.timestamp, b.sensor))
    return analysis


def format_table(analysis: Analysis) -> str:
    lines = [f"{'sensor':10s} {'n':>4s} {'min':>7s} {'max':>7s} {'mean':>7s}   breaches"]
    for sensor, s in analysis.sensors.items():
        kinds = {b.kind for b in analysis.breaches if b.sensor == sensor}
        suffix = f" ({'/'.join(sorted(kinds))})" if kinds else ""
        lines.append(f"{sensor:10s} {s['n']:4d} {s['min']:7.1f} {s['max']:7.1f} {s['mean']:7.1f}   {s['breaches']}{suffix}")
    if analysis.breaches:
        lines.append("")
        lines.append("breaches:")
        for b in analysis.breaches:
            op = "<" if b.kind == "low" else ">"
            lines.append(f"{b.timestamp}  {b.sensor}  {b.value:g} {op} {b.limit:g} ({b.kind})")
    if analysis.skipped_rows:
        lines.append(f"\nskipped rows with non-numeric values: {analysis.skipped_rows}")
    return "\n".join(lines)

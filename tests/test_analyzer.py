import pytest

from sensor_log_analyzer import analyze, load_thresholds, read_readings
from sensor_log_analyzer.analyzer import InputError


def test_example_log_reports_three_breaches_in_time_order():
    readings, skipped = read_readings("examples/readings.csv")
    analysis = analyze(readings, load_thresholds("examples/thresholds.json"), skipped)
    assert analysis.skipped_rows == 0
    assert analysis.sensors["TT-101"]["n"] == 12 and analysis.sensors["TT-101"]["breaches"] == 2
    assert analysis.sensors["PT-205"]["breaches"] == 0
    assert [(b.timestamp, b.sensor, b.kind) for b in analysis.breaches] == [
        ("2026-11-12T03:00", "TT-101", "high"), ("2026-11-12T03:15", "TT-101", "high"), ("2026-11-12T07:30", "FT-310", "low")]


def test_non_numeric_rows_are_skipped_and_counted(tmp_path):
    f = tmp_path / "r.csv"
    f.write_text("Timestamp,Sensor,Value\n2026-01-01T00:00,A,1.5\n2026-01-01T01:00,A,n/a\n", encoding="utf-8")
    readings, skipped = read_readings(f)
    assert len(readings) == 1 and skipped == 1  # column names are case-insensitive


def test_missing_columns_are_an_input_error(tmp_path):
    f = tmp_path / "r.csv"
    f.write_text("time,tag,value\n", encoding="utf-8")
    with pytest.raises(InputError) as info:
        read_readings(f)
    assert "timestamp" in str(info.value) and "sensor" in str(info.value)


def test_thresholds_are_validated(tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"X": {"high": "hot"}}', encoding="utf-8")
    with pytest.raises(InputError) as info:
        load_thresholds(f)
    assert "X:" in str(info.value)

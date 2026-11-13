import argparse
import json
import sys

from .analyzer import InputError, analyze, format_table, load_thresholds, read_readings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sensor_log_analyzer", description="Statistics and threshold breaches from a sensor CSV.")
    parser.add_argument("csv_file")
    parser.add_argument("--thresholds", help="JSON file with low/high limits per sensor")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        readings, skipped = read_readings(args.csv_file)
        analysis = analyze(readings, load_thresholds(args.thresholds), skipped)
    except (InputError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(analysis.to_dict(), indent=2) if args.json else format_table(analysis))
    return 1 if analysis.breaches else 0


if __name__ == "__main__":
    sys.exit(main())

"""Defensive demo (Topics 2 and 3): find hosts whose CPU pattern looks like mining or throttled mining.

Rules (all simple, all on INVENTED telemetry):
  always_hot : average CPU very high for the whole window (sustained 100%-style mining)
  duty_cycle : repeating busy/idle pattern (autocorrelation peak) with a high busy level, i.e. a miner
               that throttles itself to stay under an average-CPU alert
Run: python scripts/miner_duty_cycle_detector.py [csv_path]
"""
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "data" / "synthetic_cpu_telemetry.csv"


def autocorr(xs, lag):
    m = statistics.fmean(xs)
    num = sum((xs[i] - m) * (xs[i + lag] - m) for i in range(len(xs) - lag))
    den = sum((x - m) ** 2 for x in xs)
    return num / den if den else 0.0


def classify(series, hot=90, busy=60, ac_min=0.5, lags=range(5, 40)):
    mean = statistics.fmean(series)
    if mean >= hot:
        return "always_hot", mean, None
    peak_lag, peak = max(((lag, autocorr(series, lag)) for lag in lags), key=lambda p: p[1])
    busy_share = sum(x >= busy for x in series) / len(series)
    if peak >= ac_min and 0.3 <= busy_share <= 0.85:
        return "duty_cycle", mean, peak_lag
    return "normal", mean, None


def main(path):
    data = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            data[r["host"]].append((int(r["minute"]), float(r["cpu_percent"])))
    print(f"{'host':<8} {'mean CPU':>9}  verdict")
    for host, pts in sorted(data.items()):
        series = [c for _, c in sorted(pts)]
        verdict, mean, lag = classify(series)
        extra = f" (repeats about every {lag} min)" if lag else ""
        print(f"{host:<8} {mean:>8.1f}%  {verdict}{extra}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)

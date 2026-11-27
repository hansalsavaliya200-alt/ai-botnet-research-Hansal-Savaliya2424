"""Defensive demo (Topic 4): score businesses for fake-review campaigns using behaviour signals.

Signals: recent burst vs normal rate, share of reviews from very new accounts, near-duplicate wording.
Input: data/synthetic_reviews.csv (invented). It does NOT try to detect 'AI text'.
Run: python scripts/review_anomaly_detector.py [csv_path]
"""
import csv
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "data" / "synthetic_reviews.csv"


def shingles(text, n=3):
    words = "".join(c.lower() if c.isalnum() or c == " " else " " for c in text).split()
    return {" ".join(words[i:i + n]) for i in range(max(1, len(words) - n + 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def analyse(rows, window=3, new_age=30, sim_threshold=0.3):
    by_biz = defaultdict(list)
    for r in rows:
        by_biz[r["business"]].append(r)
    results = []
    for biz, items in by_biz.items():
        last_day = max(int(r["day"]) for r in items)
        recent = [r for r in items if int(r["day"]) > last_day - window]
        older = [r for r in items if int(r["day"]) <= last_day - window]
        days_old = max(1, last_day - window)
        normal_rate = len(older) / days_old            # reviews per day normally
        recent_rate = len(recent) / window
        burst = recent_rate / normal_rate if normal_rate else float("inf")
        new_share = (sum(int(r["account_age_days"]) < new_age for r in recent) / len(recent)) if recent else 0
        sets = [shingles(r["text"]) for r in recent]
        pairs = list(combinations(range(len(sets)), 2))
        similar = sum(jaccard(sets[i], sets[j]) >= sim_threshold for i, j in pairs)
        sim_share = similar / len(pairs) if pairs else 0
        score = 0
        score += 2 if burst >= 5 else 0
        score += 2 if new_share >= 0.5 else 0
        score += 2 if sim_share >= 0.2 else 0
        results.append({"business": biz, "recent_reviews": len(recent), "burst_ratio": round(burst, 1),
                        "new_account_share": round(new_share, 2), "similar_pair_share": round(sim_share, 2),
                        "risk_score": score, "flag": "REVIEW" if score >= 4 else "ok"})
    return sorted(results, key=lambda x: -x["risk_score"])


def main(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"{'business':<12} {'recent':>6} {'burst x':>8} {'new acct':>9} {'similar':>8} {'score':>6}  flag")
    for r in analyse(rows):
        print(f"{r['business']:<12} {r['recent_reviews']:>6} {r['burst_ratio']:>8} {r['new_account_share']:>9} "
              f"{r['similar_pair_share']:>8} {r['risk_score']:>6}  {r['flag']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)

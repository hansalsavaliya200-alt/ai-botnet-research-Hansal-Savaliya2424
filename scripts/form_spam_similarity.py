"""Defensive demo (Topic 1): find contact-form spam campaigns that rotate source addresses.

Idea: AI-written messages differ in wording, but the campaign still reuses (a) one browser fingerprint
across many addresses and (b) a small set of outbound domains. Flag fingerprints seen from many distinct
addresses in a short time. Input: data/synthetic_form_logs.csv (invented).
Run: python scripts/form_spam_similarity.py [csv_path]
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "data" / "synthetic_form_logs.csv"
DOMAIN = re.compile(r"\b([a-z0-9-]+(?:\.[a-z0-9-]+)+)\b")


def analyse(rows, min_ips=10, window=600):
    by_fp = defaultdict(list)
    for r in rows:
        by_fp[r["ua_hash"]].append(r)
    flagged = []
    for fp, items in by_fp.items():
        items.sort(key=lambda r: int(r["t_seconds"]))
        ips = {r["src_ip"] for r in items}
        span = int(items[-1]["t_seconds"]) - int(items[0]["t_seconds"])
        domains = defaultdict(int)
        for r in items:
            for d in DOMAIN.findall(r["message"].lower()):
                domains[d] += 1
        if len(ips) >= min_ips and span <= window:
            flagged.append({"ua_hash": fp, "posts": len(items), "distinct_ips": len(ips), "span_s": span,
                            "domains": dict(domains)})
    return flagged


def main(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result = analyse(rows)
    if not result:
        print("No campaign pattern found.")
    for r in result:
        print(f"FLAG fingerprint={r['ua_hash']} posts={r['posts']} distinct_ips={r['distinct_ips']} "
              f"over={r['span_s']}s domains={r['domains']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)

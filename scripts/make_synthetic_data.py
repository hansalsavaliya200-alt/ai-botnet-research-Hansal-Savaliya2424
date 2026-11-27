"""Generates INVENTED data for the demonstrations (fixed seed, no real people or systems).

Run:  python scripts/make_synthetic_data.py
Writes: data/synthetic_reviews.csv, data/synthetic_cpu_telemetry.csv, data/synthetic_form_logs.csv
"""
import csv
import random
from pathlib import Path

random.seed(2026)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)


def reviews():
    """Two invented businesses. 'Cafe Alpha' gets a burst of near-identical 5-star reviews from new accounts."""
    rows, rid = [], 0
    organic = ["Friendly staff and quick service", "Coffee was fine, a bit pricey", "Nice place for a meeting",
               "Waited long but the food was good", "Cozy and clean", "Average experience, would return",
               "Loved the pastries", "Too noisy at lunch time"]
    for biz in ("Cafe Alpha", "Shop Beta"):
        for day in range(1, 61):  # ~60 days of normal activity
            if random.random() < 0.35:
                rid += 1
                rows.append([rid, biz, f"user{random.randint(1, 400)}", random.randint(200, 2000),
                             random.choice([3, 4, 4, 5, 2, 5]), day, random.choice(organic) + f" ({random.randint(1,99)})"])
    templates = ["Amazing service and the {x} was perfect, highly recommend Cafe Alpha to everyone",
                 "Best {x} in town, Cafe Alpha staff were wonderful, five stars"]
    for i in range(25):  # burst on day 58-59
        rid += 1
        rows.append([rid, "Cafe Alpha", f"newuser{i}", random.randint(0, 5), 5, random.choice([58, 59]),
                     random.choice(templates).format(x=random.choice(["latte", "coffee", "cake", "brunch"]))])
    return ["review_id", "business", "account", "account_age_days", "stars", "day", "text"], rows


def telemetry():
    """CPU % per minute for 6 invented hosts over 240 minutes."""
    rows = []
    for host in ("web-01", "web-02", "db-01", "ci-01", "app-01", "app-02"):
        for t in range(240):
            if host == "app-01":      # always-on miner: ~98% flat
                cpu = random.gauss(98, 1)
            elif host == "app-02":    # throttled duty-cycle miner: 10 min busy, 5 min idle
                cpu = random.gauss(85, 3) if (t % 15) < 10 else random.gauss(6, 2)
            else:                     # normal servers: noisy low load, some random spikes
                cpu = random.gauss(18, 6) + (40 if random.random() < 0.03 else 0)
            rows.append([host, t, round(max(0, min(100, cpu)), 1)])
    return ["host", "minute", "cpu_percent"], rows


def form_logs():
    """Contact-form POSTs. 'spamfp' = one user-agent hash used from many invented addresses."""
    rows = []
    for i in range(120):  # normal visitors
        rows.append([i * 30, f"198.51.100.{random.randint(1, 250)}", f"ua{random.randint(1, 40):02d}", "/contact",
                     random.choice(["Question about opening hours", "Do you ship abroad?", "Need a quote", "Hello"])])
    for i in range(45):   # campaign: addresses rotate, fingerprint constant, message mentions the site
        rows.append([2000 + i * 8, f"203.0.113.{random.randint(1, 250)}", "ua_spamfp", "/contact",
                     f"Hi, I looked at your shop and I can improve your search ranking, visit seo-example-{i % 3}.invalid"])
    return ["t_seconds", "src_ip", "ua_hash", "path", "message"], sorted(rows)


for name, fn in (("synthetic_reviews.csv", reviews), ("synthetic_cpu_telemetry.csv", telemetry),
                 ("synthetic_form_logs.csv", form_logs)):
    header, rows = fn()
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote data/{name}: {len(rows)} rows")

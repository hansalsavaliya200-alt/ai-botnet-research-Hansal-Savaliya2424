"""Tests for the safe analysis scripts, using the synthetic data."""
import csv
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
ROOT = Path(__file__).resolve().parent.parent


def setup_module(_):
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_synthetic_data.py")], check=True,
                   stdout=subprocess.DEVNULL)


def rows(name):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_review_detector_flags_the_campaign_business_only():
    import review_anomaly_detector as d
    result = {r["business"]: r for r in d.analyse(rows("synthetic_reviews.csv"))}
    assert result["Cafe Alpha"]["flag"] == "REVIEW"
    assert result["Shop Beta"]["flag"] == "ok"


def test_duty_cycle_detector_classifies_hosts():
    import miner_duty_cycle_detector as d
    data = {}
    for r in rows("synthetic_cpu_telemetry.csv"):
        data.setdefault(r["host"], []).append((int(r["minute"]), float(r["cpu_percent"])))
    verdict = {h: d.classify([c for _, c in sorted(p)])[0] for h, p in data.items()}
    assert verdict["app-01"] == "always_hot"
    assert verdict["app-02"] == "duty_cycle"
    assert all(verdict[h] == "normal" for h in ("web-01", "web-02", "db-01", "ci-01"))


def test_form_spam_detector_finds_rotating_address_campaign():
    import form_spam_similarity as d
    flagged = d.analyse(rows("synthetic_form_logs.csv"))
    assert [f["ua_hash"] for f in flagged] == ["ua_spamfp"]
    assert flagged[0]["distinct_ips"] >= 10


def test_ioc_scanner_matches_defanged_and_plain_forms():
    import ioc_scanner as s
    iocs = s.load_iocs()
    text = "dns query for goservicewrap.com and file NextCaptchaBot-v6 seen"
    values = {h[1] for h in s.scan_text(text, iocs)}
    assert "goservicewrap[.]com" in values and "NextCaptchaBot-v6" in values
    assert s.scan_text("nothing relevant here", iocs) == []

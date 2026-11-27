"""Scans a text file (log, notes, DNS export) for the indicators in detection/iocs.csv.
Defanged values like example[.]com are matched in both defanged and normal form.
Only reads files you give it. No network access.
Run: python scripts/ioc_scanner.py <file.txt>
"""
import csv
import sys
from pathlib import Path

IOCS = Path(__file__).resolve().parent.parent / "detection" / "iocs.csv"
MATCHABLE = {"domain", "sha256", "url_path", "filename"}


def load_iocs(path=IOCS):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["type"] in MATCHABLE:
                out.append(r)
    return out


def scan_text(text, iocs):
    lowered = text.lower()
    hits = []
    for r in iocs:
        value = r["value"].lower()
        forms = {value, value.replace("[.]", ".")}
        if any(form in lowered for form in forms):
            hits.append((r["type"], r["value"], r["source"], r["confidence"]))
    return hits


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/ioc_scanner.py <file.txt>")
    content = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    found = scan_text(content, load_iocs())
    print(f"{len(found)} indicator(s) found")
    for t, v, s, c in found:
        print(f"  [{c}] {t}: {v}  ({s})")

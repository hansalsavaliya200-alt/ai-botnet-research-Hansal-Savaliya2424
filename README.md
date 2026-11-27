# AI-Assisted Botnet Research: Spam, Cryptojacking, Resource Allocation and Reputation Fraud

**Author:** Hansal Savaliya, Intern ID 2424
**Programme:** RedKross Research Foundation, Cybersecurity Malware Research Internship, Milestone Task 3
**Video:** Record and publish the 3–5 minute walkthrough on YouTube (Unlisted), Loom, or Google Drive, then add the access link here.
**Technical report:** [`report/technical-report.pdf`](report/technical-report.pdf)
**Slides:** [`slides/ai-botnet-research-slides.pptx`](slides/ai-botnet-research-slides.pptx)

This is **defensive research**. It contains no functional malware, no samples and no credentials. See [`docs/00-scope-and-ethics.md`](docs/00-scope-and-ethics.md).

## My four assigned topics

| # | Topic | Evidence level | Analysis |
|---|-------|----------------|----------|
| 1 | AI Spam-Campaign Botnet | Evidenced (AkiraBot, SentinelLABS 2025) | [docs/01](docs/01-ai-spam-campaign-botnet.md) |
| 2 | AI Cryptojacking Botnet | Evidenced; AI role inferred (Lumen 2026, Rubrik 2026, Akamai 2025) | [docs/02](docs/02-ai-cryptojacking-botnet.md) |
| 3 | AI Botnet Resource-Allocation Controller | **Conceptual**, built from evidenced components | [docs/03](docs/03-ai-botnet-resource-allocation-controller.md) |
| 4 | AI Bot Reputation-Management System | Evidenced market (Malwarebytes 2026); bot system partly conceptual | [docs/04](docs/04-ai-bot-reputation-management-system.md) |

Each document has: definition, evidenced findings, architecture, execution flow, attack vectors, kill chain (ATT&CK-aligned), detection, mitigation and limitations. Labels `[EVIDENCED]`, `[INFERRED]` and `[CONCEPTUAL]` mark how strong the evidence is.

## Architecture of this repository

```
 Published reports  --->  docs/ (analysis, kill chains)  --->  report/ + slides/
        |                         |
        |                         +--->  detection/ (YARA, Sigma, IoCs)
        |                                       ^
        +--->  scripts/ (safe demos on SYNTHETIC data) --- tests/ (13 tests validate rules and scripts)
```

## What is in the repository

| Folder | Contents |
|--------|----------|
| `docs/` | One analysis per topic, scope and ethics, saved outputs in `docs/evidence/` |
| `detection/` | 3 YARA rules, 4 Sigma documents (3 rules, 1 rule plus a correlation rule), `iocs.csv`, `iocs.md`, how each was tested |
| `scripts/` | Four defensive demos and a synthetic data generator |
| `tests/` | `pytest` checks that every rule compiles or parses, matches harmless positive text and ignores benign text, and that each script flags the planted pattern |
| `data/` | Invented CSV files created by the generator (fixed seed) |
| `report/`, `slides/` | Technical report (Markdown and PDF) and presentation |
| `status/` | Weekly project status log |
| `references.md` | Sources with titles, URLs, access dates and what each was used for |

## Run it (Python 3.10 or newer)

```
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_synthetic_data.py
python scripts/review_anomaly_detector.py       # Topic 4: flags the synthetic fake-review burst
python scripts/miner_duty_cycle_detector.py     # Topics 2/3: flags always-on and duty-cycle miners (synthetic telemetry)
python scripts/form_spam_similarity.py          # Topic 1: flags a form-spam campaign rotating addresses
python scripts/ioc_scanner.py <some_text_file>  # matches published IoCs in a text file
python -m pytest                                # expect 13 passed
```

`yara-python` needs a C compiler on some systems. If installing it fails, the rest still runs; the YARA tests need it.

## Key findings

1. **AI mainly changes content and development speed, not the delivery mechanism.** AkiraBot's AI-written messages defeat text filters, but its operator still depends on proxies and CAPTCHA services, which can be detected by behaviour.
2. **In the cryptojacking cases, AI's role is the researchers' inference.** What defenders actually see is old behaviour: exposed services, SSH brute force, miners, log wiping.
3. **Resource allocation exists today as fixed rules** (IPv4 sharding, a 70% CPU rival killer, miner proxies). An AI controller is conceptual, so I focus on cross-host and over-time behaviour signals.
4. **Reputation fraud is mostly human plus AI text plus residential proxies.** Behaviour signals (bursts, new accounts, similar wording) work better than trying to detect AI text.

## Limits

Rules and scripts are tested only on invented data and harmless text. They are teaching and hunting aids, not production detections. Topics 3 and 4 are partly conceptual and labelled as such.

## AI use

Claude and GitHub Copilot helped me research, draft and structure this work. I reviewed the content and sources and can explain it.

## Licence

MIT.

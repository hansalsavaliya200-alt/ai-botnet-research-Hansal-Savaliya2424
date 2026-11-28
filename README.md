# AI Botnet Threat Landscape

### Technical research and defensive detection engineering

**Author:** Hansal Savaliya · **Intern ID:** 2424

**Programme:** RedKross Research Foundation · Cybersecurity Malware Research Internship · Milestone Task 3
**Status:** Research complete · **Test suite:** 13 passing

> A defensive research portfolio examining four botnet and online-abuse topics, separating observed reporting from inference and hypothetical scenarios.

| Deliverable | Link / status |
|---|---|
| Technical report | [PDF](report/technical-report.pdf) · [Markdown source](report/technical-report.md) |
| Presentation | [PDF slides](slides/ai-botnet-research-slides.pdf) · [Editable PowerPoint](slides/ai-botnet-research-slides.pptx) |
| Video walkthrough | Pending publication to YouTube (Unlisted), Loom, or Google Drive |
| Public repository | [GitHub](https://github.com/hansalsavaliya200-alt/ai-botnet-research-Hansal-Savaliya2424) |

## Research coverage

| Topic | Evidence assessment | Brief |
|---|---|---|
| AI Spam-Campaign Botnet | AkiraBot reporting documented; botnet framing is qualified | [Research brief](docs/01-ai-spam-campaign-botnet.md) |
| AI Cryptojacking Botnet | Incidents documented; AI involvement is attributed as inference | [Research brief](docs/02-ai-cryptojacking-botnet.md) |
| AI Botnet Resource-Allocation Controller | Conceptual scenario; not presented as an observed system | [Research brief](docs/03-ai-botnet-resource-allocation-controller.md) |
| AI Bot Reputation-Management System | Fake-review market documented; full automation partly conceptual | [Research brief](docs/04-ai-bot-reputation-management-system.md) |

Evidence labels used throughout:

- **[EVIDENCED]** — reported by an identified public source.
- **[INFERRED]** — an interpretation or conclusion, not an established fact.
- **[CONCEPTUAL]** — a hypothetical variant used for defensive analysis.

## Project architecture

```text
Public research and references
              |
              v
  docs/ topic briefs + ethics scope
              |
      +-------+--------+
      |                |
      v                v
report/ + slides/   detection/
      |           YARA / Sigma / IoCs
      |                |
      +--------+-------+
               v
     scripts/ + synthetic data
               |
               v
        tests/ (13 passing)
```

## Repository map

| Path | Contents |
|---|---|
| [`docs/`](docs/) | Four topic briefs, research scope and ethics statement, and saved demonstration outputs |
| [`report/`](report/) | Technical report source, designed PDF, print stylesheet, and reproducible build script |
| [`slides/`](slides/) | PDF and editable PowerPoint presentation |
| [`detection/`](detection/) | Three YARA rules, Sigma rules, IoC register, testing notes |
| [`scripts/`](scripts/) | Safe local analysis demonstrations and synthetic data generator |
| [`data/`](data/) | Synthetic datasets generated for demonstrations |
| [`tests/`](tests/) | Rule parsing/compilation checks and script behaviour tests |
| [`references.md`](references.md) | Research sources and attribution notes |

## Safe demonstrations

The scripts are defensive demonstrations and use only generated synthetic data. They do not contact targets, deploy malware, or use live samples.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\make_synthetic_data.py
python scripts\review_anomaly_detector.py
python scripts\miner_duty_cycle_detector.py
python scripts\form_spam_similarity.py
python -m pytest
```

Expected test result: **13 passed**. YARA tests require `yara-python`, included in `requirements.txt`.

## Rebuild the technical report

The designed PDF uses Pandoc and Microsoft Edge or Google Chrome in headless print mode:

```powershell
.\report\build-report.ps1
```

This regenerates [`report/technical-report.html`](report/technical-report.html) and [`report/technical-report.pdf`](report/technical-report.pdf) from the Markdown source and stylesheet.

## Key defensive findings

1. Content generation can vary spam and review text, but does not remove observable behaviours such as submission bursts, account patterns, or repeated infrastructure.
2. In the reviewed cryptojacking reports, claims about AI involvement are researcher inference; detections focus on host and network behaviour.
3. An AI-based resource-allocation controller is treated as conceptual. Existing allocation mechanisms in the cited cases are not evidence of an AI controller.
4. Layered behaviour-based controls are more durable than attempting to identify AI-written text alone.

## Scope and limitations

This portfolio is for defensive education. It contains no functional malware, live samples, credentials, or real victim data. Detection rules and scripts were checked with harmless text and synthetic datasets; they are examples, not production-ready controls. See [scope and ethics](docs/00-scope-and-ethics.md).

## Acknowledgements

AI tools assisted with research organization, drafting, and editing. Sources and outputs were reviewed by the author.

## Licence

MIT. See [LICENSE](LICENSE).

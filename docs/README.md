# Research documentation

This documentation set analyses four assigned topics from a defensive perspective. It distinguishes observed reporting from interpretation and hypothetical scenarios; conceptual models are not claims of real-world incidents.

## Topic briefs

| # | Topic | Evidence posture | Related detection and demonstrations |
|---|---|---|---|
| 1 | [AI Spam-Campaign Botnet](01-ai-spam-campaign-botnet.md) | AkiraBot reporting is documented; “botnet” terminology is qualified | [Sigma form-spam rule](../detection/sigma/web_form_spam_burst.yml) · [synthetic form analysis](../scripts/form_spam_similarity.py) |
| 2 | [AI Cryptojacking Botnet](02-ai-cryptojacking-botnet.md) | Mining activity is documented; AI involvement is attributed as inference | [YARA rules](../detection/yara/) · [Sigma rules](../detection/sigma/) · [CPU telemetry analysis](../scripts/miner_duty_cycle_detector.py) |
| 3 | [AI Botnet Resource-Allocation Controller](03-ai-botnet-resource-allocation-controller.md) | Conceptual controller based on evidenced components | [synthetic CPU telemetry analysis](../scripts/miner_duty_cycle_detector.py) |
| 4 | [AI Bot Reputation-Management System](04-ai-bot-reputation-management-system.md) | Fake-review market documented; full automation partly conceptual | [synthetic review analysis](../scripts/review_anomaly_detector.py) |

## Research governance

- [Scope, ethics, and safety](00-scope-and-ethics.md)
- [Sources and attribution](../references.md)
- [Detection engineering notes and limitations](../detection/README.md)
- [Complete technical report](../report/technical-report.pdf) · [Markdown source](../report/technical-report.md)

## Evidence labels

- **[EVIDENCED]** — a cited source directly reports the finding.
- **[INFERRED]** — interpretation or attribution is reported as uncertain or is analytical synthesis.
- **[CONCEPTUAL]** — a hypothetical system or capability, not a confirmed incident.

## Safe research materials

All demonstrations operate locally on synthetic data or harmless text. The repository does not include functional malware, live samples, credentials, or real victim data. Detection artifacts are educational hunting examples and require environment-specific validation before operational use.

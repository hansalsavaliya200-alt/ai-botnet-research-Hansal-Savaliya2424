# Detection engineering

All rules were written by me from published reports (see `../references.md`) and **tested on harmless text** in `tests/test_rules.py`. No malware samples were used.

| File | Type | Topic | What it detects | Confidence |
|------|------|-------|-----------------|------------|
| `yara/cryptominer_indicators.yar` | YARA | 2 | Text naming a Stratum pool plus miner options | medium |
| `yara/linux_log_tamper_script.yar` | YARA | 2 | Script combining service stop, log wiping and `chattr +i` | medium |
| `yara/ai_spam_tooling_hunt.yar` | YARA | 1 | Script chaining services reported for AkiraBot-style tools (hunting only) | low |
| `sigma/miner_commandline.yml` | Sigma | 2, 3 | Miner launched with pool URL or miner flags | high |
| `sigma/linux_audit_logging_stopped.yml` | Sigma | 2 | `auditd` or `rsyslog` stopped | medium |
| `sigma/linux_chattr_immutable.yml` | Sigma | 2 | `chattr +i` | medium |
| `sigma/web_form_spam_burst.yml` | Sigma (rule + correlation) | 1 | 20 or more form POSTs in 10 minutes sharing one user-agent | medium |
| `iocs.csv`, `iocs.md` | IoC list | 1, 2, 4 | Published indicators with source and confidence | varies |

## Honest limits

- YARA and Sigma rules here are hunting aids. Legitimate admin actions and authorised miners can match, so each rule lists false positives.
- IoCs such as domains and repository names expire quickly. Behaviour-based rules last longer.
- I validated syntax and behaviour on synthetic text. I did not test the rules against live traffic or real samples.
- Topic 3 and Topic 4 have no signature-style rules because they are conceptual and behavioural; they use the scripts in `../scripts/`.

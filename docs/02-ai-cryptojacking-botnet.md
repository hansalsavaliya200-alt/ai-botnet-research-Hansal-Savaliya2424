# Topic 2: AI Cryptojacking Botnet

**Evidence level:** two recent public analyses give **[EVIDENCED]** material: Lumen Black Lotus Labs on *PoeLLM / Canto Incognito* (reported 7 October 2026) and Rubrik Zero Labs on an *AI-architected Linux botnet* (3 March 2026). In both, the role of AI is the researchers' **[INFERRED]** conclusion, not a confirmed fact. Akamai's mining-botnet anatomy (24 June 2025) explains the mining infrastructure.

## 1. Definition

Cryptojacking means using someone else's computing power to mine cryptocurrency, usually Monero, without permission. A cryptojacking botnet does this across many compromised machines and sends the results to the operator's wallet. "AI" here means one or both of: (a) AI-assisted development of the malware, and (b) targeting AI infrastructure, which has valuable compute.

## 2. Case A: PoeLLM / Canto Incognito [EVIDENCED, Lumen Black Lotus Labs]

| Item | Finding |
|------|---------|
| Activity | Active since April 2026. More than 3,400 victim servers identified. Peak in mid-June with nearly 2,200 affected servers (about 800 active a day). Concentrated in the US and Western Europe. |
| Targets | Exposed AI/LLM and related infrastructure, for example LiteLLM, Gotenberg, Gitea and Ivanti Sentry appliances, through **known vulnerabilities** in internet-facing services. |
| Payload | Cryptominers (XMRig and Iron) connecting victims to the Kryptex mining service. |
| Spread | Compromised hosts act as scanners and exploit servers: they send HTTP POST requests to exposed ports of other targets, telling them to download the malware. Early signs of distributed brute-forcing of SSH and other logins (maturity uncertain). |
| C2 hiding | The C2 address is hidden in a **poem stored in a public GitHub repository**. The attacker changes a few words to point bots to a new C2. This is a "dead drop resolver" pattern. |
| AI link | Researchers believe the poem was likely written by AI, based on its style [INFERRED]. |
| Attribution | Italian-speaking actor, moderate confidence (Lumen). |
| Status | The GitHub repository is no longer accessible. Lumen believes null-routing of the C2s and an abuse report may have disrupted the campaign. |

## 3. Case B: AI-architected Linux botnet [EVIDENCED, Rubrik Zero Labs]

| Item | Finding |
|------|---------|
| Sample | A Python-based modular worm; SHA-256 `8471257186db7db30d74816409fa09a09898ee099e7e0d1ad015546975e53a8f` (as published). In the wild for at least three months. |
| C2 | **No central C2.** A peer-to-peer mesh exchanges encrypted JSON. A "dead man's switch" re-downloads the payload from hard-coded public repositories if the mesh fails. |
| Spread | Brute-forces SSH (port 22) with 30+ common credentials and uploads the payload over SFTP. Targets Redis (port 6379), with a cron fallback. |
| Scanning | Splits the IPv4 space into **shards** so bots do not scan the same ranges, and prioritises cloud-provider ranges. |
| Stealth | An eBPF rootkit hooks `sys_getdents64` to hide files. Uses `chattr +i` on its files. Stops `rsyslog` and `auditd`, truncates logs, clears shell history. |
| Rival killer | Kills competing miners (such as Kinsing and TeamTNT) by name, by CPU use above 70% and by mining-pool connections. Patches the vulnerabilities it used to get in. |
| AI link | Comments such as a "100/100 SCORE" suggest LLM generation under a scoring prompt. Researchers say the code "strongly suggests" AI architecture [INFERRED, not confirmed]. |

## 4. Mining infrastructure [EVIDENCED, Akamai]

- Victims run a miner that connects to a pool **directly** (the wallet is then on the victim) or through a **mining proxy**.
- A proxy aggregates many victims, hides the pool and wallet from victims and from network inspection, and submits all work under the attacker's wallet. Communication uses the **Stratum** protocol.
- Akamai reports that one proxy produced about 3 million hashes per second, worth roughly US$26,000 a year. A victim's CPU use dropped from 100% to 0% once mining stopped.

## 5. Generalised architecture [INFERRED]

```
 Vulnerable internet-facing service (exposed AI/LLM tools, Redis, SSH)
              |  initial access
              v
        Dropper / loader  <---- payload hosting (public repos, file hosts)
              |
   +----------+-----------+
   v                      v
 Miner (XMRig-type)    Spreader (scanner + exploit/brute force)
   |                      |
   v                      v
 Mining proxy -> Pool    New victims (cycle repeats)
   |
 Stealth + persistence (rootkit, log wiping, immutable files, cron)
   |
 C2 location: dead-drop (poem/repo) or peer-to-peer mesh
```

## 6. Execution flow

1. Scan the internet for a vulnerable or weakly protected service.
2. Gain access (known vulnerability, or default or weak credentials).
3. Download the payload from a public host and run it.
4. Remove or kill rival miners; hide files; disable logging.
5. Start the miner, pointing at a pool or proxy.
6. Use the new host to scan and infect more hosts.
7. Fetch updated instructions from the dead-drop or the peer mesh.

## 7. Attack vectors

| Vector | Notes |
|--------|-------|
| Known vulnerabilities in exposed services | Unpatched LLM gateways, Git servers, appliances. |
| Weak SSH credentials | Common-password brute force. |
| Exposed Redis | Misconfigured, unauthenticated. |
| Public hosting for payloads and C2 hints | GitHub, file-sharing sites. Hard to block outright. |

## 8. Kill chain (ATT&CK-aligned; verify IDs on attack.mitre.org)

| Stage | Activity | Technique |
|-------|----------|-----------|
| Initial access | Exploit vulnerable service; SSH brute force | T1190; T1110 |
| Execution | Run downloaded payload | T1059 (command/scripting) |
| Persistence | Cron job; immutable files | T1053.003; T1222.002 |
| Defense evasion | Stop auditd/rsyslog; clear logs and history; hide files with a rootkit | T1562.001; T1070.002; T1070.003; T1014 |
| Command and control | Dead-drop in a public repository; P2P mesh | T1102.001; T1071 |
| Lateral movement / spread | SSH, exploit-and-download | T1021.004; T1105 |
| Impact | Mining with victim CPU | T1496 (Resource Hijacking) |

## 9. Detection

- **Host:** miner command lines (pool URL with `stratum`, `--donate-level`, algorithm names); sustained high CPU on servers that have no such workload; processes killing other miners; `auditd`/`rsyslog` stopped; `chattr +i` on files in temp or home directories; truncated `wtmp`/`auth.log`.
- **Network:** connections to known mining pools or to Stratum-style ports; outbound connection from a server to many random IPs on 22 and 6379 (scanner behaviour); periodic fetches from a public repository by a server that never did that before.
- **Rules provided:** `detection/yara/cryptominer_indicators.yar`, `detection/yara/linux_log_tamper_script.yar`, `detection/sigma/miner_commandline.yml`, `detection/sigma/linux_audit_logging_stopped.yml`, `detection/sigma/linux_chattr_immutable.yml`, and `scripts/miner_duty_cycle_detector.py`.

## 10. Mitigation

- Patch internet-facing services quickly; do not expose LLM gateways, Git servers or Redis to the internet without authentication and network limits.
- Disable SSH password login; use keys; limit with firewall and fail2ban-type controls.
- Egress filtering: block or alert on mining-pool traffic and on unexpected outbound scanning.
- Resource monitoring with alerts on sustained CPU use outside expected hours.
- Protect logging: forward logs off-host so truncation cannot erase evidence.
- Restrict who can load eBPF programs; monitor `bpf()` use.

## 11. Limitations

- The "AI" element is inferred in both cases. The malware's behaviour, not its author, is what defenders see, so the detections do not depend on AI.
- Only a few IoCs are published for PoeLLM (a repository name). I list what is published and no more.

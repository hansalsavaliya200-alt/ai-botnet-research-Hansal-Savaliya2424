# AI-Assisted Botnets: Technical Analysis and Detection Engineering

**Name:** Hansal Savaliya  **Intern ID:** 2424
**Programme:** RedKross Research Foundation, Milestone Task 3: Malware Research
**Date:** November 2026
**Repository:** Public GitHub repository URL to be recorded after publication
**Video:** 3–5 minute technical walkthrough URL to be recorded after publication

## 1. Research objectives

1. Document, for each of my four assigned topics, how the malware or abuse system works: architecture, execution flow, attack vectors and kill chain.
2. Build actionable defences: indicators of compromise, YARA and Sigma rules, behaviour-based detections and mitigation controls.
3. Be clear about evidence. Where no public evidence exists for a topic, mark the analysis as conceptual.

The four topics are: **(1) AI Spam-Campaign Botnet, (2) AI Cryptojacking Botnet, (3) AI Botnet Resource-Allocation Controller, (4) AI Bot Reputation-Management System.**

## 2. Methodology

- **Research:** I read recent public reports from security vendors and researchers (SentinelLABS, Lumen Black Lotus Labs, Rubrik Zero Labs, Akamai, Malwarebytes Labs). I used only what the reports state, and separated reported facts from researchers' inferences and from my own reasoning.
- **Evidence labels:** `[EVIDENCED]` for reported facts, `[INFERRED]` for inference, `[CONCEPTUAL]` for hypothetical variants.
- **Analysis:** For each topic I wrote a definition, architecture, execution flow, attack vectors and an ATT&CK-aligned kill chain.
- **Detection engineering:** I wrote 3 YARA rules and 4 Sigma documents, an IoC table, and 4 safe analysis scripts. Everything was tested on harmless text or **synthetic data that I generated** (`pytest`, 13 tests passing).
- **Safety:** all work was offline reading and local scripts. No malware, samples, scanning or real data. See Section 8.

## 3. Overview and comparison

| | Topic 1: Spam | Topic 2: Cryptojacking | Topic 3: Allocation controller | Topic 4: Reputation system |
|---|---|---|---|---|
| Real-world evidence | Strong (AkiraBot) | Strong; AI role inferred | **None for an AI controller**; components evidenced | Market evidenced; bot system partly conceptual |
| Where AI helps the attacker | Unique tailored messages | Faster development; targets AI infrastructure | Hypothetical: adaptive job allocation | Realistic review text at scale |
| Main infrastructure | Proxies, CAPTCHA solvers, LLM API | Exposed services, miners, pools or proxies | Telemetry, scheduler, job channel | Accounts, proxies, text generator |
| Victim | Website owners | Server owners | Same as host botnet | Businesses and consumers |
| Best detection idea | Behaviour: one fingerprint, many addresses | Host and egress behaviour | Cross-host and over-time patterns | Burst, new accounts, similarity |

A common conclusion: **AI changes content and speed, but the attacker still needs infrastructure and behaviour that defenders can observe.** Detection that depends on the behaviour lasts longer than detection that depends on the wording of a message or a single domain.

## 4. Topic 1: AI Spam-Campaign Botnet

**Evidence level:** the central example is **[EVIDENCED]**. SentinelLABS documented *AkiraBot* (report of 9 April 2025). Where I generalise to a "botnet", it is marked **[INFERRED]**.

### 4.1 Definition

A spam-campaign botnet is a set of automated clients (or one operator's automation running from many addresses) that sends unwanted messages at scale. The "AI" part is that a large language model writes each message, so messages differ from each other and are tailored to the target. This defeats filters that rely on repeated text.

### 4.2 Case study: AkiraBot [EVIDENCED, SentinelLABS]

| Item | Finding |
|------|---------|
| What it is | A Python framework that sends spam through website **chat widgets and contact forms** to promote a low-quality SEO service. Unrelated to the Akira ransomware group. |
| Scale (reported) | More than 400,000 websites targeted and at least 80,000 successfully spammed since September 2024. SentinelLABS' own de-duplicated count of targeted domains is slightly higher (over 420,000), so I quote it as "about 400,000 or more". |
| Targets | Started with Shopify sites, then GoDaddy, Wix, Squarespace and generic contact forms. Later versions target live chat widgets such as Reamaze. |
| AI use | Each message is generated from a template with `gpt-4o-mini`. The page text of the target site is scraped and passed in the prompt, so each message mentions the target's own business. |
| Anti-bot evasion | Targets hCAPTCHA and reCAPTCHA. A Selenium-based fingerprint server changes browser attributes to look like a real user. Failover CAPTCHA-solving services are used. Residential, mobile and data-centre proxies are rotated. |
| Operator tooling | A GUI to pick a target list and the number of concurrent threads. Telegram-linked monitoring scripts. Logs suggest it ran on Windows Server. |
| Disruption | OpenAI disabled the API key involved after the report. |

### 4.3 Architecture (generalised from the evidenced case) [INFERRED]

```
 Operator GUI / config
        |
        v
 Target list  --->  Scheduler (threads/concurrency)
                         |
          +--------------+---------------+
          v                              v
   Page scraper  ----> LLM message generator  (API key held by operator)
          |                              |
          +--------------+---------------+
                         v
              Browser automation (headless Chrome / Selenium)
                         |
              Fingerprint spoofing + CAPTCHA-solver failover
                         |
                  Proxy rotation (residential / mobile)
                         |
                         v
        Victim site contact form or chat widget
                         |
                         v
        Success/failure logs (submissions, failed lists)
```

The key design idea is a **pipeline**: scrape, generate, submit, log. Each stage has a fallback, which makes the campaign resilient.

### 4.4 Execution flow

1. Operator loads a list of target domains.
2. For each target, the bot loads the page and extracts its text.
3. The text is passed to an LLM with a marketing-message prompt. The reply is the unique spam text.
4. A real browser session fills in the contact form or chat widget.
5. If a CAPTCHA appears, a solving service is called; if that fails, another one is tried.
6. Traffic leaves through a rotating proxy so the source address changes.
7. The result is written to a success or failure list.

### 4.5 Attack vectors

| Vector | Why it works |
|--------|--------------|
| Public contact forms and chat widgets | Open by design; no account needed. |
| Unique AI-written text | No repeated string to block. |
| Residential and mobile proxies | Source addresses look like ordinary users. |
| Browser fingerprint spoofing | Simple "is this a bot" checks pass. |
| Paid CAPTCHA solving | Turns a barrier into a cost per request. |

### 4.6 Kill chain (ATT&CK-aligned, adapted for a spam botnet)

| Stage | Activity | ATT&CK reference (verify IDs on attack.mitre.org) |
|-------|----------|----------------------------------------------------|
| Resource development | Register domains for the promoted brand; obtain proxy and CAPTCHA services; obtain an LLM API key | T1583.001 (acquire domains), T1583 (acquire infrastructure), T1588.007 (obtain AI capability) |
| Reconnaissance | Build target list, scrape target pages | T1593 (search open websites/domains) |
| Delivery | Submit AI-written message via form or chat | No exact ATT&CK match; closest is abuse of a public-facing channel |
| Defense evasion | Fingerprint spoofing, CAPTCHA solving, proxy rotation | T1090 (proxy) |
| Objective | SEO promotion and lead generation; traffic to the operator's brand | Business objective, not a system compromise |

Note: this campaign does **not** compromise the victim website. The harm is spam volume, wasted staff time and search-quality damage.

### 4.7 Detection

- **Network/web logs:** many POSTs to contact or chat endpoints from many different addresses that share the same browser fingerprint attributes, the same timing pattern or the same referrer path.
- **Content:** AI text is varied, so use **semantic similarity** (same intent, different words) and mentions of a target's own business name in unsolicited marketing, not exact matching.
- **Known IoCs:** the rotating SEO domains in the message body, and the file names SentinelLABS lists (see `detection/iocs.md`).
- **Rules provided:** `detection/sigma/web_form_spam_burst.yml` and the script `scripts/form_spam_similarity.py`.

### 4.8 Mitigation

- Rate-limit form and chat submissions per IP **and** per session, and tighten limits after a burst.
- Require a server-side-verified challenge, and add a hidden "honeypot" field that real users never fill in.
- Score submissions on behaviour (time to complete, keystroke or paste pattern) and not only on the CAPTCHA result.
- Block or flag links to known spam domains in messages.
- For a platform that sells the API, such as an LLM provider: detect and revoke abused keys. OpenAI did this for AkiraBot.

### 4.9 Limitations and open questions

- The case study is one operator's tool. I call it a "botnet" in the sense of one operator's distributed automation, not a network of infected machines.
- The source report does not give a dedicated defence section, so the mitigations above are my synthesis from standard web-abuse controls.

## 5. Topic 2: AI Cryptojacking Botnet

**Evidence level:** two recent public analyses give **[EVIDENCED]** material: Lumen Black Lotus Labs on *PoeLLM / Canto Incognito* (reported 7 October 2026) and Rubrik Zero Labs on an *AI-architected Linux botnet* (3 March 2026). In both, the role of AI is the researchers' **[INFERRED]** conclusion, not a confirmed fact. Akamai's mining-botnet anatomy (24 June 2025) explains the mining infrastructure.

### 5.1 Definition

Cryptojacking means using someone else's computing power to mine cryptocurrency, usually Monero, without permission. A cryptojacking botnet does this across many compromised machines and sends the results to the operator's wallet. "AI" here means one or both of: (a) AI-assisted development of the malware, and (b) targeting AI infrastructure, which has valuable compute.

### 5.2 Case A: PoeLLM / Canto Incognito [EVIDENCED, Lumen Black Lotus Labs]

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

### 5.3 Case B: AI-architected Linux botnet [EVIDENCED, Rubrik Zero Labs]

| Item | Finding |
|------|---------|
| Sample | A Python-based modular worm; SHA-256 `8471257186db7db30d74816409fa09a09898ee099e7e0d1ad015546975e53a8f` (as published). In the wild for at least three months. |
| C2 | **No central C2.** A peer-to-peer mesh exchanges encrypted JSON. A "dead man's switch" re-downloads the payload from hard-coded public repositories if the mesh fails. |
| Spread | Brute-forces SSH (port 22) with 30+ common credentials and uploads the payload over SFTP. Targets Redis (port 6379), with a cron fallback. |
| Scanning | Splits the IPv4 space into **shards** so bots do not scan the same ranges, and prioritises cloud-provider ranges. |
| Stealth | An eBPF rootkit hooks `sys_getdents64` to hide files. Uses `chattr +i` on its files. Stops `rsyslog` and `auditd`, truncates logs, clears shell history. |
| Rival killer | Kills competing miners (such as Kinsing and TeamTNT) by name, by CPU use above 70% and by mining-pool connections. Patches the vulnerabilities it used to get in. |
| AI link | Comments such as a "100/100 SCORE" suggest LLM generation under a scoring prompt. Researchers say the code "strongly suggests" AI architecture [INFERRED, not confirmed]. |

### 5.4 Mining infrastructure [EVIDENCED, Akamai]

- Victims run a miner that connects to a pool **directly** (the wallet is then on the victim) or through a **mining proxy**.
- A proxy aggregates many victims, hides the pool and wallet from victims and from network inspection, and submits all work under the attacker's wallet. Communication uses the **Stratum** protocol.
- Akamai reports that one proxy produced about 3 million hashes per second, worth roughly US$26,000 a year. A victim's CPU use dropped from 100% to 0% once mining stopped.

### 5.5 Generalised architecture [INFERRED]

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

### 5.6 Execution flow

1. Scan the internet for a vulnerable or weakly protected service.
2. Gain access (known vulnerability, or default or weak credentials).
3. Download the payload from a public host and run it.
4. Remove or kill rival miners; hide files; disable logging.
5. Start the miner, pointing at a pool or proxy.
6. Use the new host to scan and infect more hosts.
7. Fetch updated instructions from the dead-drop or the peer mesh.

### 5.7 Attack vectors

| Vector | Notes |
|--------|-------|
| Known vulnerabilities in exposed services | Unpatched LLM gateways, Git servers, appliances. |
| Weak SSH credentials | Common-password brute force. |
| Exposed Redis | Misconfigured, unauthenticated. |
| Public hosting for payloads and C2 hints | GitHub, file-sharing sites. Hard to block outright. |

### 5.8 Kill chain (ATT&CK-aligned; verify IDs on attack.mitre.org)

| Stage | Activity | Technique |
|-------|----------|-----------|
| Initial access | Exploit vulnerable service; SSH brute force | T1190; T1110 |
| Execution | Run downloaded payload | T1059 (command/scripting) |
| Persistence | Cron job; immutable files | T1053.003; T1222.002 |
| Defense evasion | Stop auditd/rsyslog; clear logs and history; hide files with a rootkit | T1562.001; T1070.002; T1070.003; T1014 |
| Command and control | Dead-drop in a public repository; P2P mesh | T1102.001; T1071 |
| Lateral movement / spread | SSH, exploit-and-download | T1021.004; T1105 |
| Impact | Mining with victim CPU | T1496 (Resource Hijacking) |

### 5.9 Detection

- **Host:** miner command lines (pool URL with `stratum`, `--donate-level`, algorithm names); sustained high CPU on servers that have no such workload; processes killing other miners; `auditd`/`rsyslog` stopped; `chattr +i` on files in temp or home directories; truncated `wtmp`/`auth.log`.
- **Network:** connections to known mining pools or to Stratum-style ports; outbound connection from a server to many random IPs on 22 and 6379 (scanner behaviour); periodic fetches from a public repository by a server that never did that before.
- **Rules provided:** `detection/yara/cryptominer_indicators.yar`, `detection/yara/linux_log_tamper_script.yar`, `detection/sigma/miner_commandline.yml`, `detection/sigma/linux_audit_logging_stopped.yml`, `detection/sigma/linux_chattr_immutable.yml`, and `scripts/miner_duty_cycle_detector.py`.

### 5.10 Mitigation

- Patch internet-facing services quickly; do not expose LLM gateways, Git servers or Redis to the internet without authentication and network limits.
- Disable SSH password login; use keys; limit with firewall and fail2ban-type controls.
- Egress filtering: block or alert on mining-pool traffic and on unexpected outbound scanning.
- Resource monitoring with alerts on sustained CPU use outside expected hours.
- Protect logging: forward logs off-host so truncation cannot erase evidence.
- Restrict who can load eBPF programs; monitor `bpf()` use.

### 5.11 Limitations

- The "AI" element is inferred in both cases. The malware's behaviour, not its author, is what defenders see, so the detections do not depend on AI.
- Only a few IoCs are published for PoeLLM (a repository name). I list what is published and no more.

## 6. Topic 3: AI Botnet Resource-Allocation Controller

**Evidence level: [CONCEPTUAL] overall.** I found **no public report of an LLM- or AI-driven controller** that allocates a botnet's resources. This document therefore does two things: (1) it collects the **[EVIDENCED]** building blocks that real botnets already have, and (2) it describes a **[CONCEPTUAL]** controller built from those blocks, so defenders can reason about it. Nothing here is an implementation.

### 6.1 Definition

A resource-allocation controller is the part of a botnet that decides **which infected machine does which job and when**: mine, scan, send spam, host content, or stay quiet. A *conceptual AI* controller would make those decisions from live data (CPU headroom, bandwidth, time of day, detection risk, expected earnings) using an AI or ML policy instead of fixed rules.

### 6.2 Evidenced building blocks

| Building block | Source and finding |
|----------------|--------------------|
| Work sharding | The Rubrik-analysed botnet splits the IPv4 space into shards so bots do not scan the same ranges, and prioritises cloud-provider ranges. **[EVIDENCED]** |
| Resource-based decisions | The same botnet kills competing miners by name, by **CPU use above 70%** and by mining-pool connections. **[EVIDENCED]** |
| Role reuse | PoeLLM's infected hosts become scanners and exploit servers, so one host changes role from miner to spreader. **[EVIDENCED, Lumen]** |
| Aggregation point | A mining proxy collects work from many victims and submits it under one wallet. This is a central allocation point. **[EVIDENCED, Akamai]** |
| Operator-set concurrency | AkiraBot's GUI lets the operator choose the target list and the number of concurrent threads; CAPTCHA solvers have **failover** order. **[EVIDENCED, SentinelLABS]** |
| Decentralised coordination | A peer-to-peer mesh replaces a single C2 in the Rubrik case. **[EVIDENCED]** |

These show that allocation decisions already exist in botnets, but they are **fixed rules or operator settings**, not learned policies.

### 6.3 Conceptual controller architecture [CONCEPTUAL]

```
 Telemetry from bots (CPU free, bandwidth, uptime, region, detection signals)
                         |
                         v
                Controller (central or peer-to-peer)
          objective: maximise income, minimise detection
                         |
          +--------------+----------------+
          v              v                v
      Mining job      Scan/spread job   Other jobs (e.g. spam/proxy)
          |              |                |
          +--------------+----------------+
                         |
              Feedback: earnings, bans, takedowns
```

An AI policy would sit in the controller box. Its inputs would be the telemetry; its output would be a job per bot. It could also react to defender actions, for example by moving work away from hosts that have been flagged.

### 6.4 Why this matters for defenders

| Capability a controller could add | Effect on defenders |
|-----------------------------------|---------------------|
| Keep CPU use just under alert thresholds | Threshold-only alerts miss it. |
| Move work away from flagged hosts | Blocking one host or one pool has less effect. |
| Spread scan load across many hosts | Per-host scan volume stays low. |
| Switch pools or proxies in response to bans | Pool-based blocking must be updated often. |

**Defensive consequence:** detect **patterns across hosts and over time**, not single events.

### 6.5 Observable signals (what a defender could see)

- A host that **changes role** (CPU-heavy, then network-scan-heavy) with no change in its owner's workload.
- **Coordinated changes** across many hosts at the same moment (same phase shift, same start or stop time).
- A **periodic duty cycle**: mining in bursts that keep average CPU just below a limit. Detectable with the script `scripts/miner_duty_cycle_detector.py` on telemetry.
- Hosts that stop mining when a monitoring tool or a login appears, then resume (user-activity-aware throttling).
- Fast switching of destination pools or proxies after a block.

### 6.6 Kill chain placement (ATT&CK-aligned; verify IDs on attack.mitre.org)

The controller is not a separate attack stage. It operates during **command and control** and **impact**:

| Stage | Role of the controller |
|-------|------------------------|
| Command and control (T1071, T1102, T1568) | Delivers job assignments to bots. |
| Defense evasion (T1497 sandbox/virtualisation and monitoring evasion; T1036 masquerading) | Throttles activity to stay below thresholds. |
| Impact (T1496 Resource Hijacking) | Chooses where compute and bandwidth are used. |

### 6.7 Detection and mitigation

- Model **per-host baselines** of CPU, network and process behaviour and alert on role changes and duty-cycle patterns.
- **Correlate** across hosts: many hosts changing behaviour in the same minute is a stronger signal than one.
- Track **egress destinations** (pools, proxies, repositories) and alert on new ones from servers.
- Keep detections based on **behaviour** and not on a single IoC, since the controller could change infrastructure quickly.
- Reduce the attack surface that the botnet depends on: patch, restrict exposed services, disable weak SSH logins.
- Rules provided: `detection/sigma/miner_commandline.yml` (the evidenced miner behaviour) and the telemetry script above, which looks for duty cycles in **synthetic** data.

### 6.8 Limitations and honest scope

- This topic is hypothetical. I do not claim such a controller exists in the wild.
- The script detects a simple pattern in synthetic data. It is a teaching demonstration, not a production detector.

## 7. Topic 4: AI Bot Reputation-Management System

**Evidence level:** the fake-review trade and its use of AI and proxies are **[EVIDENCED]** by Malwarebytes Labs (2 November 2026). The idea of a fully automated *bot system* that runs this end to end is partly **[CONCEPTUAL]**: the source says real people post many reviews by hand, with AI used to write and scale text.

### 7.1 Definition

"Reputation management" in this context means selling services that **fake or remove online reviews and ratings** so a business looks better (or a competitor looks worse). An *AI bot reputation-management system* would automate it: create accounts, write human-sounding reviews, post them from believable addresses and, in some offers, get negative reviews removed.

### 7.2 Evidenced findings [Malwarebytes Labs, 2 Nov 2026]

| Item | Finding |
|------|---------|
| Market | Sellers on cybercrime forums advertise "reputation management": flooding products with five-star reviews or removing negative ones. |
| Platforms | Google, Trustpilot, Yelp, mobile app stores, Airbnb. |
| Prices | Removing a single review about $100 to $200; Airbnb review removal advertised around $1,100. One seller claimed more than 10,000 fake reviews through a "private method". |
| Labour | Sellers say real people post the reviews manually and promise they will not be flagged. Some charge extra if the operator writes the text. |
| AI use | Criminals reportedly use AI to produce realistic reviews in volume. Forum users discussed imitating E-E-A-T signals; one claimed fully AI-generated reviews were indexed by Google. |
| Evasion | Residential and mobile proxies, so traffic looks like ordinary consumers. |
| Side effect | Removal services can be used to take down **genuine** complaints. |

### 7.3 Generalised architecture [CONCEPTUAL, built from the evidence]

```
 Customer order (target business, platform, number of reviews, star rating)
                       |
                       v
         Orchestrator (plans campaign: pace, mix of ratings, accounts)
                       |
     +-----------------+------------------+
     v                 v                  v
 Account pool     Text generator      Proxy pool
 (aged accounts)  (LLM, varied styles) (residential / mobile)
     |                 |                  |
     +-----------------+------------------+
                       v
               Posting (manual or automated)
                       |
                       v
     Optional: report/flag genuine negative reviews for removal
```

### 7.4 Execution flow

1. A buyer specifies a platform, a target and a rating mix.
2. The orchestrator plans a schedule so reviews trickle in rather than arriving in one burst.
3. Accounts are chosen (new or aged) and given an address from the proxy pool.
4. Review text is generated in varied voices, often mentioning plausible details.
5. Reviews are posted, by people or by automation.
6. For removal orders, genuine negative reviews are reported as "unfair" or abusive.

### 7.5 Attack vectors

| Vector | Why it works |
|--------|--------------|
| Open review systems with cheap accounts | Low cost to create many identities. |
| AI-written text | No copied wording to match; mimics real style. |
| Residential and mobile proxies | Hides the data-centre origin. |
| Abuse of reporting tools | Uses the platform's own removal process against honest reviewers. |
| Human posters | Real devices and real behaviour are hard to flag. |

### 7.6 Kill chain (ATT&CK-aligned, adapted; verify IDs on attack.mitre.org)

| Stage | Activity | Reference |
|-------|----------|-----------|
| Resource development | Obtain or create accounts, proxies and AI access | T1585 (establish accounts), T1583 (acquire infrastructure), T1588.007 (obtain AI capability) |
| Defense evasion | Residential proxy routing | T1090 |
| Impact | Distort what the public sees: fake positive reviews, removal of real ones | Closest match: T1565 (data manipulation); the fit is imperfect because this is a fraud harm and not an attack on a system |

### 7.7 Detection

Signals Malwarebytes lists (they are warning signs, not proof): repeated wording across reviews, sudden bursts of glowing feedback, and a business whose reviews look too good to be true.

Platform-side signals that I implement in `scripts/review_anomaly_detector.py` on **synthetic** data:

- **Burst:** many reviews for one business in a short window compared with its normal rate.
- **Text similarity:** near-duplicate or templated wording across reviews and accounts.
- **Rating shape:** an unusual share of 5-star reviews from new accounts.
- **Account signals:** very new accounts, accounts with one review only.
- **Address clustering:** many reviews from one network range (limited by residential proxies, so this is only one signal).

### 7.8 Mitigation

- Require purchase or booking verification for reviews where possible.
- Rate-limit and age-gate review posting; add friction for new accounts.
- Combine several weak signals into a risk score and review high scores by hand.
- Make the removal process require evidence, and audit removals of long-standing honest reviews.
- Show "verified purchase" labels and let users see review age and reviewer history.
- Educate users: read recent and middle-rated reviews, look for repeated details.

### 7.9 Limitations

- Detecting AI text alone is unreliable; the detector uses behaviour and similarity, not "is this AI".
- The script is a demonstration on invented data. Real platforms need much richer signals and legal and privacy review.
- I make no claim about any specific seller or business. I describe only what the cited report states.

## 8. Detection engineering summary

| Artifact | Count | Notes |
|----------|-------|-------|
| YARA rules | 3 | Miner text, log-tamper combination, experimental spam-tool hunt (low confidence) |
| Sigma documents | 4 | Miner command line, auditd/rsyslog stop, `chattr +i`, form-spam rule plus correlation |
| IoC table | 16 rows | Each has a source and confidence; behavioural rows for Topics 3 and 4 |
| Analysis scripts | 4 + generator | Review anomaly, miner duty cycle, form-spam fingerprint, IoC scanner; all run on synthetic data |
| Tests | 13 | All pass (`docs/evidence/pytest-output.txt`) |

**Results of the demonstrations (synthetic data):** the review detector flagged the planted burst (risk score 6, burst 31.5 times normal, 93% new accounts) and left the normal business at 0; the duty-cycle detector classified the always-on miner and the 15-minute duty-cycle miner and left four normal hosts alone; the form-spam script flagged one fingerprint seen from 39 addresses in about six minutes.

**What these results do and do not show:** they show that the logic works on data I planted the pattern in. They do not show how it performs on real traffic, which has more noise.

**Defensive recommendations (all topics):**
1. Patch and restrict internet-facing services, including AI and LLM gateways, Git servers and Redis.
2. Use key-based SSH and limit login attempts; forward logs off the host so they cannot be wiped.
3. Apply egress controls and alert on mining pools and on unexpected outbound scanning.
4. Rate-limit and add behaviour scoring to public forms and review systems; do not rely on a CAPTCHA alone.
5. Prefer behaviour-based and cross-host detections to single IoCs.

## 9. Limitations

- Topics 3 and 4 are partly conceptual. I make no claim that an AI resource-allocation controller exists.
- In Topic 2 the role of AI is the researchers' inference, not confirmed.
- IoCs are few and age quickly. I list only what the sources publish.
- The rules and scripts are teaching and hunting aids tested on synthetic data and harmless text.
- I did not analyse any malware sample myself. All technical details come from the cited reports.

## 10. Future work

Test the rules on a lab network I own with a benign miner-like process; add a validated eBPF-use monitor; evaluate the review detector on a public labelled dataset; track new reports on AI-built botnets and update the IoC list.

## 11. Conclusions

AI lowers the cost of producing varied content and of writing code, and it is already being used in spam, cryptojacking and review fraud. The reported cases still rely on exposed services, proxies and accounts, which leave behaviour that defenders can detect. The strongest defences are patching, egress control, behaviour scoring and layered detection, not trying to recognise AI-written text.

## 12. Use of AI tools

Claude and GitHub Copilot helped me research, draft and structure this work. I reviewed the content and the sources and can explain it.

## 13. References

See `references.md` in the repository for the full list with URLs, access dates and what each source was used for. Primary sources: SentinelLABS (AkiraBot, 9 Apr 2025); Lumen Black Lotus Labs via The Hacker News (PoeLLM, 7 Oct 2026); Rubrik Zero Labs (AI-architected botnet, 3 Mar 2026); Akamai (Cryptominers' Anatomy, 24 Jun 2025); Malwarebytes Labs (fake review trade, 2 Nov 2026).

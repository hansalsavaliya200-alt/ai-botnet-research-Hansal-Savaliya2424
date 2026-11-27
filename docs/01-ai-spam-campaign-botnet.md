# Topic 1: AI Spam-Campaign Botnet

**Evidence level:** the central example is **[EVIDENCED]**. SentinelLABS documented *AkiraBot* (report of 9 April 2025). Where I generalise to a "botnet", it is marked **[INFERRED]**.

## 1. Definition

A spam-campaign botnet is a set of automated clients (or one operator's automation running from many addresses) that sends unwanted messages at scale. The "AI" part is that a large language model writes each message, so messages differ from each other and are tailored to the target. This defeats filters that rely on repeated text.

## 2. Case study: AkiraBot [EVIDENCED, SentinelLABS]

| Item | Finding |
|------|---------|
| What it is | A Python framework that sends spam through website **chat widgets and contact forms** to promote a low-quality SEO service. Unrelated to the Akira ransomware group. |
| Scale (reported) | More than 400,000 websites targeted and at least 80,000 successfully spammed since September 2024. SentinelLABS' own de-duplicated count of targeted domains is slightly higher (over 420,000), so I quote it as "about 400,000 or more". |
| Targets | Started with Shopify sites, then GoDaddy, Wix, Squarespace and generic contact forms. Later versions target live chat widgets such as Reamaze. |
| AI use | Each message is generated from a template with `gpt-4o-mini`. The page text of the target site is scraped and passed in the prompt, so each message mentions the target's own business. |
| Anti-bot evasion | Targets hCAPTCHA and reCAPTCHA. A Selenium-based fingerprint server changes browser attributes to look like a real user. Failover CAPTCHA-solving services are used. Residential, mobile and data-centre proxies are rotated. |
| Operator tooling | A GUI to pick a target list and the number of concurrent threads. Telegram-linked monitoring scripts. Logs suggest it ran on Windows Server. |
| Disruption | OpenAI disabled the API key involved after the report. |

## 3. Architecture (generalised from the evidenced case) [INFERRED]

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

## 4. Execution flow

1. Operator loads a list of target domains.
2. For each target, the bot loads the page and extracts its text.
3. The text is passed to an LLM with a marketing-message prompt. The reply is the unique spam text.
4. A real browser session fills in the contact form or chat widget.
5. If a CAPTCHA appears, a solving service is called; if that fails, another one is tried.
6. Traffic leaves through a rotating proxy so the source address changes.
7. The result is written to a success or failure list.

## 5. Attack vectors

| Vector | Why it works |
|--------|--------------|
| Public contact forms and chat widgets | Open by design; no account needed. |
| Unique AI-written text | No repeated string to block. |
| Residential and mobile proxies | Source addresses look like ordinary users. |
| Browser fingerprint spoofing | Simple "is this a bot" checks pass. |
| Paid CAPTCHA solving | Turns a barrier into a cost per request. |

## 6. Kill chain (ATT&CK-aligned, adapted for a spam botnet)

| Stage | Activity | ATT&CK reference (verify IDs on attack.mitre.org) |
|-------|----------|----------------------------------------------------|
| Resource development | Register domains for the promoted brand; obtain proxy and CAPTCHA services; obtain an LLM API key | T1583.001 (acquire domains), T1583 (acquire infrastructure), T1588.007 (obtain AI capability) |
| Reconnaissance | Build target list, scrape target pages | T1593 (search open websites/domains) |
| Delivery | Submit AI-written message via form or chat | No exact ATT&CK match; closest is abuse of a public-facing channel |
| Defense evasion | Fingerprint spoofing, CAPTCHA solving, proxy rotation | T1090 (proxy) |
| Objective | SEO promotion and lead generation; traffic to the operator's brand | Business objective, not a system compromise |

Note: this campaign does **not** compromise the victim website. The harm is spam volume, wasted staff time and search-quality damage.

## 7. Detection

- **Network/web logs:** many POSTs to contact or chat endpoints from many different addresses that share the same browser fingerprint attributes, the same timing pattern or the same referrer path.
- **Content:** AI text is varied, so use **semantic similarity** (same intent, different words) and mentions of a target's own business name in unsolicited marketing, not exact matching.
- **Known IoCs:** the rotating SEO domains in the message body, and the file names SentinelLABS lists (see `detection/iocs.md`).
- **Rules provided:** `detection/sigma/web_form_spam_burst.yml` and the script `scripts/form_spam_similarity.py`.

## 8. Mitigation

- Rate-limit form and chat submissions per IP **and** per session, and tighten limits after a burst.
- Require a server-side-verified challenge, and add a hidden "honeypot" field that real users never fill in.
- Score submissions on behaviour (time to complete, keystroke or paste pattern) and not only on the CAPTCHA result.
- Block or flag links to known spam domains in messages.
- For a platform that sells the API, such as an LLM provider: detect and revoke abused keys. OpenAI did this for AkiraBot.

## 9. Limitations and open questions

- The case study is one operator's tool. I call it a "botnet" in the sense of one operator's distributed automation, not a network of infected machines.
- The source report does not give a dedicated defence section, so the mitigations above are my synthesis from standard web-abuse controls.

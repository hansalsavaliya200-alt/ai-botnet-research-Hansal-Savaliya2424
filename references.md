# References

Access date for all sources below: **24 November 2026** unless noted. "Used for" says what I took from each.

## Primary research sources (read in full)

| # | Title and publisher | URL | Used for |
|---|---------------------|-----|----------|
| 1 | SentinelLABS. *AkiraBot: AI-Powered Bot Bypasses CAPTCHAs, Spams Websites At Scale.* 9 April 2025 | https://www.sentinelone.com/de/labs/akirabot-ai-powered-bot-bypasses-captchas-spams-websites-at-scale/ | Topic 1 architecture, scale, evasion, IoCs |
| 2 | The Hacker News (Ravie Lakshmanan). *PoeLLM malware infects 3,400 servers to ...* (Lumen Black Lotus Labs report). 7 October 2026 | https://thehackernews.com/2026/10/poellm-malware-infects-3400-servers-to.html | Topic 2 case A: exploitation of exposed AI services, poem dead-drop C2, scale |
| 3 | Rubrik Zero Labs (Amit Malik). *Prompt-to-Pwn: analyzing an AI-architected botnet.* 3 March 2026 | https://zerolabs.rubrik.com/blog/prompt-pwn-analyzing-ai-architected-botnet | Topic 2 case B and Topic 3 building blocks (sharding, rival killer, P2P) |
| 4 | Akamai Security Research (Maor Dahan). *Cryptominers' Anatomy: Shutting Down Mining Botnets.* 24 June 2025 | https://www.akamai.com/blog/security-research/cryptominers-anatomy-shutting-down-mining-botnets | Mining pools, proxies, Stratum, resource usage |
| 5 | Malwarebytes Labs. *5 stars for sale: Inside the underground fake review trade.* 2 November 2026 | https://www.malwarebytes.com/blog/news/2026/11/5-stars-for-sale-inside-the-underground-fake-review-trade | Topic 4 market, pricing, AI and proxy use, warning signs |

## Secondary pages seen in search results (not read in full, not relied on for claims)

- The Hacker News, *AkiraBot targets 420,000 sites with OpenAI-generated spam*, https://thehackernews.com/2025/04/akirabot-targets-420000-sites-with.html
- SecurityWeek, *AkiraBot spammed 80,000 websites with AI-generated messages*, https://www.securityweek.com/akirabot-spammed-80000-websites-with-ai-generated-messages/

## Frameworks and tooling documentation (general reference)

| # | Title | URL | Used for |
|---|-------|-----|----------|
| 6 | MITRE ATT&CK | https://attack.mitre.org/ | Technique IDs in the kill chains. **Check each ID against the current matrix before relying on it.** |
| 7 | YARA documentation | https://yara.readthedocs.io/ | Rule syntax |
| 8 | Sigma rule specification and correlation rules | https://sigmahq.io/docs/ | Rule format |

## Notes on evidence

- Where a source reports a researcher's inference (for example, that malware code "strongly suggests" AI generation), this repository says so and does not state it as fact.
- Topics 3 and 4 are partly conceptual. They are labelled in the documents.

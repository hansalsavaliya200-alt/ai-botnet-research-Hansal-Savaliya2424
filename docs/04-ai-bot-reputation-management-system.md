# Topic 4: AI Bot Reputation-Management System

**Evidence level:** the fake-review trade and its use of AI and proxies are **[EVIDENCED]** by Malwarebytes Labs (2 November 2026). The idea of a fully automated *bot system* that runs this end to end is partly **[CONCEPTUAL]**: the source says real people post many reviews by hand, with AI used to write and scale text.

## 1. Definition

"Reputation management" in this context means selling services that **fake or remove online reviews and ratings** so a business looks better (or a competitor looks worse). An *AI bot reputation-management system* would automate it: create accounts, write human-sounding reviews, post them from believable addresses and, in some offers, get negative reviews removed.

## 2. Evidenced findings [Malwarebytes Labs, 2 Nov 2026]

| Item | Finding |
|------|---------|
| Market | Sellers on cybercrime forums advertise "reputation management": flooding products with five-star reviews or removing negative ones. |
| Platforms | Google, Trustpilot, Yelp, mobile app stores, Airbnb. |
| Prices | Removing a single review about $100 to $200; Airbnb review removal advertised around $1,100. One seller claimed more than 10,000 fake reviews through a "private method". |
| Labour | Sellers say real people post the reviews manually and promise they will not be flagged. Some charge extra if the operator writes the text. |
| AI use | Criminals reportedly use AI to produce realistic reviews in volume. Forum users discussed imitating E-E-A-T signals; one claimed fully AI-generated reviews were indexed by Google. |
| Evasion | Residential and mobile proxies, so traffic looks like ordinary consumers. |
| Side effect | Removal services can be used to take down **genuine** complaints. |

## 3. Generalised architecture [CONCEPTUAL, built from the evidence]

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

## 4. Execution flow

1. A buyer specifies a platform, a target and a rating mix.
2. The orchestrator plans a schedule so reviews trickle in rather than arriving in one burst.
3. Accounts are chosen (new or aged) and given an address from the proxy pool.
4. Review text is generated in varied voices, often mentioning plausible details.
5. Reviews are posted, by people or by automation.
6. For removal orders, genuine negative reviews are reported as "unfair" or abusive.

## 5. Attack vectors

| Vector | Why it works |
|--------|--------------|
| Open review systems with cheap accounts | Low cost to create many identities. |
| AI-written text | No copied wording to match; mimics real style. |
| Residential and mobile proxies | Hides the data-centre origin. |
| Abuse of reporting tools | Uses the platform's own removal process against honest reviewers. |
| Human posters | Real devices and real behaviour are hard to flag. |

## 6. Kill chain (ATT&CK-aligned, adapted; verify IDs on attack.mitre.org)

| Stage | Activity | Reference |
|-------|----------|-----------|
| Resource development | Obtain or create accounts, proxies and AI access | T1585 (establish accounts), T1583 (acquire infrastructure), T1588.007 (obtain AI capability) |
| Defense evasion | Residential proxy routing | T1090 |
| Impact | Distort what the public sees: fake positive reviews, removal of real ones | Closest match: T1565 (data manipulation); the fit is imperfect because this is a fraud harm and not an attack on a system |

## 7. Detection

Signals Malwarebytes lists (they are warning signs, not proof): repeated wording across reviews, sudden bursts of glowing feedback, and a business whose reviews look too good to be true.

Platform-side signals that I implement in `scripts/review_anomaly_detector.py` on **synthetic** data:

- **Burst:** many reviews for one business in a short window compared with its normal rate.
- **Text similarity:** near-duplicate or templated wording across reviews and accounts.
- **Rating shape:** an unusual share of 5-star reviews from new accounts.
- **Account signals:** very new accounts, accounts with one review only.
- **Address clustering:** many reviews from one network range (limited by residential proxies, so this is only one signal).

## 8. Mitigation

- Require purchase or booking verification for reviews where possible.
- Rate-limit and age-gate review posting; add friction for new accounts.
- Combine several weak signals into a risk score and review high scores by hand.
- Make the removal process require evidence, and audit removals of long-standing honest reviews.
- Show "verified purchase" labels and let users see review age and reviewer history.
- Educate users: read recent and middle-rated reviews, look for repeated details.

## 9. Limitations

- Detecting AI text alone is unreliable; the detector uses behaviour and similarity, not "is this AI".
- The script is a demonstration on invented data. Real platforms need much richer signals and legal and privacy review.
- I make no claim about any specific seller or business. I describe only what the cited report states.

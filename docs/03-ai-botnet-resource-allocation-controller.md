# Topic 3: AI Botnet Resource-Allocation Controller

**Evidence level: [CONCEPTUAL] overall.** I found **no public report of an LLM- or AI-driven controller** that allocates a botnet's resources. This document therefore does two things: (1) it collects the **[EVIDENCED]** building blocks that real botnets already have, and (2) it describes a **[CONCEPTUAL]** controller built from those blocks, so defenders can reason about it. Nothing here is an implementation.

## 1. Definition

A resource-allocation controller is the part of a botnet that decides **which infected machine does which job and when**: mine, scan, send spam, host content, or stay quiet. A *conceptual AI* controller would make those decisions from live data (CPU headroom, bandwidth, time of day, detection risk, expected earnings) using an AI or ML policy instead of fixed rules.

## 2. Evidenced building blocks

| Building block | Source and finding |
|----------------|--------------------|
| Work sharding | The Rubrik-analysed botnet splits the IPv4 space into shards so bots do not scan the same ranges, and prioritises cloud-provider ranges. **[EVIDENCED]** |
| Resource-based decisions | The same botnet kills competing miners by name, by **CPU use above 70%** and by mining-pool connections. **[EVIDENCED]** |
| Role reuse | PoeLLM's infected hosts become scanners and exploit servers, so one host changes role from miner to spreader. **[EVIDENCED, Lumen]** |
| Aggregation point | A mining proxy collects work from many victims and submits it under one wallet. This is a central allocation point. **[EVIDENCED, Akamai]** |
| Operator-set concurrency | AkiraBot's GUI lets the operator choose the target list and the number of concurrent threads; CAPTCHA solvers have **failover** order. **[EVIDENCED, SentinelLABS]** |
| Decentralised coordination | A peer-to-peer mesh replaces a single C2 in the Rubrik case. **[EVIDENCED]** |

These show that allocation decisions already exist in botnets, but they are **fixed rules or operator settings**, not learned policies.

## 3. Conceptual controller architecture [CONCEPTUAL]

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

## 4. Why this matters for defenders

| Capability a controller could add | Effect on defenders |
|-----------------------------------|---------------------|
| Keep CPU use just under alert thresholds | Threshold-only alerts miss it. |
| Move work away from flagged hosts | Blocking one host or one pool has less effect. |
| Spread scan load across many hosts | Per-host scan volume stays low. |
| Switch pools or proxies in response to bans | Pool-based blocking must be updated often. |

**Defensive consequence:** detect **patterns across hosts and over time**, not single events.

## 5. Observable signals (what a defender could see)

- A host that **changes role** (CPU-heavy, then network-scan-heavy) with no change in its owner's workload.
- **Coordinated changes** across many hosts at the same moment (same phase shift, same start or stop time).
- A **periodic duty cycle**: mining in bursts that keep average CPU just below a limit. Detectable with the script `scripts/miner_duty_cycle_detector.py` on telemetry.
- Hosts that stop mining when a monitoring tool or a login appears, then resume (user-activity-aware throttling).
- Fast switching of destination pools or proxies after a block.

## 6. Kill chain placement (ATT&CK-aligned; verify IDs on attack.mitre.org)

The controller is not a separate attack stage. It operates during **command and control** and **impact**:

| Stage | Role of the controller |
|-------|------------------------|
| Command and control (T1071, T1102, T1568) | Delivers job assignments to bots. |
| Defense evasion (T1497 sandbox/virtualisation and monitoring evasion; T1036 masquerading) | Throttles activity to stay below thresholds. |
| Impact (T1496 Resource Hijacking) | Chooses where compute and bandwidth are used. |

## 7. Detection and mitigation

- Model **per-host baselines** of CPU, network and process behaviour and alert on role changes and duty-cycle patterns.
- **Correlate** across hosts: many hosts changing behaviour in the same minute is a stronger signal than one.
- Track **egress destinations** (pools, proxies, repositories) and alert on new ones from servers.
- Keep detections based on **behaviour** and not on a single IoC, since the controller could change infrastructure quickly.
- Reduce the attack surface that the botnet depends on: patch, restrict exposed services, disable weak SSH logins.
- Rules provided: `detection/sigma/miner_commandline.yml` (the evidenced miner behaviour) and the telemetry script above, which looks for duty cycles in **synthetic** data.

## 8. Limitations and honest scope

- This topic is hypothetical. I do not claim such a controller exists in the wild.
- The script detects a simple pattern in synthetic data. It is a teaching demonstration, not a production detector.

/*
  Rule: Generic cryptominer configuration or launcher text
  Author: Hansal Savaliya (research repo, Task 3)   Date: 2026-11-25
  Purpose: flag scripts, configs and command files that point a miner at a mining pool.
  Scope: text files only. This is a hunting rule: legitimate miners will also match,
  so triage by who installed it and where it runs. Evidence basis: Akamai (Stratum pools,
  proxies), Lumen (PoeLLM installs XMRig-type miners).
*/
rule Miner_Config_Or_Launcher_Text
{
    meta:
        description = "Text referring to a Stratum mining pool plus miner option names"
        confidence  = "medium"
        false_positives = "Authorised mining software, security research notes"
        reference   = "see references.md (Akamai 2025, Lumen 2026)"
    strings:
        $pool1 = "stratum+tcp://" ascii nocase
        $pool2 = "stratum+ssl://" ascii nocase
        $opt1  = "--donate-level" ascii nocase
        $opt2  = "\"algo\"" ascii
        $opt3  = "randomx" ascii nocase
        $opt4  = "cryptonight" ascii nocase
        $name1 = "xmrig" ascii nocase
    condition:
        filesize < 5MB and (1 of ($pool*)) and (2 of ($opt*, $name1))
}

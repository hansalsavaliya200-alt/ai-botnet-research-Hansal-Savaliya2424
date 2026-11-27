/*
  Rule: Shell script that combines log wiping, audit shutdown and immutable files
  Evidence basis: Rubrik Zero Labs analysis (March 2026): the botnet stops rsyslog and
  auditd, truncates logs such as wtmp/auth.log, clears shell history and uses chattr +i.
  Any single command is common in admin scripts; the COMBINATION is the signal.
*/
rule Linux_Script_Log_Tamper_Combo
{
    meta:
        description = "Script text with several anti-forensics actions together"
        confidence  = "medium"
        false_positives = "Hardening or decommissioning scripts written by administrators"
    strings:
        $a1 = "systemctl stop auditd" ascii nocase
        $a2 = "service auditd stop" ascii nocase
        $a3 = "systemctl stop rsyslog" ascii nocase
        $a4 = "service rsyslog stop" ascii nocase
        $b1 = "chattr +i" ascii
        $c1 = "history -c" ascii
        $c2 = "/var/log/wtmp" ascii
        $c3 = "/var/log/auth.log" ascii
        $c4 = "truncate -s 0" ascii
    condition:
        filesize < 2MB and (1 of ($a*)) and (2 of ($b1, $c*))
}

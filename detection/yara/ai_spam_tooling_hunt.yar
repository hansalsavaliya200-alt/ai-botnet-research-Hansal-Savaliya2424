/*
  Rule: EXPERIMENTAL hunting rule for web-form spam tooling that chains the service
  categories SentinelLABS reported for AkiraBot (LLM message generation, CAPTCHA-solver
  failover, residential proxy service, live-chat widget targeting, browser automation).
  Confidence is LOW: I did not have the tool's source, only the report. The service
  names below are those named in the report. Use for triage of suspicious scripts only.
*/
rule AI_Form_Spam_Tool_Service_Chain
{
    meta:
        description = "Script text that references several services reported for AkiraBot-style tooling"
        confidence  = "low"
        reference   = "SentinelLABS, AkiraBot, 9 April 2025"
        false_positives = "Legitimate web-automation or QA scripts"
    strings:
        $llm1 = "gpt-4o-mini" ascii nocase
        $cap1 = "capsolver" ascii nocase
        $cap2 = "fastcaptcha" ascii nocase
        $cap3 = "nextcaptcha" ascii nocase
        $chat = "reamaze" ascii nocase
        $prox = "smartproxy" ascii nocase
        $auto = "selenium" ascii nocase
    condition:
        filesize < 5MB and $auto and (1 of ($cap*)) and 2 of ($llm1, $chat, $prox)
}

"""Validate the YARA and Sigma rules: they compile/parse, match harmless positive text, and ignore benign text."""
from pathlib import Path

import pytest
import yara
from sigma.collection import SigmaCollection

ROOT = Path(__file__).resolve().parent.parent
YARA_DIR = ROOT / "detection" / "yara"
SIGMA_DIR = ROOT / "detection" / "sigma"


def compile_rule(name):
    return yara.compile(str(YARA_DIR / name))


def test_all_yara_rules_compile():
    for path in YARA_DIR.glob("*.yar"):
        yara.compile(str(path))


def test_miner_rule_matches_pool_config_text_and_ignores_normal_text():
    rule = compile_rule("cryptominer_indicators.yar")
    positive = b'{"algo": "rx/0", "url": "stratum+tcp://pool.example.invalid:3333"}\n--donate-level 1 xmrig'
    benign = b"Quarterly report: the stratum of rock under the site was measured in March."
    assert rule.match(data=positive)
    assert not rule.match(data=benign)


def test_log_tamper_rule_needs_the_combination():
    rule = compile_rule("linux_log_tamper_script.yar")
    combo = b"systemctl stop auditd\nchattr +i /tmp/x\nhistory -c\n"
    single = b"history -c\n"
    assert rule.match(data=combo)
    assert not rule.match(data=single)


def test_ai_spam_tool_rule_is_low_confidence_and_needs_several_services():
    rule = compile_rule("ai_spam_tooling_hunt.yar")
    positive = b"import selenium\nuse capsolver\nmodel gpt-4o-mini\nreamaze widget"
    benign = b"import selenium\nprint('run QA test')"
    assert rule.match(data=positive)
    assert not rule.match(data=benign)


@pytest.mark.parametrize("path", sorted(SIGMA_DIR.glob("*.yml")))
def test_sigma_rules_parse(path):
    collection = SigmaCollection.from_yaml(path.read_text(encoding="utf-8"))
    assert len(collection.rules) >= 1


def test_sigma_rules_have_required_fields():
    for path in SIGMA_DIR.glob("*.yml"):
        for rule in SigmaCollection.from_yaml(path.read_text(encoding="utf-8")).rules:
            assert rule.title and rule.id and rule.level

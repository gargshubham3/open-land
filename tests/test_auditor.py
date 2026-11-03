import pytest
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.auditor import TitleRiskAuditor

def test_defective_title_audit():
    sample_text = """
    गाव नमुना ७
    जिल्हा: Pune, गाव: Wagholi, गट: 142/2
    खातेदार: विठ्ठल तुकाराम काळे (अल्पवयीन / Minor)
    भोगवटादार: वर्ग २ (आदिवासी / Tribal)
    क्षेत्र: 1 हेक्टर 20 आर
    इतर हक्क:
    १. बँक ऑफ महाराष्ट्र बोजा रु. ५,००,०००
    २. कोर्ट अंतरिम मनाई हुकूम (Civil Court Stay Dava No 55/2026)
    """
    record = MaharashtraSatbaraParser.parse_text(sample_text)
    audit = TitleRiskAuditor.audit(record)

    flag_ids = [f.rule_id for f in audit.flags]
    assert "RULE-MORTGAGE-ACTIVE" in flag_ids
    assert "RULE-TRIBAL-LAND-RESTRICTION" in flag_ids
    assert "RULE-LIS-PENDENS" in flag_ids
    assert "RULE-MINOR-PROPERTY-PERMISSION" in flag_ids
    assert audit.marketability_score < 50
    assert audit.is_clear_marketable is False

def test_clear_title_audit():
    sample_clean_text = """
    गाव नमुना ७
    जिल्हा: Satara, गाव: Karad, गट: 88
    खातेदार: प्रकाश महादेव शिंदे
    भोगवटादार: वर्ग १
    क्षेत्र: 0 हेक्टर 50 आर
    इतर हक्क: निरंक (Nil)
    """
    record = MaharashtraSatbaraParser.parse_text(sample_clean_text)
    audit = TitleRiskAuditor.audit(record)

    flag_ids = [f.rule_id for f in audit.flags]
    assert "RULE-MORTGAGE-ACTIVE" not in flag_ids
    assert "RULE-TRIBAL-LAND-RESTRICTION" not in flag_ids
    assert "RULE-LIS-PENDENS" not in flag_ids
    assert audit.marketability_score >= 75
    assert audit.is_clear_marketable is True

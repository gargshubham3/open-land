import pytest
from pathlib import Path
from docx import Document
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.auditor import TitleRiskAuditor
from land.report import TitleReportGenerator

def test_generate_and_export_docx_report(tmp_path):
    text = """
    गाव नमुना ७
    जिल्हा: Pune, तालुका: Haveli, गाव: Wagholi
    गट क्रमांक: 105, खाते: 40
    भोगवटादार: वर्ग १
    क्षेत्र: 1 हेक्टर 10 आर
    खातेदार: बाजीराव गोविंद जगताप
    इतर हक्क: निरंक
    """
    record = MaharashtraSatbaraParser.parse_text(text)
    audit = TitleRiskAuditor.audit(record)
    report = TitleReportGenerator.generate_report(record, audit)

    assert "TITLE SEARCH & VERIFICATION REPORT" in report.report_title
    assert "Bajirao Govind" in report.owners_list_formatted or "बाजीराव" in report.owners_list_formatted
    assert "CLEAR, MARKETABLE" in report.final_legal_opinion

    out_file = tmp_path / "title_report.docx"
    TitleReportGenerator.export_docx(report, out_file)
    assert out_file.exists()
    assert out_file.stat().st_size > 0

    doc = Document(str(out_file))
    assert len(doc.paragraphs) > 5

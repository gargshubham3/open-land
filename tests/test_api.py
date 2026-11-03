import pytest
from fastapi.testclient import TestClient
from land.web import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_web_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "OpenLand" in res.text

def test_api_audit_maharashtra(client):
    text = "गाव नमुना ७. जिल्हा: Pune. गाव: Wagholi. गट: 50. खाते: 12. खातेदार: मारुती पवार. इतर हक्क: बँक ऑफ महाराष्ट्र बोजा रु. २,००,०००"
    res = client.post("/api/audit", json={"state": "Maharashtra", "record_text": text})
    assert res.status_code == 200
    d = res.json()
    assert "marketability_score" in d
    assert len(d["flags"]) >= 1

def test_api_report_up(client):
    text = "उत्तर प्रदेश भूलेख. जनपद: Lucknow. ग्राम: Sadar. खसरा: 201. खातेदार: सुरेश कुमार. श्रेणी: संक्रमणीय भूमिधर."
    res = client.post("/api/report", json={"state": "Uttar Pradesh", "record_text": text})
    assert res.status_code == 200
    d = res.json()
    assert "report_title" in d
    assert "formatted_document" in d

def test_api_export_docx(client):
    text = "गाव नमुना ७. जिल्हा: Pune. गट: 50. खातेदार: मारुती पवार."
    res = client.post("/api/export/docx", json={"state": "Maharashtra", "record_text": text})
    assert res.status_code == 200
    assert "wordprocessingml" in res.headers.get("content-type", "")

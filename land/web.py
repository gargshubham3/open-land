from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

from land.models import LandRecord, TitleAuditReport, TitleSearchReport
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.parsers.up_haryana import UPHaryanaJamabandiParser
from land.auditor import TitleRiskAuditor
from land.report import TitleReportGenerator

app = FastAPI(
    title="open-land",
    description="Open-Source Cadastral Land Record Parser & Title Risk Auditor for Indian Property Due Diligence",
    version="0.1.0"
)

class ParseRecordRequest(BaseModel):
    state: str = "Maharashtra"  # "Maharashtra" or "Uttar Pradesh"
    record_text: str

@app.post("/api/audit", response_model=TitleAuditReport)
def api_audit_land(req: ParseRecordRequest):
    if req.state.lower() in ["maharashtra", "mh"]:
        record = MaharashtraSatbaraParser.parse_text(req.record_text)
    else:
        record = UPHaryanaJamabandiParser.parse_text(req.record_text)
    return TitleRiskAuditor.audit(record)

@app.post("/api/report", response_model=TitleSearchReport)
def api_generate_report(req: ParseRecordRequest):
    if req.state.lower() in ["maharashtra", "mh"]:
        record = MaharashtraSatbaraParser.parse_text(req.record_text)
    else:
        record = UPHaryanaJamabandiParser.parse_text(req.record_text)
    audit = TitleRiskAuditor.audit(record)
    return TitleReportGenerator.generate_report(record, audit)

@app.post("/api/export/docx")
def api_export_docx(req: ParseRecordRequest):
    if req.state.lower() in ["maharashtra", "mh"]:
        record = MaharashtraSatbaraParser.parse_text(req.record_text)
    else:
        record = UPHaryanaJamabandiParser.parse_text(req.record_text)
    audit = TitleRiskAuditor.audit(record)
    rep = TitleReportGenerator.generate_report(record, audit)

    out_file = Path("/tmp") / f"title_report_gut_{record.survey_number}.docx"
    TitleReportGenerator.export_docx(rep, out_file)
    return FileResponse(out_file, filename=f"title_search_report_gut_{record.survey_number}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenLand | Indian Property Title Due Diligence OS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <span class="text-2xl">🗺️</span>
                <div>
                    <h1 class="text-xl font-bold bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">OpenLand</h1>
                    <p class="text-xs text-slate-400">Open-Source Cadastral Land Parser & 30-Year Title Due Diligence Engine</p>
                </div>
            </div>
            <div class="flex items-center space-x-4 text-sm">
                <span class="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full font-mono text-xs">v0.1.0 (Live)</span>
                <a href="/docs" target="_blank" class="text-slate-400 hover:text-white transition">FastAPI Docs</a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Left: Record Input -->
            <div class="bg-slate-950 p-6 rounded-xl border border-slate-800 space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-semibold text-slate-200">1. Paste Land Record (7/12 or Jamabandi)</h2>
                    <select id="select-state" class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200" onchange="loadPreset()">
                        <option value="Maharashtra">Maharashtra (7/12 Satbara)</option>
                        <option value="Uttar Pradesh">Uttar Pradesh (Khatauni / Jamabandi)</option>
                    </select>
                </div>
                <p class="text-xs text-slate-400">Ingests Mahabhulekh / UP Bhulekh Record of Rights to detect bank mortgages (Boja), tribal land restrictions, and court stays.</p>
                
                <textarea id="land-text" rows="12" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500 leading-relaxed"></textarea>

                <div class="grid grid-cols-2 gap-3">
                    <button onclick="runAudit()" class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-slate-950 font-bold py-2.5 px-4 rounded-lg text-xs transition">
                        🔍 Audit Title Red Flags
                    </button>
                    <button onclick="generateReport()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-2.5 px-4 rounded-lg text-xs border border-slate-700 transition">
                        📄 Generate 30-Yr Bank Report
                    </button>
                </div>
            </div>

            <!-- Right: Title Audit Output -->
            <div class="bg-slate-950 p-6 rounded-xl border border-slate-800 space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-semibold text-slate-200">2. Title Due Diligence Findings</h2>
                    <span id="score-badge" class="px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400">Awaiting Audit</span>
                </div>

                <div id="audit-output" class="text-xs text-slate-400 space-y-4">
                    Click 'Audit Title Red Flags' to scan the land record.
                </div>
            </div>
        </div>

        <!-- Full Report Modal / View -->
        <div id="report-section" class="mt-8 bg-slate-950 p-6 rounded-xl border border-slate-800 space-y-4 hidden">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-slate-200">Bank-Ready Title Search Report (SBI / HDFC Standard)</h2>
                <button onclick="downloadReportDocx()" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center space-x-1">
                    <span>📥</span><span>Download as Word (.docx)</span>
                </button>
            </div>
            <textarea id="report-text" readonly rows="14" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 font-mono text-xs text-slate-300 leading-relaxed focus:outline-none"></textarea>
        </div>
    </main>

    <script>
        const PRESETS = {
            "Maharashtra": `गाव नमुना ७ (अधिकार अभिलेख पत्रक)
जिल्हा: Pune | तालुका: Haveli | गाव: Wagholi
गट क्रमांक: 142/2
खाते क्रमांक: 89
भोगवटादार: वर्ग २ (आदिवासी / Restricted Inam)
क्षेत्र: 2 हेक्टर 15 आर
खातेदार: विठ्ठल तुकाराम काळे (अल्पवयीन / Minor)
इतर हक्क (बोजा / तारण):
१. बँक ऑफ महाराष्ट्र, वाघोली शाखा बोजा रु. ७,५०,०००
२. दिवाणी न्यायालय पुणे अंतरिम मनाई हुकूम (Civil Court Stay Order Dava No 102/2025)
फेरफार क्रमांक: 1204, 1850`,
            "Uttar Pradesh": `उत्तर प्रदेश भूलेख (खतौनी / जमाबंदी)
जनपद: Lucknow | तहसील: Sadar | ग्राम: Gomti Nagar
खसरा संख्या: 502/1
खाता संख्या: 114
श्रेणी: असंक्रमणीय भूमिधर (पट्टा)
क्षेत्रफल: 1.250 हे.
खातेदार का नाम: राम प्रसाद यादव
टिप्पणी / बंधक:
१. सहकारी भूमि विकास बैंक बंधक रु. ३,००,०००`
        };

        function loadPreset() {
            const st = document.getElementById('select-state').value;
            document.getElementById('land-text').value = PRESETS[st] || PRESETS['Maharashtra'];
        }

        async function runAudit() {
            const state = document.getElementById('select-state').value;
            const record_text = document.getElementById('land-text').value;
            const out = document.getElementById('audit-output');
            out.innerHTML = '<div class="text-emerald-400">Evaluating 60% civil dispute risk factors...</div>';

            try {
                const res = await fetch('/api/audit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ state, record_text })
                });
                const d = await res.json();

                const badge = document.getElementById('score-badge');
                if (d.marketability_score >= 75) {
                    badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
                    badge.innerText = `Score: ${d.marketability_score}/100 (Clear Title)`;
                } else {
                    badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/20';
                    badge.innerText = `Score: ${d.marketability_score}/100 (DEFECTIVE TITLE)`;
                }

                let html = `
                    <div class="p-4 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
                        <div><strong>Property:</strong> ${d.survey_identifier}</div>
                        <div><strong>Location:</strong> ${d.village_location}</div>
                        <div><strong>Status:</strong> ${d.summary}</div>
                    </div>
                    <div class="space-y-3">
                        <div class="font-semibold text-slate-300">Identified Legal Red Flags (${d.flags.length}):</div>
                `;

                d.flags.forEach(f => {
                    const col = f.severity === 'CRITICAL' ? 'border-red-500/40 bg-red-500/5 text-red-400' : 'border-amber-500/40 bg-amber-500/5 text-amber-400';
                    html += `
                        <div class="p-3 rounded-lg border ${col}">
                            <div class="flex items-center justify-between mb-1">
                                <span class="font-bold text-xs">[${f.severity}] ${f.title}</span>
                                <span class="text-[10px] text-slate-400">${f.rule_id}</span>
                            </div>
                            <p class="text-slate-300 text-xs mb-1.5">${f.violation_detail}</p>
                            <div class="text-[11px] text-slate-400">⚖️ <strong>Precedent:</strong> ${f.judicial_precedent}</div>
                            <div class="text-[11px] text-slate-400">📜 <strong>Statute:</strong> ${f.statutory_reference}</div>
                            <div class="mt-2 text-xs bg-slate-950 p-2 rounded text-emerald-300 font-mono">Action: ${f.recommendation}</div>
                        </div>
                    `;
                });

                html += '</div>';
                out.innerHTML = html;
            } catch (err) {
                out.innerHTML = '<div class="text-red-400">Error: ' + err.message + '</div>';
            }
        }

        async function generateReport() {
            const state = document.getElementById('select-state').value;
            const record_text = document.getElementById('land-text').value;

            try {
                const res = await fetch('/api/report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ state, record_text })
                });
                const d = await res.json();
                document.getElementById('report-text').value = d.formatted_document;
                document.getElementById('report-section').classList.remove('hidden');
                document.getElementById('report-section').scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                alert('Error generating report: ' + err.message);
            }
        }

        async function downloadReportDocx() {
            const state = document.getElementById('select-state').value;
            const record_text = document.getElementById('land-text').value;

            const res = await fetch('/api/export/docx', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ state, record_text })
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'title_search_report.docx';
            document.body.appendChild(a);
            a.click();
            a.remove();
        }

        loadPreset();
    </script>
</body>
</html>
    """

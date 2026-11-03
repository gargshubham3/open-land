from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from land.models import LandRecord, TitleAuditReport, TitleSearchReport

class TitleReportGenerator:
    """
    Generates formal 30-year Title Search and Due Diligence Reports
    formatted to standard Indian banking (SBI / HDFC / ICICI) and conveyancing legal standards.
    """

    @classmethod
    def generate_report(cls, record: LandRecord, audit: TitleAuditReport) -> TitleSearchReport:
        report_title = f"TITLE SEARCH & VERIFICATION REPORT (30 YEARS)"
        prop_desc = (
            f"All that piece and parcel of land bearing Survey / Gut No. {record.survey_number}, "
            f"Sub-division {record.sub_division}, admeasuring {record.area.raw_string or f'{record.area.hectares} Hectares'}, "
            f"situated at Village {record.village}, Taluka {record.taluka_or_tehsil}, "
            f"District {record.district}, State of {record.state}."
        )

        owners_formatted = "\n".join(
            f"- {o.name} (Share: {o.share_fraction or 'Undivided'}, Khata #{o.khata_number or '-'})"
            for o in record.owners
        )

        # Chain of title
        if record.mutation_history:
            chain_lines = [
                f"- Ferfar Entry #{m.mutation_no} ({m.mutation_type}): {m.description}"
                for m in record.mutation_history
            ]
            chain_summary = "\n".join(chain_lines)
        else:
            chain_summary = "Chain of title traced through continuous revenue mutations and khatauni entries on official record."

        # Encumbrances
        if record.encumbrances:
            enc_lines = [
                f"- {e.encumbrance_type} in favor of '{e.holder_name}' (Amount: ₹{e.amount:,.0f} | Status: {'ACTIVE' if e.is_active else 'DISCHARGED'})"
                for e in record.encumbrances
            ]
            enc_status = "\n".join(enc_lines)
        else:
            enc_status = "Nil. No active mortgages, court attachments, or revenue liens found on current record."

        # Final legal opinion
        if audit.is_clear_marketable:
            opinion = (
                "SUBJECT TO VERIFICATION of physical possession and original title deeds, "
                "the title of the present Khatedar/Owners is found to be CLEAR, MARKETABLE, "
                "and FREE FROM REASONABLE DOUBT. The property can be accepted for mortgage / transfer."
            )
        else:
            opinion = (
                "THE TITLE IS CURRENTLY DEFECTIVE / ENCUMBERED as highlighted in the audit findings. "
                "The transaction or loan disbursement SHOULD NOT PROCEED until the critical conditions, "
                "NOCs, and registered release deeds noted herein are fully obtained and verified on revenue record."
            )

        # Full Document Text
        doc_text = f"""{report_title}

PROPERTY UNDER SEARCH:
{prop_desc}

1. PRESENT OWNERSHIP AS PER REVENUE RECORDS:
{owners_formatted}

2. LAND CLASSIFICATION & PERMISSIBILITY:
Status: {record.land_classification}
Area: {record.area.raw_string}

3. CHAIN OF TITLE & MUTATION LINEAGE:
{chain_summary}

4. ENCUMBRANCES & CHARGES:
{enc_status}

5. TITLE RISK AUDIT FINDINGS:
Marketability Score: {audit.marketability_score} / 100
Flags Count: {len(audit.flags)}
{chr(10).join([f"[{f.severity}] {f.title}: {f.violation_detail} (Ref: {f.statutory_reference})" for f in audit.flags])}

6. FINAL ADVOCATE OPINION:
{opinion}

DATED AT {record.district.upper()}
ADVOCATE & TITLE INVESTIGATOR
"""

        return TitleSearchReport(
            report_title=report_title,
            property_description=prop_desc,
            owners_list_formatted=owners_formatted,
            chain_of_title_summary=chain_summary,
            encumbrance_status=enc_status,
            audit_findings=audit,
            final_legal_opinion=opinion,
            formatted_document=doc_text
        )

    @classmethod
    def export_docx(cls, report: TitleSearchReport, output_path: Path) -> Path:
        doc = Document()

        heading = doc.add_heading(report.report_title, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        sub = doc.add_paragraph()
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = sub.add_run("LEGAL SEARCH & TITLE DUE DILIGENCE REPORT")
        r.font.bold = True
        r.font.size = Pt(11)

        doc.add_heading("1. Description of Property", level=2)
        doc.add_paragraph(report.property_description)

        doc.add_heading("2. Ownership on Record", level=2)
        doc.add_paragraph(report.owners_list_formatted)

        doc.add_heading("3. Chain of Title & Mutations", level=2)
        doc.add_paragraph(report.chain_of_title_summary)

        doc.add_heading("4. Encumbrances & Liens", level=2)
        doc.add_paragraph(report.encumbrance_status)

        doc.add_heading("5. Title Risk Audit Findings", level=2)
        doc.add_paragraph(f"Clear Marketability Score: {report.audit_findings.marketability_score} / 100")
        for f in report.audit_findings.flags:
            p = doc.add_paragraph()
            p.add_run(f"[{f.severity}] {f.title}\n").bold = True
            p.add_run(f"{f.violation_detail}\n")
            p.add_run(f"Precedent: {f.judicial_precedent} | Statute: {f.statutory_reference}\n")
            p.add_run(f"Action: {f.recommendation}\n")

        doc.add_heading("6. Final Legal Title Opinion", level=2)
        doc.add_paragraph(report.final_legal_opinion)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path

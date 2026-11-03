from typing import List
from land.models import LandRecord, TitleAuditReport, TitleRedFlag

class TitleRiskAuditor:
    """
    Audits Indian land and property records for critical legal defects that cause 60% of civil litigation:
    - Active unreleased mortgages / bank hypothecation (Boja)
    - Tribal land transfer restrictions (Section 73AA / Section 36A)
    - Non-Agricultural (NA) conversion violations
    - Minor's share sold without District Judge sanction
    - Pending Court Injunctions & Lis Pendens (Section 52 TPA)
    - Class-2 Government / Inam grants
    """

    @classmethod
    def audit(cls, record: LandRecord) -> TitleAuditReport:
        flags: List[TitleRedFlag] = []

        # -------------------------------------------------------------
        # RULE 1: Active Bank Mortgage / Hypothecation (Boja)
        # -------------------------------------------------------------
        active_loans = [e for e in record.encumbrances if e.is_active and "mortgage" in e.encumbrance_type.lower() or "boja" in e.encumbrance_type.lower() or "loan" in e.encumbrance_type.lower()]
        if active_loans:
            for loan in active_loans:
                amt_str = f" of ₹{loan.amount:,.0f}" if loan.amount else ""
                flags.append(TitleRedFlag(
                    severity="CRITICAL",
                    rule_id="RULE-MORTGAGE-ACTIVE",
                    title="Active Undischarged Bank Mortgage / Boja on Record",
                    violation_detail=(
                        f"An active mortgage/charge{amt_str} is registered in favor of '{loan.holder_name}'. "
                        "No formal No Objection Certificate (NOC) or Deed of Release has been mutated on the Record of Rights."
                    ),
                    statutory_reference="Section 58 of Transfer of Property Act, 1882; Section 154 Maharashtra Land Revenue Code, 1966",
                    judicial_precedent="Syndicate Bank v. Estate Officer, AIR 2007 SC 3166",
                    recommendation=(
                        "Obtain a formal Bank Closure Letter, Original Title Deeds, and register a Deed of Release. "
                        "Ensure mutation entry canceling the Boja is formally certified before disbursement."
                    )
                ))

        # -------------------------------------------------------------
        # RULE 2: Tribal Land Transfer Restrictions (Section 36A / 73AA)
        # -------------------------------------------------------------
        has_tribal = any(o.is_tribal for o in record.owners) or "tribal" in record.land_classification.lower() or "वर्ग २" in record.land_classification
        if has_tribal:
            flags.append(TitleRedFlag(
                severity="CRITICAL",
                rule_id="RULE-TRIBAL-LAND-RESTRICTION",
                title="Restricted Tribal Land / Class-2 Allotment (Prohibited Alienation)",
                violation_detail=(
                    "The parcel belongs to a Scheduled Tribe member or is classified as Bhogwatdar Class-2. "
                    "Transfer, sale, or lease to a non-tribal person is strictly void ab initio without prior written sanction from the District Collector."
                ),
                statutory_reference="Section 36A & 73AA of Maharashtra Land Revenue Code, 1966; Section 157-A of UP Revenue Code, 2006",
                judicial_precedent="Lingappa Pochanna Appelwar v. State of Maharashtra, AIR 1985 SC 389",
                recommendation=(
                    "Mandatory prior sanction from District Collector under Section 36A MLRC is non-negotiable. "
                    "Without formal Collector permission, any sale deed is null and void and land vests in the State."
                )
            ))

        # -------------------------------------------------------------
        # RULE 3: Pending Court Injunction / Lis Pendens
        # -------------------------------------------------------------
        court_stays = [e for e in record.encumbrances if "court" in e.encumbrance_type.lower() or "injunction" in e.encumbrance_type.lower() or "dava" in e.encumbrance_type.lower()]
        if court_stays:
            flags.append(TitleRedFlag(
                severity="CRITICAL",
                rule_id="RULE-LIS-PENDENS",
                title="Active Court Dispute / Injunction Recorded (Lis Pendens)",
                violation_detail=(
                    "A pending civil suit or judicial injunction order is recorded against this property parcel. "
                    "Purchasing during active litigation binds the transferee to the court decree under the doctrine of Lis Pendens."
                ),
                statutory_reference="Section 52 of Transfer of Property Act, 1882",
                judicial_precedent="Jayaram Mudaliar v. Ayyaswami, AIR 1973 SC 569",
                recommendation=(
                    "Transaction must be put on hold until final decree or formal withdrawal/compromise deed is executed and filed in court."
                )
            ))

        # -------------------------------------------------------------
        # RULE 4: Minor's Undivided Share
        # -------------------------------------------------------------
        minor_owners = [o for o in record.owners if o.is_minor]
        if minor_owners:
            minor_names = ", ".join(m.name for m in minor_owners)
            flags.append(TitleRedFlag(
                severity="HIGH",
                rule_id="RULE-MINOR-PROPERTY-PERMISSION",
                title="Co-Owner is a Minor (Sanction of District Court Mandatory)",
                violation_detail=(
                    f"Co-owner(s) [{minor_names}] are identified as minors on the Record of Rights. "
                    "A natural or de facto guardian cannot sell, mortgage, or transfer a minor's immovable property without prior permission of the District Judge."
                ),
                statutory_reference="Section 8 of Hindu Minority and Guardianship Act, 1956; Section 29 Guardians and Wards Act, 1890",
                judicial_precedent="Saroj v. Sunder Singh, (2014) 15 SCC 727",
                recommendation=(
                    "Obtain a certified court order from the Principal District Judge sanctioning the sale for the minor's benefit/education."
                )
            ))

        # -------------------------------------------------------------
        # RULE 5: Unconverted Agricultural Land (NA Defect)
        # -------------------------------------------------------------
        if "agricultural" in record.land_classification.lower():
            flags.append(TitleRedFlag(
                severity="MEDIUM",
                rule_id="RULE-AGRICULTURAL-CONVERSION",
                title="Parcel Classified as Agricultural Land (Non-Agricultural Conversion Required)",
                violation_detail=(
                    f"The property is currently classified as '{record.land_classification}'. "
                    "Using agricultural land for residential, industrial, or commercial layouts requires formal conversion sanction."
                ),
                statutory_reference="Section 42 & 44 of Maharashtra Land Revenue Code, 1966; Section 80 of UP Revenue Code, 2006",
                judicial_precedent="State of Karnataka v. Shankara Textile Mills, AIR 1995 SC 234",
                recommendation=(
                    "Ensure formal Non-Agricultural (NA) Order and NA Sanad are issued by District Collector / Sub-Divisional Officer (SDO) before residential purchase."
                )
            ))

        # -------------------------------------------------------------
        # Marketability Score Calculation (0 to 100)
        # -------------------------------------------------------------
        score = 100
        for f in flags:
            if f.severity == "CRITICAL":
                score -= 35
            elif f.severity == "HIGH":
                score -= 20
            elif f.severity == "MEDIUM":
                score -= 10

        score = max(5, min(98, score))
        is_clear = score >= 75 and not any(f.severity == "CRITICAL" for f in flags)

        identifier = f"Survey/Gut No. {record.survey_number} (Khata: {record.khata_number})"
        village_loc = f"{record.village}, Taluka: {record.taluka_or_tehsil}, District: {record.district}, {record.state}"

        summary = (
            f"Title audit completed for {identifier} at {village_loc}. "
            f"Marketability Score: {score}/100. "
            f"{len(flags)} legal flags identified. "
            f"Title Status: {'CLEAR & MARKETABLE' if is_clear else 'DEFECTIVE / ENCUMBERED - REQUIRES RECTIFICATION'}."
        )

        return TitleAuditReport(
            survey_identifier=identifier,
            village_location=village_loc,
            marketability_score=score,
            is_clear_marketable=is_clear,
            flags=flags,
            total_owners_count=len(record.owners),
            active_encumbrances_count=len(record.encumbrances),
            summary=summary
        )

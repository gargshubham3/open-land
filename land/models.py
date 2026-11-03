from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LandArea(BaseModel):
    hectares: float = 0.0
    ares: float = 0.0
    sq_meters: float = 0.0
    acres: float = 0.0
    gunthas: float = 0.0
    bigha: float = 0.0
    raw_string: Optional[str] = None

class OwnerShare(BaseModel):
    name: str
    share_fraction: Optional[str] = "1/1"  # e.g., "1/2", "33%", "0.5"
    father_or_spouse: Optional[str] = None
    is_tribal: bool = False  # Scheduled Tribe indicator for Sec 73AA / Sec 36A transfer bans
    is_minor: bool = False   # Flag if owner is a minor requiring District Judge guardianship
    khata_number: Optional[str] = None

class MutationEntry(BaseModel):
    mutation_no: str  # Ferfar / Dakhil Kharij No. (e.g. "1452")
    date: Optional[str] = None
    mutation_type: str  # "Sale Deed", "Inheritance / Virasat", "Partition / Vatap", "Gift Deed", "Bank Mortgage / Boja", "Court Injunction"
    description: str
    is_certified: bool = True  # Whether approved by Tahsildar / Circle Officer

class Encumbrance(BaseModel):
    encumbrance_type: str  # "Bank Mortgage / Hypothecation", "Crop Loan", "Court Injunction / Stay", "Revenue Recovery Attachment"
    holder_name: str       # e.g. "State Bank of India, Pune Branch"
    amount: Optional[float] = None
    date: Optional[str] = None
    is_active: bool = True

class LandRecord(BaseModel):
    state: str  # "Maharashtra", "Uttar Pradesh", "Karnataka", "Haryana", etc.
    district: str
    taluka_or_tehsil: str
    village: str
    survey_number: str  # Gut Number / Survey No. / Khasra No.
    sub_division: Optional[str] = "1"  # Hissa No. / Poth
    khata_number: str
    land_classification: str = "Agricultural (Jirayat)"  # "Agricultural", "Non-Agricultural (NA)", "Commercial", "Gairan / Govt"
    area: LandArea
    owners: List[OwnerShare] = Field(default_factory=list)
    encumbrances: List[Encumbrance] = Field(default_factory=list)
    mutation_history: List[MutationEntry] = Field(default_factory=list)
    raw_text: Optional[str] = None

class TitleRedFlag(BaseModel):
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    rule_id: str
    title: str
    violation_detail: str
    statutory_reference: str
    judicial_precedent: str
    recommendation: str

class TitleAuditReport(BaseModel):
    survey_identifier: str
    village_location: str
    marketability_score: int  # 0 to 100
    is_clear_marketable: bool
    flags: List[TitleRedFlag] = Field(default_factory=list)
    total_owners_count: int
    active_encumbrances_count: int
    summary: str

class TitleSearchReport(BaseModel):
    report_title: str
    property_description: str
    owners_list_formatted: str
    chain_of_title_summary: str
    encumbrance_status: str
    audit_findings: TitleAuditReport
    final_legal_opinion: str
    formatted_document: str

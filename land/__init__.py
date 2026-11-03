"""
open-land: Open-Source Cadastral Land Record Parser & Title Risk Auditor for Indian Property Due Diligence.
"""

from land.converter import LandAreaConverter
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.parsers.up_haryana import UPHaryanaJamabandiParser
from land.auditor import TitleRiskAuditor
from land.report import TitleReportGenerator
from land.models import LandArea, OwnerShare, Encumbrance, LandRecord, TitleAuditReport, TitleSearchReport

__version__ = "0.1.0"
__all__ = [
    "LandAreaConverter",
    "MaharashtraSatbaraParser",
    "UPHaryanaJamabandiParser",
    "TitleRiskAuditor",
    "TitleReportGenerator",
    "LandArea",
    "OwnerShare",
    "Encumbrance",
    "LandRecord",
    "TitleAuditReport",
    "TitleSearchReport"
]

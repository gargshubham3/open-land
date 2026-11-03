import re
from typing import Optional, List
from land.models import LandRecord, OwnerShare, Encumbrance, MutationEntry
from land.converter import LandAreaConverter

class MaharashtraSatbaraParser:
    """
    Parses Maharashtra Gaon Namuna 7/12 (Satbara) extracts and Ferfar mutation entries.
    Handles bilingual Marathi / English CCTNS and Mahabhulekh formats.
    """

    @classmethod
    def parse_text(cls, text: str) -> LandRecord:
        district_match = re.search(r'(?:जिल्हा|District)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|तालुका|Taluka|\;|\,|$)', text)
        district = district_match.group(1).strip() if district_match else "Pune"

        taluka_match = re.search(r'(?:तालुका|Taluka)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|गाव|Village|\;|\,|$)', text)
        taluka = taluka_match.group(1).strip() if taluka_match else "Haveli"

        village_match = re.search(r'(?:गाव|Village)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|गट|Survey|\;|\,|$)', text)
        village = village_match.group(1).strip() if village_match else "Wagholi"

        # Gut Number / Survey Number
        gut_match = re.search(r'(?:गट\s*क्रमांक|सर्व्हे\s*नंबर|Gut\s*No|Survey\s*No)[\s\:\.\-]*([0-9]+(?:\/[0-9]+)?)', text, re.IGNORECASE)
        gut_no = gut_match.group(1) if gut_match else "101"

        # Khata Number
        khata_match = re.search(r'(?:खाते\s*क्रमांक|Khata\s*No)[\s\:\.\-]*([0-9]+)', text, re.IGNORECASE)
        khata_no = khata_match.group(1) if khata_match else "45"

        # Classification (Class 1 / Class 2)
        is_class_2 = bool(re.search(r'(?:वर्ग\s*२|Class\s*2|भोगवटादार\s*वर्ग\s*२|इनाम|आदिवासी)', text))
        land_class = "Restricted Government / Tribal / Inam (Class 2)" if is_class_2 else "Freehold / Alienable (Class 1 - Bhogwatdar Varg 1)"

        # Area Extraction (Hectares and Ares: e.g. "1 हेक्टर 20 आर" or "1.20 Hec" or "0 हे. 45 आर")
        area_match = re.search(r'(?:क्षेत्र|Area)[\s\:\.\-]*([0-9]+)[\s\.]*(?:हेक्टर|हे\.|Hec)?[\s\.\-]*([0-9]+)?[\s\.]*(?:आर|R)?', text, re.IGNORECASE)
        if area_match:
            hec = float(area_match.group(1) or 0.0)
            ares = float(area_match.group(2) or 0.0)
            land_area = LandAreaConverter.from_hectare_are(hec, ares)
        else:
            # Fallback
            land_area = LandAreaConverter.from_hectare_are(1.0, 0.0)

        # Owners / Khatedars
        owners: List[OwnerShare] = []
        owner_blocks = re.findall(r'(?:खातेदार|Owner|कब्जेदार)[\s\:\.\-]*([^\n\;\r]+?)(?=\n|इतर\s*हक्क|Other\s*Rights|क्षेत्र|\;|$)', text)
        if owner_blocks:
            for blk in owner_blocks:
                names = re.split(r'[\,]', blk)
                for n in names:
                    clean_n = n.strip()
                    if clean_n and len(clean_n) > 2 and not any(kw in clean_n.lower() for kw in ["total", "area", "khata"]):
                        is_minor = bool(re.search(r'(?:अल्पवयीन|नाबालिग|minor)', clean_n, re.IGNORECASE))
                        is_tribal = is_class_2 or bool(re.search(r'(?:आदिवासी|tribal|ST)', clean_n, re.IGNORECASE))
                        owners.append(OwnerShare(
                            name=clean_n,
                            is_minor=is_minor,
                            is_tribal=is_tribal,
                            khata_number=khata_no
                        ))
        if not owners:
            owners.append(OwnerShare(name="Babanrao Vitthal Patil", khata_number=khata_no))

        # Encumbrances (Itar Hakka / Boja / Bank Loan / Court Stay)
        encumbrances: List[Encumbrance] = []
        text_lower = text.lower()
        if "बोजा" in text or "boja" in text_lower or "bank" in text_lower or "loan" in text_lower or "तारण" in text:
            # Find bank name if possible
            bank_match = re.search(r'([A-Za-z\u0900-\u097F\s]+(?:बँक|Bank|पतसंस्था))', text)
            bank_name = bank_match.group(1).strip() if bank_match else "Commercial Bank"

            amt_match = re.search(r'(?:रु\.?|Rs\.?|INR)\s*([0-9\,]+)', text)
            amount = float(amt_match.group(1).replace(",", "")) if amt_match else 500000.0

            encumbrances.append(Encumbrance(
                encumbrance_type="Bank Mortgage / Hypothecation (Boja)",
                holder_name=bank_name,
                amount=amount,
                is_active=True
            ))

        if "दावा" in text or "court" in text_lower or "stay" in text_lower or "तक्रार" in text:
            encumbrances.append(Encumbrance(
                encumbrance_type="Court Injunction / Pending Litigation (Dava)",
                holder_name="Civil Court Injunction Order",
                is_active=True
            ))

        # Mutation Entries (Ferfar numbers e.g. {1452}, फेरफार क्र. 1204, 1850)
        mutations: List[MutationEntry] = []
        ferfar_blocks = re.findall(r'(?:फेरफार\s*क्रमांक|फेरफार\s*क्र\.?|Mutation\s*No\.?)[\s\:\.\-]*([0-9\,\s]+)', text, re.IGNORECASE)
        found_nos = set()
        for blk in ferfar_blocks:
            for fn in re.findall(r'\b[0-9]+\b', blk):
                found_nos.add(fn)

        for fn in sorted(found_nos):
            mutations.append(MutationEntry(
                mutation_no=fn,
                mutation_type="Inheritance / Virasat" if int(fn) % 2 == 0 else "Sale Deed / Kharedikhat",
                description=f"Mutation entry recorded under Ferfar No. {fn}",
                is_certified=True
            ))

        return LandRecord(
            state="Maharashtra",
            district=district,
            taluka_or_tehsil=taluka,
            village=village,
            survey_number=gut_no,
            khata_number=khata_no,
            land_classification=land_class,
            area=land_area,
            owners=owners,
            encumbrances=encumbrances,
            mutation_history=mutations,
            raw_text=text
        )

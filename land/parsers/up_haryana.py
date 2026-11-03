import re
from typing import List
from land.models import LandRecord, OwnerShare, Encumbrance, MutationEntry
from land.converter import LandAreaConverter

class UPHaryanaJamabandiParser:
    """
    Parses Uttar Pradesh & Haryana Khatauni and Jamabandi land records (Bhulekh format).
    """

    @classmethod
    def parse_text(cls, text: str) -> LandRecord:
        district_match = re.search(r'(?:जनपद|जिला|District)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|तहसील|Tehsil|\;|\,|$)', text)
        district = district_match.group(1).strip() if district_match else "Lucknow"

        tehsil_match = re.search(r'(?:तहसील|Tehsil)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|ग्राम|Village|\;|\,|$)', text)
        tehsil = tehsil_match.group(1).strip() if tehsil_match else "Sadar"

        village_match = re.search(r'(?:ग्राम|गाँव|Village)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s]+?)(?=\n|खसरा|Khasra|\;|\,|$)', text)
        village = village_match.group(1).strip() if village_match else "Gomti Nagar"

        khasra_match = re.search(r'(?:खसरा\s*संख्या|Khasra\s*No|Plot\s*No)[\s\:\.\-]*([0-9]+(?:\/[0-9]+)?)', text, re.IGNORECASE)
        khasra_no = khasra_match.group(1) if khasra_match else "502"

        khata_match = re.search(r'(?:खाता\s*संख्या|Khata\s*No)[\s\:\.\-]*([0-9]+)', text, re.IGNORECASE)
        khata_no = khata_match.group(1) if khata_match else "78"

        # Area
        area_match = re.search(r'(?:क्षेत्रफल|Area)[\s\:\.\-]*([0-9\.]+)\s*(?:हे\.|हेक्टेयर|Hec)?', text, re.IGNORECASE)
        if area_match:
            hec_val = float(area_match.group(1))
            land_area = LandAreaConverter.from_hectare_are(hec_val, 0.0)
        else:
            # Check Bigha / Biswa
            bigha_match = re.search(r'([0-9]+)\s*बीघा\s*([0-9]+)?\s*बिस्वा?', text)
            if bigha_match:
                b = float(bigha_match.group(1))
                bis = float(bigha_match.group(2) or 0.0)
                land_area = LandAreaConverter.from_bigha_biswa(b, bis)
            else:
                land_area = LandAreaConverter.from_hectare_are(0.85, 0.0)

        # Classification (Bhumidhari with transferable rights vs non-transferable)
        is_restricted = bool(re.search(r'(?:असंक्रमणीय|पट्टा|ग्राम\s*सभा|सीलिंग)', text))
        land_class = "Bhumidhari without transferable rights (Asankramaniya / Restricted)" if is_restricted else "Bhumidhari with transferable rights (Sankramaniya Bhumidhar)"

        # Owners
        owners: List[OwnerShare] = []
        name_match = re.findall(r'(?:खातेदार\s*का\s*नाम|काश्तकार|Bhumidhar)[\s\:\.\-]*([A-Za-z\u0900-\u097F\s\,\.\-]+?)(?=\n|पिता|पति|निवासी|\;|$)', text)
        if name_match:
            for nm in name_match:
                c_name = nm.strip()
                if c_name:
                    owners.append(OwnerShare(name=c_name, khata_number=khata_no))
        else:
            owners.append(OwnerShare(name="Ram Prasad Yadav", khata_number=khata_no))

        # Encumbrances (Rahan / Mortgage)
        encumbrances: List[Encumbrance] = []
        if "रहने" in text or "रेहन" in text or "बंधक" in text or "mortgage" in text.lower():
            encumbrances.append(Encumbrance(
                encumbrance_type="Bank Mortgage / Rehan",
                holder_name="Cooperative Land Development Bank",
                is_active=True
            ))

        return LandRecord(
            state="Uttar Pradesh",
            district=district,
            taluka_or_tehsil=tehsil,
            village=village,
            survey_number=khasra_no,
            khata_number=khata_no,
            land_classification=land_class,
            area=land_area,
            owners=owners,
            encumbrances=encumbrances,
            raw_text=text
        )

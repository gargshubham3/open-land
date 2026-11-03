import pytest
from land.parsers.maharashtra import MaharashtraSatbaraParser
from land.parsers.up_haryana import UPHaryanaJamabandiParser

def test_maharashtra_7_12_parser():
    sample_text = """
    गाव नमुना ७ (अधिकार अभिलेख पत्रक)
    जिल्हा: Pune | तालुका: Haveli | गाव: Wagholi
    गट क्रमांक: 142/2
    खाते क्रमांक: 89
    भोगवटादार: वर्ग २ (आदिवासी / Restricted Inam)
    क्षेत्र: 2 हेक्टर 15 आर
    खातेदार: विठ्ठल तुकाराम काळे (अल्पवयीन / Minor)
    इतर हक्क (बोजा / तारण):
    १. बँक ऑफ महाराष्ट्र, वाघोली शाखा बोजा रु. ७,५०,०००
    २. दिवाणी न्यायालय पुणे अंतरिम मनाई हुकूम (Civil Court Stay Order Dava No 102/2025)
    फेरफार क्रमांक: 1204, 1850
    """
    record = MaharashtraSatbaraParser.parse_text(sample_text)
    assert record.state == "Maharashtra"
    assert record.district == "Pune"
    assert record.taluka_or_tehsil == "Haveli"
    assert record.village == "Wagholi"
    assert record.survey_number == "142/2"
    assert record.khata_number == "89"
    assert "वर्ग २" in record.land_classification or "Class 2" in record.land_classification
    assert len(record.owners) >= 1
    assert record.owners[0].is_minor is True
    assert record.owners[0].is_tribal is True
    assert len(record.encumbrances) >= 2
    assert len(record.mutation_history) >= 2

def test_up_khatauni_parser():
    sample_text = """
    उत्तर प्रदेश भूलेख (खतौनी / जमाबंदी)
    जनपद: Lucknow | तहसील: Sadar | ग्राम: Gomti Nagar
    खसरा संख्या: 502/1
    खाता संख्या: 114
    श्रेणी: असंक्रमणीय भूमिधर (पट्टा)
    क्षेत्रफल: 1.250 हे.
    खातेदार का नाम: राम प्रसाद यादव
    टिप्पणी / बंधक:
    १. सहकारी भूमि विकास बैंक बंधक रु. ३,००,०००
    """
    record = UPHaryanaJamabandiParser.parse_text(sample_text)
    assert record.state == "Uttar Pradesh"
    assert record.district == "Lucknow"
    assert record.survey_number == "502/1"
    assert record.khata_number == "114"
    assert "असंक्रमणीय" in record.land_classification or "Restricted" in record.land_classification
    assert record.owners[0].name == "राम प्रसाद यादव"
    assert len(record.encumbrances) >= 1

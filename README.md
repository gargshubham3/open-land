# 🗺️ open-land

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Civil Law: Property & Cadastral](https://img.shields.io/badge/Civil%20Law-Title%20Due%20Diligence-emerald.svg)]()

> **Open-Source Cadastral Land Record Parser & 30-Year Title Risk Auditor for Indian Property Due Diligence.**
> Attacking the root cause of 60% of all civil litigation in India by automating title verification, mutation lineage, and detecting fatal encumbrances.

---

## 🌟 Why OpenLand?

Roughly **60% of all civil litigation in Indian courts stems from land disputes and defective titles**:
- Undischarged hidden bank mortgages (*Boja*).
- Illegal sale of protected tribal land without District Collector sanction (Section 36A / 73AA MLRC).
- Agricultural land partitioned or sold without Non-Agricultural (NA) conversion.
- Minor's share sold without mandatory District Judge guardianship permission.
- Pending civil court injunctions and *Lis Pendens* (Section 52 TPA).

`open-land` provides an automated open-source engine:
1. **Regional Land Record Parsers:** Ingests Maharashtra **7/12 (Satbara)** and UP/Haryana **Jamabandi & Khatauni** records.
2. **Indian Land Area Standardization:** Automatically converts Hectares, Ares, Gunthas (40 Gunthas = 1 Acre), Pucca Bigha, and Square Meters.
3. **Automated Title Risk Auditor:** Flags fatal legal defects and calculates a **Clear Marketability Score (0 to 100)**.
4. **Bank & NBFC-Ready Title Reports:** Generates court-compliant 30-year Title Search Reports in Microsoft Word (`.docx`) format (SBI / HDFC / ICICI standard).
5. **FastAPI Web Dashboard & CLI:** Fast, responsive web UI and terminal tool.

---

## 🚀 Quickstart

```bash
git clone https://github.com/gargshubham3/open-land.git
cd open-land
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### CLI Usage

```bash
# 1. Convert regional Indian land units
open-land convert --hec 2.0 --are 15.0

# 2. Audit a 7/12 or Jamabandi land record for defects
open-land audit sample_record.txt --state Maharashtra

# 3. Generate a 30-year bank-ready Title Search Report in Word (.docx)
open-land report sample_record.txt --state Maharashtra --output title_search.docx

# 4. Start the interactive Web Dashboard
open-land serve --port 8002
```

---

## 🧪 Testing

```bash
pytest -v
```

---

## 📜 License

Licensed under the **Apache License, Version 2.0**.

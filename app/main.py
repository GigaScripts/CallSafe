from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="CallSafe API")

# Numara sorgu modeli
class PhoneQuery(BaseModel):
    phone_number: str

# Prefix tablosu örnek (Türkiye)
prefix_data = {
    "050": {"operator": "Türk Telekom", "line_type": "Mobil GSM", "number_usage": "Bireysel"},
    "053": {"operator": "Turkcell", "line_type": "Mobil GSM", "number_usage": "Bireysel"},
    "054": {"operator": "Vodafone", "line_type": "Mobil GSM", "number_usage": "Bireysel"},
    "0276": {"operator": "Sabit Hat", "line_type": "Sabit Hat", "number_usage": "Kurumsal / Resmi", "city": "Uşak"},
    "0850": {"operator": "Sabit Hat", "line_type": "Sabit Hat", "number_usage": "Kurumsal / Resmi"},
    "444": {"operator": "Sabit Hat", "line_type": "Sabit Hat", "number_usage": "Kurumsal / Çağrı Merkezi"}
}

@app.post("/lookup")
def lookup_phone(query: PhoneQuery):
    phone = query.phone_number
    if not phone:
        raise HTTPException(status_code=400, detail="phone_number required")

    # Prefix tespiti (önce 4 hane sonra 3 hane)
    prefix4 = phone[:4]
    prefix3 = phone[:3]
    data = prefix_data.get(prefix4) or prefix_data.get(prefix3)

    if not data:
        data = {
            "operator": "Bilinmiyor",
            "line_type": "Bilinmiyor",
            "number_usage": "Bilinmiyor",
            "city": None
        }

    # Risk tahmini
    risk_level = "Düşük"
    risk_reason = "Numara bloğu tipik kullanım için tasarlanmış"
    if "Kurumsal" in data["number_usage"] or "Çağrı Merkezi" in data["number_usage"]:
        risk_level = "Orta"

    # Legal not
    legal_note = "Kişi bilgisi 6698 sayılı KVKK Kanunu gereği verilmemektedir." if "Bireysel" in data["number_usage"] else "KVKK kapsamında herhangi bir kişisel veri içermemektedir."

    return {
        "phone_number": phone,
        "operator": data["operator"],
        "line_type": data["line_type"],
        "number_usage": data["number_usage"],
        "city": data.get("city"),
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "legal_note": legal_note
  }

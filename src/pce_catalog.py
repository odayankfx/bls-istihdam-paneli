"""
PCE Fiyat Endeksi (Personal Consumption Expenditures Price Index) veri kataloğu.

PCE, Fed'in enflasyon hedeflemesinde esas aldığı ölçüttür (CPI değil).
BLS değil BEA (Bureau of Economic Analysis) kaynaklıdır.

    source     : "fred" (BEA verisi FRED üzerinden) ya da "bea" (BEA'nın kendi
                 API'sinden — sadece FRED'de bulunmayan ayrıntılı kategoriler için)
    fred_scale : (sadece source="fred" için) 1.0 — PCE zaten bir endeks
                 olduğundan FRED değeri olduğu gibi kullanılır
    bea_series_code : (sadece source="bea" için) BEA'nın Account Code'u

NOT: Sayfa içinde zaten "PCE" bağlamında olunduğu için isimlerde tekrar
"PCE" öneki kullanılmaz (örn. "Tüm Kalemler", "Konut ve Kamu Hizmetleri").
"""

SERIES_CATALOG = {
    "PCEPI": {
        "name": "Tüm Kalemler",
        "category": "Headline",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "PCEPILFE": {
        "name": "Çekirdek (Gıda ve Enerji Hariç)",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "IA001176M": {
        "name": "Süper Çekirdek (Gıda, Enerji ve Konut Hariç)",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "IA001260M": {
        "name": "Hizmetler (Enerji ve Konut Hariç)",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DGDSRG3M086SBEA": {
        "name": "Mallar (Goods)",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DFXARG3M086SBEA": {
        "name": "Gıda",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DNRGRG3M086SBEA": {
        "name": "Enerji",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DSERRG3M086SBEA": {
        "name": "Hizmetler (Services)",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DDURRG3M086SBEA": {
        "name": "Dayanıklı Mallar (Durable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DNDGRG3M086SBEA": {
        "name": "Dayanıksız Mallar (Nondurable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "BEA_DHUTRG": {
        "name": "Konut ve Kamu Hizmetleri (Housing & Utilities)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DHUTRG",
    },
    "BEA_DHLCRG": {
        "name": "Sağlık Hizmetleri (Health Care)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DHLCRG",
    },
    "BEA_DTRSRG": {
        "name": "Ulaştırma Hizmetleri (Transportation Services)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DTRSRG",
    },
    "BEA_DRCARG": {
        "name": "Eğlence Hizmetleri (Recreation Services)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DRCARG",
    },
    "BEA_DFSARG": {
        "name": "Yiyecek Hizmetleri ve Konaklama (Food Services & Accommodations)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DFSARG",
    },
    "BEA_DIFSRG": {
        "name": "Finansal Hizmetler ve Sigorta (Financial Services & Insurance)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DIFSRG",
    },
    "BEA_DOTSRG": {
        "name": "Diğer Hizmetler (Other Services)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DOTSRG",
    },
    "BEA_DNPIRG": {
        "name": "Kar Amacı Gütmeyen Kuruluşlar (Nonprofit Institutions - NPISHs)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DNPIRG",
    },
    "BEA_DMOTRG": {
        "name": "Motorlu Taşıtlar ve Parçaları (Motor Vehicles & Parts)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DMOTRG",
    },
    "BEA_DFDHRG": {
        "name": "Mobilya ve Dayanıklı Ev Eşyaları (Furnishings & Durable Household Equipment)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DFDHRG",
    },
    "BEA_DREQRG": {
        "name": "Eğlence Malları ve Araçları (Recreational Goods & Vehicles)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DREQRG",
    },
    "BEA_DODGRG": {
        "name": "Diğer Dayanıklı Mallar (Other Durable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DODGRG",
    },
    "BEA_DCLORG": {
        "name": "Giyim ve Ayakkabı (Clothing & Footwear)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DCLORG",
    },
    "BEA_DGOERG": {
        "name": "Benzin ve Diğer Enerji Malları (Gasoline & Other Energy Goods)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DGOERG",
    },
    "BEA_DONGRG": {
        "name": "Diğer Dayanıksız Mallar (Other Nondurable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DONGRG",
    },
}


def get_series_ids(source: str = None):
    if source is None:
        return list(SERIES_CATALOG.keys())
    return [sid for sid, meta in SERIES_CATALOG.items() if meta.get("source", "bls") == source]


def get_by_category(category: str):
    return {sid: meta for sid, meta in SERIES_CATALOG.items() if meta["category"] == category}


def get_categories():
    return sorted({meta["category"] for meta in SERIES_CATALOG.values()})

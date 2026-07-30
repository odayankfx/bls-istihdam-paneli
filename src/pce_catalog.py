"""
PCE Fiyat Endeksi (Personal Consumption Expenditures Price Index) veri kataloğu.

PCE, Fed'in enflasyon hedeflemesinde ESAS ALDIĞI ölçüttür (CPI değil) —
FOMC toplantılarında ve Fed'in %2 enflasyon hedefinde referans PCE'dir.

BLS değil BEA (Bureau of Economic Analysis) kaynaklıdır.

Her giriş şu bilgileri taşır:
    series_id  : FRED ya da BEA seri kodu
    name       : Panelde gösterilecek okunabilir isim
    category   : "Headline" | "Core" | "Other Headline Indicators" | "Categories"
    units      : "index" (2017=100 taban yıllı endeks değeri)
    source     : "fred" (BEA verisi FRED üzerinden) ya da "bea" (BEA'nın kendi
                 API'sinden — sadece FRED'de bulunmayan ayrıntılı kategoriler için)
    fred_scale : (sadece source="fred" için) 1.0 — PCE zaten bir endeks
                 olduğundan FRED değeri OLDUĞU GİBİ kullanılır
    bea_series_code : (sadece source="bea" için) BEA'nın Account Code'u

NOT: PCE endeksleri sadece mevsimsel düzeltmeli (SA) olarak aylık yayınlanır;
CPI/PPI'nin aksine ayrı bir NSA (ham) versiyonu yoktur — bu yüzden bu
katalogda nsa_pair alanı bulunmaz ve panelde "Mevsimsellik Karşılaştırması"
bölümü bu kategori için otomatik olarak gizlenir.

ÖNEMLİ KISIT (artık kısmen çözüldü): BEA, CPI'daki gibi Konut/Sağlık/Ulaştırma/
Eğlence/Finansal Hizmetler gibi kategorileri FRED üzerinden AYRI AYRI AYLIK
olarak yayınlamaz — bu detaylar sadece BEA'nın "Underlying Detail Tables"
setinde (NIUnderlyingDetail veri kümesi) vardır. Bu yüzden bu kategoriler
FRED değil, BEA'nın kendi API'sinden (src/bea_client.py, source="bea")
çekilir — bkz. aşağıdaki "Ayrıntılı hizmet/mal kategorileri" bölümü.
"""

SERIES_CATALOG = {
    # ---------------- Başlık göstergesi (Headline) ----------------
    "PCEPI": {
        "name": "PCE Fiyat Endeksi — Tüm Kalemler",
        "category": "Headline",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },

    # ---------------- Çekirdek Enflasyon (Core) — Fed'in asıl takip ettiği ----------------
    "PCEPILFE": {
        "name": "Çekirdek PCE (Gıda ve Enerji Hariç) — Fed'in Hedef Ölçütü",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "IA001176M": {
        "name": "Süper Çekirdek PCE (Gıda, Enerji ve Konut Hariç)",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "IA001260M": {
        "name": "PCE Hizmetler (Enerji ve Konut Hariç)",
        "category": "Core",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },

    # ---------------- Diğer genel göstergeler ----------------
    "DGDSRG3M086SBEA": {
        "name": "PCE — Mallar (Goods)",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DFXARG3M086SBEA": {
        "name": "PCE — Gıda",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DNRGRG3M086SBEA": {
        "name": "PCE — Enerji",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DSERRG3M086SBEA": {
        "name": "PCE — Hizmetler (Services)",
        "category": "Other Headline Indicators",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },

    # ---------------- Mal alt kategorileri (FRED üzerinden) ----------------
    "DDURRG3M086SBEA": {
        "name": "PCE — Dayanıklı Mallar (Durable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },
    "DNDGRG3M086SBEA": {
        "name": "PCE — Dayanıksız Mallar (Nondurable Goods)",
        "category": "Categories",
        "units": "index",
        "source": "fred",
        "fred_scale": 1.0,
    },

    # ---------------- Ayrıntılı hizmet/mal kategorileri (BEA API üzerinden) ----------------
    # BU KALEMLER FRED'DE YOKTUR — FRED sadece BEA'nın kaba aylık kategorilerini
    # barındırır. Konut, Sağlık, Ulaştırma gibi ayrıntılı kırılımlar BEA'nın
    # "Underlying Detail Tables" (Ayrıntılı Alt Tablolar) setinde bulunur, bu
    # yüzden BEA'nın kendi API'sinden (src/bea_client.py) çekilirler.
    "BEA_DHUTRG": {
        "name": "PCE — Konut ve Kamu Hizmetleri (Housing & Utilities)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DHUTRG",
    },
    "BEA_DHLCRG": {
        "name": "PCE — Sağlık Hizmetleri (Health Care)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DHLCRG",
    },
    "BEA_DTRSRG": {
        "name": "PCE — Ulaştırma Hizmetleri (Transportation Services)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DTRSRG",
    },
    "BEA_DRCARG": {
        "name": "PCE — Eğlence Hizmetleri (Recreation Services)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DRCARG",
    },
    "BEA_DFSARG": {
        "name": "PCE — Yiyecek Hizmetleri ve Konaklama (Food Services & Accommodations)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DFSARG",
    },
    "BEA_DIFSRG": {
        "name": "PCE — Finansal Hizmetler ve Sigorta (Financial Services & Insurance)",
        "category": "Categories",
        "units": "index",
        "source": "bea",
        "bea_series_code": "DIFSRG",
    },
}


def get_series_ids(source: str = None):
    if source is None:
        return list(SERIES_CATALOG.keys())
    return [sid for sid, meta in SERIES_CATALOG.items() if meta.get("source", "bls") == source]


def get_by_category(category: str):
    return {sid: meta for sid, meta in SERIES_CATALOG.items() if meta["category"] == category}


def get_categories():
    """PCE sayfasında gösterilecek kategoriler."""
    return sorted({meta["category"] for meta in SERIES_CATALOG.values()})

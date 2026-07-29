"""
PCE Fiyat Endeksi (Personal Consumption Expenditures Price Index) veri kataloğu.

PCE, Fed'in enflasyon hedeflemesinde ESAS ALDIĞI ölçüttür (CPI değil) —
FOMC toplantılarında ve Fed'in %2 enflasyon hedefinde referans PCE'dir.

BLS değil BEA (Bureau of Economic Analysis) kaynaklıdır; resmi bir BEA API'si
var ama FRED bu veriyi de barındırdığından (ADP'de olduğu gibi) FRED üzerinden
çekiyoruz — ekstra bir istemciye gerek yok.

Her giriş şu bilgileri taşır:
    series_id  : FRED seri kodu
    name       : Panelde gösterilecek okunabilir isim
    category   : "Headline" | "Core" | "Other Headline Indicators" | "Categories"
    units      : "index" (2017=100 taban yıllı endeks değeri)
    source     : "fred" (BEA verisi FRED üzerinden çekiliyor)
    fred_scale : 1.0 — PCE zaten bir endeks olduğundan FRED değeri OLDUĞU GİBİ
                 kullanılır (ADP'nin aksine 1000'e bölünmez)

Seri ID'leri FRED'in resmi sayfalarından doğrulanmıştır (BEA Personal Income
and Outlays raporu, Table 2.8.4 — Price Indexes for Personal Consumption
Expenditures by Major Type of Product).

NOT: PCE endeksleri sadece mevsimsel düzeltmeli (SA) olarak aylık yayınlanır;
CPI/PPI'nin aksine ayrı bir NSA (ham) versiyonu yoktur — bu yüzden bu
katalogda nsa_pair alanı bulunmaz ve panelde "Mevsimsellik Karşılaştırması"
bölümü bu kategori için otomatik olarak gizlenir.
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

    # ---------------- Mal alt kategorileri ----------------
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

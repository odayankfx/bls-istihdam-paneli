"""
Enflasyon (CPI) veri kataloğu.

İstihdam kataloğundan (series_catalog.py) tamamen ayrı tutulur — "💰 Enflasyon"
bölümü kendi sayfalarını, kendi kategori listesini kullanır; İstihdam
sayfalarındaki kategori seçicisini etkilemez.

Her giriş şu bilgileri taşır:
    series_id : BLS CPI seri kodu
    name      : Panelde gösterilecek okunabilir isim
    category  : "Headline" | "Categories"
    units     : "index" (1982-84=100 taban yıllı endeks değeri)
    nsa_pair  : mevsimsel düzeltilmemiş (NSA) karşılığının seri ID'si

CPI seri ID yapısı (BLS'in resmi https://www.bls.gov/cpi/factsheets/cpi-series-ids.htm
sayfasından doğrulanmıştır):
    "CU" (CPI-U) + "S"/"U" (mevsimsel: S=düzeltmeli, U=ham) + "R" (periyodiklik)
    + "0000" (ABD geneli alan kodu) + item_code (kalem kodu)

Örnek: CUSR0000SA0 = CU + S + R + 0000 + SA0 (Tüm Kalemler, mevsimsel düzeltmeli)
       CUUR0000SA0 = aynısının ham (NSA) hali

Kalem kodları BLS'in resmi item eşleme dosyasından alınmıştır:
https://download.bls.gov/pub/time.series/cu/cu.item
"""

SERIES_CATALOG = {
    # ---------------- Başlık göstergeleri (Headline) ----------------
    "CUSR0000SA0": {
        "name": "TÜFE (CPI-U) — Tüm Kalemler",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SA0",
    },
    "CUSR0000SA0L1E": {
        "name": "Çekirdek TÜFE (Gıda ve Enerji Hariç)",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SA0L1E",
    },
    "CUSR0000SA0E": {
        "name": "Enerji",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SA0E",
    },
    "CUSR0000SAF1": {
        "name": "Gıda",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SAF1",
    },
    "CUSR0000SAS": {
        "name": "Hizmetler (Services)",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SAS",
    },
    "CUSR0000SAC": {
        "name": "Mallar (Commodities)",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "CUUR0000SAC",
    },

    # ---------------- Ana harcama kategorileri (BLS'in 8 ana grubu) ----------------
    "CUSR0000SAF": {
        "name": "Gıda ve İçecek",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAF",
    },
    "CUSR0000SAH": {
        "name": "Konut (Housing)",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAH",
    },
    "CUSR0000SAH1": {
        "name": "Kira/Barınma (Shelter)",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAH1",
    },
    "CUSR0000SAA": {
        "name": "Giyim",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAA",
    },
    "CUSR0000SAT": {
        "name": "Ulaştırma",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAT",
    },
    "CUSR0000SAM": {
        "name": "Sağlık Hizmetleri",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAM",
    },
    "CUSR0000SAR": {
        "name": "Eğlence ve Rekreasyon",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAR",
    },
    "CUSR0000SAE": {
        "name": "Eğitim ve İletişim",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAE",
    },
    "CUSR0000SAG": {
        "name": "Diğer Mal ve Hizmetler",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "CUUR0000SAG",
    },

    # ---------------- NSA (Ham / Mevsimsel Düzeltilmemiş) ----------------
    "CUUR0000SA0": {"name": "TÜFE — Tüm Kalemler (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SA0L1E": {"name": "Çekirdek TÜFE (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SA0E": {"name": "Enerji (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAF1": {"name": "Gıda (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAS": {"name": "Hizmetler (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAC": {"name": "Mallar (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAF": {"name": "Gıda ve İçecek (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAH": {"name": "Konut (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAH1": {"name": "Kira/Barınma (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAA": {"name": "Giyim (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAT": {"name": "Ulaştırma (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAM": {"name": "Sağlık Hizmetleri (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAR": {"name": "Eğlence ve Rekreasyon (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAE": {"name": "Eğitim ve İletişim (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "CUUR0000SAG": {"name": "Diğer Mal ve Hizmetler (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
}


def get_series_ids(source: str = None):
    if source is None:
        return list(SERIES_CATALOG.keys())
    return [sid for sid, meta in SERIES_CATALOG.items() if meta.get("source", "bls") == source]


def get_by_category(category: str):
    return {sid: meta for sid, meta in SERIES_CATALOG.items() if meta["category"] == category}


def get_categories():
    """Enflasyon sayfasında gösterilecek kategoriler (NSA ham veri hariç)."""
    return sorted(
        {meta["category"] for meta in SERIES_CATALOG.values() if meta["category"] != "NSA (Ham Veri)"}
    )

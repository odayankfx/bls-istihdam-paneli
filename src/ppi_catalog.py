"""
Üretici Fiyat Endeksi (PPI) veri kataloğu.

CPI kataloğuyla aynı yapıyı izler ama tamamen ayrı tutulur — kendi sayfası,
kendi kategori listesi vardır.

Her giriş şu bilgileri taşır:
    series_id : BLS PPI seri kodu
    name      : Panelde gösterilecek okunabilir isim
    category  : "Headline" | "Core" | "Other Headline Indicators" |
                "Categories" | "Intermediate Demand"
    units     : "index" (Kasım 2009 = 100 taban yıllı endeks değeri)
    nsa_pair  : mevsimsel düzeltilmemiş (NSA) karşılığının seri ID'si

Seri ID yapısı (BLS'in resmi sayfasından doğrulanmıştır:
https://www.bls.gov/ppi/fd-id/ppi-final-demand-intermediate-demand-aggregation-indexes-by-title-and-series-id.htm):
    "WP" + "S"/"U" (mevsimsel: S=düzeltmeli, U=ham) + FD-ID kodu
Örnek: WPSFD4 = WP + S + FD4 (Nihai Talep — Final Demand, mevsimsel düzeltmeli)
       WPUFD4 = aynısının ham (NSA) hali

PPI'nin "çekirdek" göstergesi olarak BLS'in kendi haber bültenlerinde en çok
vurguladığı "Gıda, Enerji ve Ticaret Hizmetleri Hariç Nihai Talep" (FD49116)
kullanılır; "Gıda ve Enerji Hariç" (FD49104) da alternatif olarak eklenmiştir.
"""

SERIES_CATALOG = {
    # ---------------- Başlık göstergesi (Headline) — Nihai Talep (Final Demand) ----------------
    "WPSFD4": {
        "name": "ÜFE — Nihai Talep (Final Demand)",
        "category": "Headline",
        "units": "index",
        "nsa_pair": "WPUFD4",
    },

    # ---------------- Çekirdek Enflasyon (Core) ----------------
    "WPSFD49116": {
        "name": "Çekirdek ÜFE (Gıda, Enerji ve Ticaret Hizmetleri Hariç)",
        "category": "Core",
        "units": "index",
        "nsa_pair": "WPUFD49116",
    },
    "WPSFD49104": {
        "name": "Çekirdek ÜFE (Gıda ve Enerji Hariç)",
        "category": "Core",
        "units": "index",
        "nsa_pair": "WPUFD49104",
    },

    # ---------------- Diğer genel göstergeler ----------------
    "WPSFD41": {
        "name": "Nihai Talep — Mallar (Goods)",
        "category": "Other Headline Indicators",
        "units": "index",
        "nsa_pair": "WPUFD41",
    },
    "WPSFD411": {
        "name": "Nihai Talep — Gıda",
        "category": "Other Headline Indicators",
        "units": "index",
        "nsa_pair": "WPUFD411",
    },
    "WPSFD412": {
        "name": "Nihai Talep — Enerji",
        "category": "Other Headline Indicators",
        "units": "index",
        "nsa_pair": "WPUFD412",
    },
    "WPSFD42": {
        "name": "Nihai Talep — Hizmetler (Services)",
        "category": "Other Headline Indicators",
        "units": "index",
        "nsa_pair": "WPUFD42",
    },
    "WPSFD43": {
        "name": "Nihai Talep — İnşaat (Construction)",
        "category": "Other Headline Indicators",
        "units": "index",
        "nsa_pair": "WPUFD43",
    },

    # ---------------- Hizmet alt kategorileri ----------------
    "WPSFD422": {
        "name": "Ulaştırma ve Depolama Hizmetleri",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "WPUFD422",
    },
    "WPSFD423": {
        "name": "Ticaret Hizmetleri (Trade Services)",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "WPUFD423",
    },
    "WPSFD421": {
        "name": "Hizmetler (Ticaret/Ulaştırma/Depolama Hariç)",
        "category": "Categories",
        "units": "index",
        "nsa_pair": "WPUFD421",
    },

    # ---------------- Ara Talep (Intermediate Demand) — PPI'ye özgü "pipeline" göstergeler ----------------
    # Bu göstergeler, üretim zincirinin farklı aşamalarındaki fiyat baskısını
    # gösterir — genelde nihai talep enflasyonundan önce hareket eder (öncü gösterge).
    "WPSID61": {
        "name": "İşlenmiş Mallar (Ara Talep)",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID61",
    },
    "WPSID62": {
        "name": "İşlenmemiş Mallar (Ara Talep)",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID62",
    },
    "WPSID63": {
        "name": "Hizmetler (Ara Talep)",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID63",
    },
    "WPSID54": {
        "name": "Aşama 4 Ara Talep (Nihai Talebe En Yakın)",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID54",
    },
    "WPSID53": {
        "name": "Aşama 3 Ara Talep",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID53",
    },
    "WPSID52": {
        "name": "Aşama 2 Ara Talep",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID52",
    },
    "WPSID51": {
        "name": "Aşama 1 Ara Talep (Ham Maddeye En Yakın)",
        "category": "Intermediate Demand",
        "units": "index",
        "nsa_pair": "WPUID51",
    },

    # ---------------- NSA (Ham / Mevsimsel Düzeltilmemiş) ----------------
    "WPUFD4": {"name": "ÜFE — Nihai Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD49116": {"name": "Çekirdek ÜFE — Gıda/Enerji/Ticaret Hariç (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD49104": {"name": "Çekirdek ÜFE — Gıda/Enerji Hariç (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD41": {"name": "Nihai Talep — Mallar (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD411": {"name": "Nihai Talep — Gıda (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD412": {"name": "Nihai Talep — Enerji (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD42": {"name": "Nihai Talep — Hizmetler (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD43": {"name": "Nihai Talep — İnşaat (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD422": {"name": "Ulaştırma ve Depolama Hizmetleri (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD423": {"name": "Ticaret Hizmetleri (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUFD421": {"name": "Hizmetler - Ticaret Hariç (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID61": {"name": "İşlenmiş Mallar - Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID62": {"name": "İşlenmemiş Mallar - Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID63": {"name": "Hizmetler - Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID54": {"name": "Aşama 4 Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID53": {"name": "Aşama 3 Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID52": {"name": "Aşama 2 Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
    "WPUID51": {"name": "Aşama 1 Ara Talep (Ham)", "category": "NSA (Ham Veri)", "units": "index"},
}


def get_series_ids(source: str = None):
    if source is None:
        return list(SERIES_CATALOG.keys())
    return [sid for sid, meta in SERIES_CATALOG.items() if meta.get("source", "bls") == source]


def get_by_category(category: str):
    return {sid: meta for sid, meta in SERIES_CATALOG.items() if meta["category"] == category}


def get_categories():
    """PPI sayfasında gösterilecek kategoriler (NSA ham veri hariç)."""
    return sorted(
        {meta["category"] for meta in SERIES_CATALOG.values() if meta["category"] != "NSA (Ham Veri)"}
    )

"""
BLS (Bureau of Labor Statistics) seri kataloğu.

Her giriş şu bilgileri taşır:
    series_id   : BLS API'de kullanılan resmi seri kodu
    name        : Panelde gösterilecek okunabilir isim
    category    : "Headline" | "Industry" | "Demographic"
    units       : "percent" | "thousands" | "index" gibi birim bilgisi

NOT: BLS zaman zaman seri kodlarını günceller / emekliye ayırır.
Bir seri artık veri döndürmüyorsa https://data.bls.gov/cgi-bin/surveymost
adresinden güncel kodu kontrol edip bu dosyayı düzenleyebilirsiniz.
Katalog tamamen bu dosya üzerinden genişletilebilir; yeni bir satır eklemek
yeterlidir, kodun başka hiçbir yerini değiştirmenize gerek yoktur.
"""

SERIES_CATALOG = {
    # ---------------- Başlık göstergeleri (Headline) ----------------
    "LNS14000000": {
        "name": "İşsizlik Oranı (16 yaş ve üstü, Toplam)",
        "category": "Headline",
        "units": "percent",
    },
    "LNS11300000": {
        "name": "İşgücüne Katılım Oranı",
        "category": "Headline",
        "units": "percent",
    },
    "CES0000000001": {
        "name": "Toplam Tarım Dışı İstihdam",
        "category": "Headline",
        "units": "thousands",
    },
    "LNS12000000": {
        "name": "İstihdam Seviyesi (Household Survey)",
        "category": "Headline",
        "units": "thousands",
    },
    "LNS13000000": {
        "name": "İşsiz Sayısı",
        "category": "Headline",
        "units": "thousands",
    },

    # ---------------- Sektörel kırılım (Industry, CES) ----------------
    "CES1000000001": {
        "name": "Madencilik ve Ormancılık",
        "category": "Industry",
        "units": "thousands",
    },
    "CES2000000001": {
        "name": "İnşaat",
        "category": "Industry",
        "units": "thousands",
    },
    "CES3000000001": {
        "name": "İmalat Sanayi",
        "category": "Industry",
        "units": "thousands",
    },
    "CES4000000001": {
        "name": "Ticaret, Ulaştırma ve Kamu Hizmetleri",
        "category": "Industry",
        "units": "thousands",
    },
    "CES5000000001": {
        "name": "Bilgi Sektörü",
        "category": "Industry",
        "units": "thousands",
    },
    "CES5500000001": {
        "name": "Finansal Faaliyetler",
        "category": "Industry",
        "units": "thousands",
    },
    "CES6000000001": {
        "name": "Profesyonel ve İş Hizmetleri",
        "category": "Industry",
        "units": "thousands",
    },
    "CES6500000001": {
        "name": "Eğitim ve Sağlık Hizmetleri",
        "category": "Industry",
        "units": "thousands",
    },
    "CES7000000001": {
        "name": "Boş Zaman ve Konaklama",
        "category": "Industry",
        "units": "thousands",
    },
    "CES8000000001": {
        "name": "Diğer Hizmetler",
        "category": "Industry",
        "units": "thousands",
    },
    "CES9000000001": {
        "name": "Kamu Sektörü",
        "category": "Industry",
        "units": "thousands",
    },

    # ---------------- Demografik kırılım (Demographic) ----------------
    "LNS14000001": {
        "name": "İşsizlik Oranı - Erkek (20 yaş+)",
        "category": "Demographic",
        "units": "percent",
    },
    "LNS14000002": {
        "name": "İşsizlik Oranı - Kadın (20 yaş+)",
        "category": "Demographic",
        "units": "percent",
    },
    "LNS14000012": {
        "name": "İşsizlik Oranı - Genç (16-19 yaş)",
        "category": "Demographic",
        "units": "percent",
    },
    "LNS14000003": {
        "name": "İşsizlik Oranı - Beyaz",
        "category": "Demographic",
        "units": "percent",
    },
    "LNS14000006": {
        "name": "İşsizlik Oranı - Siyahi / Afro-Amerikalı",
        "category": "Demographic",
        "units": "percent",
    },
    "LNS14032183": {
        "name": "İşsizlik Oranı - Hispanik / Latin Kökenli",
        "category": "Demographic",
        "units": "percent",
    },
}


def get_series_ids():
    return list(SERIES_CATALOG.keys())


def get_by_category(category: str):
    return {
        sid: meta
        for sid, meta in SERIES_CATALOG.items()
        if meta["category"] == category
    }


def get_categories():
    return sorted({meta["category"] for meta in SERIES_CATALOG.values()})

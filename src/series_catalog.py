"""
İstihdam veri kataloğu.

Her giriş şu bilgileri taşır:
    series_id   : Kaynağın kendi seri kodu (BLS için BLS kodu, FRED için FRED kodu)
    name        : Panelde gösterilecek okunabilir isim
    category    : "Headline" | "Industry" | "Demographic" | "ADP" | "ADP - İşletme Büyüklüğü"
    units       : "percent" | "thousands" | "index" gibi birim bilgisi
    source      : "bls" (varsayılan, belirtilmezse) veya "fred" — verinin hangi
                  API'den çekileceğini belirler. BLS serileri src/bls_client.py,
                  FRED serileri src/fred_client.py üzerinden çekilir.

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

    # ---------------- ADP National Employment Report (FRED üzerinden) ----------------
    # ADP, BLS'ten bağımsız, özel sektör bordro verisine dayanan kendi raporunu
    # yayınlar. Resmi bir hükümet API'si yok, ama FRED bu veriyi de barındırıyor.
    "ADPMNUSNERSA": {
        "name": "ADP Toplam Özel Sektör İstihdamı",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDMANNERSA": {
        "name": "ADP - İmalat Sanayi",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDCONNERSA": {
        "name": "ADP - İnşaat",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDPROBUSNERSA": {
        "name": "ADP - Profesyonel ve İş Hizmetleri",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDEDHLTNERSA": {
        "name": "ADP - Eğitim ve Sağlık Hizmetleri",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDINFONERSA": {
        "name": "ADP - Bilgi Sektörü",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDLSHPNERSA": {
        "name": "ADP - Boş Zaman ve Konaklama",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
    },

    # ---------------- ADP - İşletme büyüklüğüne göre kırılım ----------------
    # Bu kırılım sadece ADP'de var, BLS'te karşılığı yok — ADP'nin kendi
    # müşteri bordrolarından geldiği için işletme büyüklüğüne göre de
    # ayrıştırabiliyor.
    "ADPMES1T19ENERSA": {
        "name": "ADP - Küçük İşletme (1-19 çalışan)",
        "category": "ADP - İşletme Büyüklüğü",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMES20T49ENERSA": {
        "name": "ADP - Küçük İşletme (20-49 çalışan)",
        "category": "ADP - İşletme Büyüklüğü",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMES50T249ENERSA": {
        "name": "ADP - Orta Ölçekli İşletme (50-249 çalışan)",
        "category": "ADP - İşletme Büyüklüğü",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMES250T499ENERSA": {
        "name": "ADP - Orta Ölçekli İşletme (250-499 çalışan)",
        "category": "ADP - İşletme Büyüklüğü",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMES500PENERSA": {
        "name": "ADP - Büyük İşletme (500+ çalışan)",
        "category": "ADP - İşletme Büyüklüğü",
        "units": "thousands",
        "source": "fred",
    },
}


def get_series_ids(source: str = None):
    """source=None -> tüm seriler. source='bls' ya da 'fred' -> sadece o kaynağa ait seriler."""
    if source is None:
        return list(SERIES_CATALOG.keys())
    return [
        sid for sid, meta in SERIES_CATALOG.items()
        if meta.get("source", "bls") == source
    ]


def get_by_category(category: str):
    return {
        sid: meta
        for sid, meta in SERIES_CATALOG.items()
        if meta["category"] == category
    }


def get_categories():
    return sorted({meta["category"] for meta in SERIES_CATALOG.values()})

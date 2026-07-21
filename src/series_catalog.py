"""
İstihdam veri kataloğu.

Her giriş şu bilgileri taşır:
    series_id   : Kaynağın kendi seri kodu (BLS için BLS kodu, FRED için FRED kodu)
    name        : Panelde gösterilecek okunabilir isim
    category    : "Headline" | "Industry" | "Demographic" | "ADP" |
                  "ADP - İşletme Büyüklüğü" | "JOLTS" | "JOLTS - Sektörel" | "NSA (Ham Veri)"
    units       : "percent" | "thousands" | "index" gibi birim bilgisi
    source      : "bls" (varsayılan, belirtilmezse) veya "fred" — verinin hangi
                  API'den çekileceğini belirler. BLS serileri src/bls_client.py,
                  FRED serileri src/fred_client.py üzerinden çekilir.
    nsa_pair    : (opsiyonel) Bu serinin mevsimsel düzeltilmemiş (NSA) karşılığının
                  series_id'si. Sadece mevsimsel düzeltmeli (SA) serilerde bulunur;
                  "Mevsimsellik Karşılaştırması" bölümü bu eşlemeyi kullanır.

NOT: BLS zaman zaman seri kodlarını günceller / emekliye ayırır.
Bir seri artık veri döndürmüyorsa https://data.bls.gov/cgi-bin/surveymost
adresinden güncel kodu kontrol edip bu dosyayı düzenleyebilirsiniz.
Katalog tamamen bu dosya üzerinden genişletilebilir; yeni bir satır eklemek
yeterlidir, kodun başka hiçbir yerini değiştirmenize gerek yoktur.

BLS NSA (ham/düzeltilmemiş) karşılığı: "CES" önekini "CEU" ile değiştirmek
yeterlidir, geri kalan kod aynı kalır (örn. CES3000000001 -> CEU3000000001).
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
        "nsa_pair": "CEU0000000001",
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
        "nsa_pair": "CEU1000000001",
    },
    "CES2000000001": {
        "name": "İnşaat",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU2000000001",
    },
    "CES3000000001": {
        "name": "İmalat Sanayi",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU3000000001",
    },
    "CES4000000001": {
        "name": "Ticaret, Ulaştırma ve Kamu Hizmetleri",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU4000000001",
    },
    "CES5000000001": {
        "name": "Bilgi Sektörü",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU5000000001",
    },
    "CES5500000001": {
        "name": "Finansal Faaliyetler",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU5500000001",
    },
    "CES6000000001": {
        "name": "Profesyonel ve İş Hizmetleri",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU6000000001",
    },
    "CES6500000001": {
        "name": "Eğitim ve Sağlık Hizmetleri",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU6500000001",
    },
    "CES7000000001": {
        "name": "Boş Zaman ve Konaklama",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU7000000001",
    },
    "CES8000000001": {
        "name": "Diğer Hizmetler",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU8000000001",
    },
    "CES9000000001": {
        "name": "Kamu Sektörü",
        "category": "Industry",
        "units": "thousands",
        "nsa_pair": "CEU9000000001",
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
        "nsa_pair": "ADPMNUSNERNSA",
    },
    "ADPMINDMANNERSA": {
        "name": "ADP - İmalat Sanayi",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDMANNERNSA",
    },
    "ADPMINDCONNERSA": {
        "name": "ADP - İnşaat",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDCONNERNSA",
    },
    "ADPMINDPROBUSNERSA": {
        "name": "ADP - Profesyonel ve İş Hizmetleri",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDPROBUSNERNSA",
    },
    "ADPMINDEDHLTNERSA": {
        "name": "ADP - Eğitim ve Sağlık Hizmetleri",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDEDHLTNERNSA",
    },
    "ADPMINDINFONERSA": {
        "name": "ADP - Bilgi Sektörü",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDINFONERNSA",
    },
    "ADPMINDLSHPNERSA": {
        "name": "ADP - Boş Zaman ve Konaklama",
        "category": "ADP",
        "units": "thousands",
        "source": "fred",
        "nsa_pair": "ADPMINDLSHPNERNSA",
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

    # ---------------- JOLTS (Job Openings and Labor Turnover Survey) ----------------
    # BLS'in ayrı bir anketi; işgücü talebi ve devir hızını ölçer. Tamamen BLS
    # API'sinden geldiği için ekstra bir istemciye gerek yoktur.
    "JTS000000000000000JOL": {
        "name": "İş İlanları (Job Openings)",
        "category": "JOLTS",
        "units": "thousands",
    },
    "JTS000000000000000HIL": {
        "name": "İşe Alımlar (Hires)",
        "category": "JOLTS",
        "units": "thousands",
    },
    "JTS000000000000000TSL": {
        "name": "Toplam Ayrılmalar (Total Separations)",
        "category": "JOLTS",
        "units": "thousands",
    },
    "JTS000000000000000QUL": {
        "name": "Gönüllü İşten Ayrılmalar (Quits)",
        "category": "JOLTS",
        "units": "thousands",
    },
    "JTS000000000000000LDL": {
        "name": "İşten Çıkarmalar (Layoffs & Discharges)",
        "category": "JOLTS",
        "units": "thousands",
    },
    "JTS000000000000000OSL": {
        "name": "Diğer Ayrılmalar (Other Separations)",
        "category": "JOLTS",
        "units": "thousands",
    },

}

# ---------------- JOLTS - Sektörel Kırılım ----------------
# JOLTS seri ID yapısı 21 karakterdir (BLS'in resmi jt.txt tanım dosyasından
# doğrulanmıştır: https://download.bls.gov/pub/time.series/jt/jt.txt):
#   "JT" + seasonal(1: S/U) + industry_code(6) + state_code(2,00) +
#   area_code(5,00000) + sizeclass_code(2,00) + dataelement_code(2) + ratelevel(1: L/R)
# Sektör kodları BLS'in resmi jt.industry eşleme dosyasından alınmıştır
# (https://download.bls.gov/pub/time.series/jt/jt.industry).
JOLTS_INDUSTRIES = {
    "100000": "Toplam Özel Sektör",
    "110099": "Madencilik ve Ormancılık",
    "230000": "İnşaat",
    "300000": "İmalat Sanayi (Toplam)",
    "320000": "Dayanıklı Mal İmalatı",
    "340000": "Dayanıksız Mal İmalatı",
    "400000": "Ticaret, Ulaştırma ve Kamu Hizmetleri (Toplam)",
    "420000": "Toptan Ticaret",
    "440000": "Perakende Ticaret",
    "480099": "Ulaştırma, Depolama ve Kamu Hizmetleri",
    "510000": "Bilgi Sektörü",
    "510099": "Finansal Faaliyetler (Toplam)",
    "520000": "Finans ve Sigortacılık",
    "530000": "Gayrimenkul ve Kiralama",
    "540099": "Profesyonel ve İş Hizmetleri",
    "600000": "Özel Eğitim ve Sağlık Hizmetleri (Toplam)",
    "610000": "Özel Eğitim Hizmetleri",
    "620000": "Sağlık Hizmetleri ve Sosyal Yardım",
    "700000": "Boş Zaman ve Konaklama (Toplam)",
    "710000": "Sanat, Eğlence ve Rekreasyon",
    "720000": "Konaklama ve Yiyecek Hizmetleri",
    "810000": "Diğer Hizmetler",
    "900000": "Kamu Sektörü (Toplam)",
    "910000": "Federal Hükümet",
    "920000": "Eyalet ve Yerel Yönetim (Toplam)",
    "923000": "Eyalet ve Yerel Yönetim - Eğitim",
    "929000": "Eyalet ve Yerel Yönetim - Eğitim Hariç",
}

JOLTS_ELEMENTS = {
    "JO": "İş İlanları",
    "HI": "İşe Alımlar",
    "QU": "Gönüllü Ayrılmalar",
    "LD": "İşten Çıkarmalar",
    "OS": "Diğer Ayrılmalar",
    "TS": "Toplam Ayrılmalar",
}

for _industry_code, _industry_name in JOLTS_INDUSTRIES.items():
    for _elem_code, _elem_name in JOLTS_ELEMENTS.items():
        # Tam 21 karakterlik seri ID: JT + S + industry(6) + 00 + 00000 + 00 + elem(2) + L
        _sid = "JT" + "S" + _industry_code + "00" + "00000" + "00" + _elem_code + "L"
        SERIES_CATALOG[_sid] = {
            "name": f"{_elem_name} - {_industry_name}",
            "category": "JOLTS - Sektörel",
            "units": "thousands",
            "jolts_metric": _elem_code,
            "jolts_industry": _industry_name,
        }

SERIES_CATALOG.update({    # ---------------- NSA (Ham / Mevsimsel Düzeltilmemiş Veri) ----------------
    # Bu seriler ayrı kart olarak öne çıkmaz; "Mevsimsellik Karşılaştırması"
    # bölümünde yukarıdaki SA (mevsimsel düzeltmeli) serilerin karşılığı
    # olarak kullanılır (nsa_pair alanı üzerinden eşlenir).
    "CEU0000000001": {
        "name": "Toplam Tarım Dışı İstihdam (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU1000000001": {
        "name": "Madencilik ve Ormancılık (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU2000000001": {
        "name": "İnşaat (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU3000000001": {
        "name": "İmalat Sanayi (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU4000000001": {
        "name": "Ticaret, Ulaştırma ve Kamu Hizmetleri (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU5000000001": {
        "name": "Bilgi Sektörü (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU5500000001": {
        "name": "Finansal Faaliyetler (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU6000000001": {
        "name": "Profesyonel ve İş Hizmetleri (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU6500000001": {
        "name": "Eğitim ve Sağlık Hizmetleri (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU7000000001": {
        "name": "Boş Zaman ve Konaklama (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU8000000001": {
        "name": "Diğer Hizmetler (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "CEU9000000001": {
        "name": "Kamu Sektörü (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
    },
    "ADPMNUSNERNSA": {
        "name": "ADP Toplam Özel Sektör İstihdamı (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDMANNERNSA": {
        "name": "ADP - İmalat Sanayi (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDCONNERNSA": {
        "name": "ADP - İnşaat (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDPROBUSNERNSA": {
        "name": "ADP - Profesyonel ve İş Hizmetleri (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDEDHLTNERNSA": {
        "name": "ADP - Eğitim ve Sağlık Hizmetleri (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDINFONERNSA": {
        "name": "ADP - Bilgi Sektörü (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
    "ADPMINDLSHPNERNSA": {
        "name": "ADP - Boş Zaman ve Konaklama (Ham)",
        "category": "NSA (Ham Veri)",
        "units": "thousands",
        "source": "fred",
    },
})


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
    """Ana panelde (Genel Bakış) gösterilecek kategoriler. JOLTS ve NSA ham veri
    kategorileri hariç tutulur — JOLTS kendi ayrı sayfasında, NSA ise sadece
    'Mevsimsellik Karşılaştırması' bölümünde arka planda kullanılır."""
    excluded = {"NSA (Ham Veri)", "JOLTS", "JOLTS - Sektörel"}
    return sorted(
        {
            meta["category"]
            for meta in SERIES_CATALOG.values()
            if meta["category"] not in excluded
        }
    )

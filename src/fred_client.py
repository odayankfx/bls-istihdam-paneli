"""
FRED / ALFRED API istemcisi.

FRED (Federal Reserve Economic Data), BLS verilerinin "vintage" (yayınlandığı
andaki ilk hali + sonraki tüm revizyonları) kopyalarını da tutar — buna ALFRED
(Archival FRED) deniyor. BLS'in kendi API'si sadece EN SON revize edilmiş
değeri verdiği için, geçmişe dönük revizyon geçmişi (örn. "Ocak ayı verisi
ilk açıklandığında X'ti, sonra Y'ye revize edildi") için FRED'in iki farklı
"output_type" değerini karşılaştırıyoruz:

    output_type=4  -> "Initial Release Only": her dönem için SADECE ilk
                      açıklanan (revize edilmemiş) değer.
    output_type=1  -> "Observations by Real-Time Period" (varsayılan): o an
                      bilinen EN GÜNCEL (son revize) değer.

ÖNEMLİ: units="chg" parametresiyle FRED'den SEVİYE (level, örn. 158,736,000
kişi) değil, doğrudan AYLIK DEĞİŞİM (örn. "+115,000" gibi BLS'in manşette
verdiği rakam) çekiyoruz. Bunun sebebi: seviye üzerinden ilk/güncel farkı
almak, önceki ayların da revize olması yüzünden yanıltıcı bir "kümülatif
sürüklenme" verir (örn. Şubat'ın seviyesi revize olunca Nisan'ın seviyesi de
otomatik kayar). Değişim (chg) üzerinden çalışmak, doğrudan BLS'in
"X ay Y bin kişi revize edildi" şeklindeki resmi anlatımıyla eşleşir.

Not: Buradaki "ilk açıklanan vs güncel" karşılaştırması, o ayın İLK YAYIN
tarihinden BUGÜNE KADAR biriken TOPLAM revizyonu gösterir — BLS'in her ay
haber bültenlerinde verdiği "bir önceki rapora göre X bin revize edildi"
(yani sadece SON revizyon adımı) ile birebir aynı sayı olmayabilir. Belirli
bir ayın tüm revizyon adımlarını (her yayın tarihindeki değeriyle) görmek
için sayfadaki "Belirli bir ayın tüm revizyon geçmişini gör" bölümünü kullanın.

Ücretsiz API anahtarı: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import requests

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Bizim BLS seri ID'lerimizin FRED karşılıkları.
# Sadece revizyon/vintage takibi yapılacak seriler için eşleme gerekir.
FRED_SERIES_MAP = {
    "CES0000000001": "PAYEMS",  # Toplam Tarım Dışı İstihdam (mevsimsel düzeltmeli)
}


def _fetch_observations(
    fred_series_id: str,
    api_key: str,
    output_type: int,
    start_date: str,
    realtime_start: str = None,
    realtime_end: str = None,
):
    params = {
        "series_id": fred_series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "output_type": output_type,
        "units": "chg",  # SEVİYE değil, AYLIK DEĞİŞİM (BLS'in manşet rakamı)
    }
    # "İlk açıklanan" (output_type=4) sorgusu, hangi tarihlerde ilk açıklamalar
    # yapıldığını bulmak için TÜM geçmişi taraması gerekir. Varsayılan
    # realtime_start/realtime_end sadece "bugünü" kapsadığından (tek günlük
    # pencere), geçmişteki ilk açıklama tarihlerini bulamayıp 400 hatası verir.
    # Bu yüzden bu durumda geniş bir aralık belirtiyoruz.
    if realtime_start:
        params["realtime_start"] = realtime_start
    if realtime_end:
        params["realtime_end"] = realtime_end

    response = requests.get(FRED_BASE_URL, params=params, timeout=60)
    if response.status_code != 200:
        # FRED, hatanın gerçek sebebini gövdede (body) döndürür; onu görünür kılıyoruz.
        raise RuntimeError(
            f"FRED API hata döndürdü (HTTP {response.status_code}): {response.text[:500]}"
        )
    data = response.json()

    if "observations" not in data:
        raise RuntimeError(f"FRED API beklenmeyen yanıt döndürdü: {data}")

    results = []
    for obs in data["observations"]:
        value = obs.get("value")
        if value in (".", None, ""):
            continue
        results.append(
            {
                "ref_date": obs["date"],
                "realtime_start": obs.get("realtime_start", obs["date"]),
                "value": float(value),
            }
        )
    return results


def fetch_vintage_observations(fred_series_id: str, api_key: str, start_date: str = "2000-01-01"):
    """
    Belirtilen FRED serisi için "ilk açıklanan" ve "güncel" değerleri çekip
    tek bir listede döner (her dönem için 2 kayıt: ilk + güncel).

    Dönüş: [ {ref_date, realtime_start, value}, ... ]
        ref_date       -> verinin ait olduğu dönem (örn. "2024-01-01")
        realtime_start -> bu değerin bu haliyle geçerli olduğu tarih
        value          -> o andaki değer
    """
    # "İlk açıklanan" için geniş bir realtime aralığı gerekir (bkz. yukarıdaki not).
    initial = _fetch_observations(
        fred_series_id,
        api_key,
        output_type=4,
        start_date=start_date,
        realtime_start="1900-01-01",
        realtime_end="9999-12-31",
    )
    # "Güncel" (en son revize) değer için varsayılan davranış (bugünün penceresi) doğrudur.
    current = _fetch_observations(fred_series_id, api_key, output_type=1, start_date=start_date)
    return initial + current

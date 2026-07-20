"""
FRED / ALFRED API istemcisi.

FRED (Federal Reserve Economic Data), BLS verilerinin "vintage" (yayınlandığı
andaki ilk hali + sonraki tüm revizyonları) kopyalarını da tutar — buna ALFRED
(Archival FRED) deniyor. BLS'in kendi API'si sadece EN SON revize edilmiş
değeri verdiği için, geçmişe dönük revizyon geçmişi (örn. "Ocak ayı verisi
ilk açıklandığında X'ti, sonra Y'ye revize edildi") için iki farklı değer
hesaplıyoruz:

    "İlk açıklanan değişim"  -> o ayın İLK YAYINLANDIĞI GÜNDE, BLS'in resmen
                                açıkladığı değişim. Bunu doğru hesaplamak için
                                sadece o ayın kendi ilk seviyesini değil, bir
                                önceki ayın da TAM O YAYIN GÜNÜNDE nasıl
                                bilindiğini (belki zaten bir kez revize
                                edilmiş halini) ayrıca sorguluyoruz — yoksa
                                iki farklı vintage'ı karıştırıp yanlış bir
                                fark hesaplanır. Bu yüzden her ay için 1 ekstra
                                FRED sorgusu yapılıyor (hıza karşı doğruluk).
    "Güncel değişim"         -> FRED'den doğrudan units=chg ile çekilen,
                                o an bilinen EN GÜNCEL aylık değişim.

Performans için "ilk açıklanan değişim" hesaplaması sadece son ~3 yılla
sınırlı tutulur (PRECISE_YEARS); daha eski aylar için bu hesap atlanır.

Ücretsiz API anahtarı: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import time
import requests
from datetime import date

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Bizim BLS seri ID'lerimizin FRED karşılıkları.
# Sadece revizyon/vintage takibi yapılacak seriler için eşleme gerekir.
FRED_SERIES_MAP = {
    "CES0000000001": "PAYEMS",  # Toplam Tarım Dışı İstihdam (mevsimsel düzeltmeli)
}

# "İlk açıklanan değişim"in tam (vintage-eşleşmeli) hesaplandığı geçmiş yıl sayısı.
# Her ay için 1 ekstra FRED sorgusu gerektirdiğinden makul bir sınırda tutulur.
PRECISE_YEARS = 3

REQUEST_DELAY_SECONDS = 0.3


def _fetch_observations(
    fred_series_id: str,
    api_key: str,
    output_type: int,
    start_date: str,
    units: str = "lin",
    end_date: str = None,
    realtime_start: str = None,
    realtime_end: str = None,
):
    params = {
        "series_id": fred_series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "output_type": output_type,
        "units": units,
    }
    if end_date:
        params["observation_end"] = end_date
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


def _one_month_earlier(date_str: str) -> str:
    y, m, d = (int(x) for x in date_str.split("-"))
    if m == 1:
        y, m = y - 1, 12
    else:
        m -= 1
    return f"{y:04d}-{m:02d}-01"


def fetch_vintage_observations(fred_series_id: str, api_key: str, start_date: str = "2000-01-01"):
    """
    Belirtilen FRED serisi için "ilk açıklanan değişim" ve "güncel değişim"
    değerlerini çekip tek bir listede döner (her dönem için 2 kayıt).

    Dönüş: [ {ref_date, realtime_start, value}, ... ]
        ref_date       -> verinin ait olduğu dönem (örn. "2024-01-01")
        realtime_start -> bu değerin bu haliyle geçerli olduğu tarih
        value          -> o andaki AYLIK DEĞİŞİM (bin kişi)
    """
    # "İlk açıklanan değişim" hesaplamasını son PRECISE_YEARS yılla sınırlıyoruz
    # (her ay için 1 ekstra sorgu gerektirdiğinden).
    precise_cutoff = date.today().replace(year=date.today().year - PRECISE_YEARS).isoformat()
    precise_start = max(start_date, precise_cutoff)
    extended_start = _one_month_earlier(precise_start)

    # 1) Bu aralıktaki her ayın kendi ilk açıklanan SEVİYESİ + yayın tarihi.
    #    (output_type=4 sadece units=lin destekliyor.)
    initial_levels = _fetch_observations(
        fred_series_id,
        api_key,
        output_type=4,
        units="lin",
        start_date=extended_start,
        realtime_start="1900-01-01",
        realtime_end="9999-12-31",
    )
    initial_levels.sort(key=lambda r: r["ref_date"])
    # extended_start'tan itibaren gelen ilk ay sadece "bir önceki ay" referansı
    # için var, kendisi için değişim hesaplamıyoruz (precise_start'tan başlıyoruz).
    initial_levels_by_date = {r["ref_date"]: r for r in initial_levels}

    initial_changes = []
    for row in initial_levels:
        if row["ref_date"] < precise_start:
            continue
        prev_date = _one_month_earlier(row["ref_date"])
        release_date = row["realtime_start"]

        # Bir önceki ayın, TAM BU YAYIN GÜNÜNDE (release_date) bilinen değerini
        # ayrıca sorguluyoruz — bu, doğru vintage eşleşmesi için gerekli.
        try:
            prev_at_release = _fetch_observations(
                fred_series_id,
                api_key,
                output_type=1,
                units="lin",
                start_date=prev_date,
                end_date=prev_date,
                realtime_start=release_date,
                realtime_end=release_date,
            )
        except RuntimeError:
            prev_at_release = []
        time.sleep(REQUEST_DELAY_SECONDS)

        if not prev_at_release:
            # Bu ay için tam eşleşme bulunamadıysa (örn. çok eski/kenar durum),
            # kaba yaklaşım olarak ayın kendi ilk seviyesine geri düşüyoruz.
            prev_row = initial_levels_by_date.get(prev_date)
            if prev_row is None:
                continue
            prev_value = prev_row["value"]
        else:
            prev_value = prev_at_release[0]["value"]

        initial_changes.append(
            {
                "ref_date": row["ref_date"],
                "realtime_start": release_date,
                "value": row["value"] - prev_value,
            }
        )

    # 2) Güncel DEĞİŞİM: FRED'den doğrudan units=chg ile (output_type=1 bunu destekliyor).
    current_changes = _fetch_observations(
        fred_series_id, api_key, output_type=1, units="chg", start_date=start_date
    )

    return initial_changes + current_changes

"""
FRED / ALFRED API istemcisi.

FRED (Federal Reserve Economic Data), BLS verilerinin "vintage" (yayınlandığı
andaki ilk hali + sonraki tüm revizyonları) kopyalarını da tutar — buna ALFRED
(Archival FRED) deniyor. BLS'in kendi API'si sadece EN SON revize edilmiş
değeri verdiği için, geçmişe dönük revizyon geçmişi (örn. "Ocak ayı verisi
ilk açıklandığında X'ti, sonra Y'ye revize edildi") için iki farklı değer
hesaplıyoruz:

    "İlk açıklanan değişim"  -> o ayın İLK YAYINLANAN seviyesi ile bir önceki
                                ayın YİNE KENDİ İLK YAYINLANAN seviyesi
                                arasındaki fark. (FRED'in output_type=4
                                "Initial Release Only" modu SADECE units=lin
                                (seviye) ile çalışıyor, units=chg (değişim)
                                ile ÇALIŞMIYOR — bu yüzden değişimi kendimiz,
                                iki ardışık ayın seviyesinden hesaplıyoruz.)
    "Güncel değişim"         -> FRED'den doğrudan units=chg ile çekilen,
                                o an bilinen EN GÜNCEL aylık değişim.

Not: "İlk açıklanan değişim" hesabında küçük bir yaklaşıklık var: bir önceki
ayın da KENDİ ilk yayınından bu yana (genelde tek bir revizyon adımı kadar)
küçük bir revize olmuş olabilir. Bu, tüm geçmiş boyunca biriken revizyonu
karıştırmaktan çok daha isabetlidir, ama BLS'in o ay için verdiği "X bin
revize edildi" manşet rakamıyla milimetrik olarak örtüşmeyebilir.

Ücretsiz API anahtarı: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import requests
from datetime import date, timedelta

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
    units: str = "lin",
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
    # Bir önceki ayı da hesaba katabilmek için 1 ay geriden başlıyoruz.
    extended_start = _one_month_earlier(start_date)

    # 1) İlk açıklanan SEVİYELER (output_type=4 sadece units=lin destekliyor).
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

    # Ardışık aylardan "ilk açıklanan değişim"i kendimiz hesaplıyoruz.
    initial_changes = []
    for i in range(1, len(initial_levels)):
        prev_row = initial_levels[i - 1]
        curr_row = initial_levels[i]
        initial_changes.append(
            {
                "ref_date": curr_row["ref_date"],
                "realtime_start": curr_row["realtime_start"],
                "value": curr_row["value"] - prev_row["value"],
            }
        )

    # 2) Güncel DEĞİŞİM: FRED'den doğrudan units=chg ile (output_type=1 bunu destekliyor).
    current_changes = _fetch_observations(
        fred_series_id, api_key, output_type=1, units="chg", start_date=start_date
    )

    return initial_changes + current_changes

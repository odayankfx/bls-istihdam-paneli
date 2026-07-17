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

Bu ikisini karşılaştırarak "ilk açıklanan vs güncel" farkını hesaplıyoruz.
(Not: Daha önce kullanılan output_type=2 "tüm vintage" modu, bazı serilerde
beklenmedik bir JSON yapısı döndürdüğü için bu yönteme geçildi.)

Ücretsiz API anahtarı: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import requests

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Bizim BLS seri ID'lerimizin FRED karşılıkları.
# Sadece revizyon/vintage takibi yapılacak seriler için eşleme gerekir.
FRED_SERIES_MAP = {
    "CES0000000001": "PAYEMS",  # Toplam Tarım Dışı İstihdam (mevsimsel düzeltmeli)
}


def _fetch_observations(fred_series_id: str, api_key: str, output_type: int, start_date: str):
    params = {
        "series_id": fred_series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "output_type": output_type,
    }
    response = requests.get(FRED_BASE_URL, params=params, timeout=60)
    response.raise_for_status()
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
    initial = _fetch_observations(fred_series_id, api_key, output_type=4, start_date=start_date)
    current = _fetch_observations(fred_series_id, api_key, output_type=1, start_date=start_date)
    return initial + current

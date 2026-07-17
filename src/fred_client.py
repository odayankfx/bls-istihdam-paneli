"""
FRED / ALFRED API istemcisi.

FRED (Federal Reserve Economic Data), BLS verilerinin "vintage" (yayınlandığı
andaki ilk hali + sonraki tüm revizyonları) kopyalarını da tutar — buna ALFRED
(Archival FRED) deniyor. BLS'in kendi API'si sadece EN SON revize edilmiş
değeri verdiği için, geçmişe dönük revizyon geçmişi (örn. "Ocak ayı verisi
ilk açıklandığında X'ti, sonra Y'ye revize edildi") için FRED'in
"output_type=2" (vintage bazlı, tüm gözlemler) özelliğini kullanıyoruz.

Ücretsiz API anahtarı: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import requests

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Bizim BLS seri ID'lerimizin FRED karşılıkları.
# Sadece revizyon/vintage takibi yapılacak seriler için eşleme gerekir.
FRED_SERIES_MAP = {
    "CES0000000001": "PAYEMS",  # Toplam Tarım Dışı İstihdam (mevsimsel düzeltmeli)
}


def fetch_vintage_observations(fred_series_id: str, api_key: str, start_date: str = "2000-01-01"):
    """
    Belirtilen FRED serisi için TÜM vintage (revizyon) geçmişini çeker.

    Dönüş: [ {ref_date, realtime_start, value}, ... ]
        ref_date       -> verinin ait olduğu dönem (örn. "2024-01-01")
        realtime_start -> bu değerin bu haliyle ilk kez yayınlandığı tarih
        value          -> o vintage'daki değer
    """
    params = {
        "series_id": fred_series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "realtime_start": "1900-01-01",
        "realtime_end": "9999-12-31",
        "output_type": 2,  # vintage bazlı, tüm gözlemler (tüm revizyonlar dahil)
    }
    response = requests.get(FRED_BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    if "observations" not in data:
        raise RuntimeError(f"FRED API beklenmeyen yanıt döndürdü: {data}")

    results = []
    for obs in data["observations"]:
        if obs["value"] in (".", None, ""):
            continue
        results.append(
            {
                "ref_date": obs["date"],
                "realtime_start": obs["realtime_start"],
                "value": float(obs["value"]),
            }
        )
    return results

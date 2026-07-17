"""
BLS Public Data API v2 istemcisi.

BLS API kısıtları (kayıtlı API anahtarı ile):
    - İstek başına en fazla 50 seri
    - İstek başına en fazla 20 yıllık aralık
    - Günde en fazla 500 istek

Bu modül bu limitleri otomatik olarak yönetir: seri listesini 50'lik
gruplara, yıl aralığını da 20 yıllık parçalara böler.

API anahtarı olmadan da (kayıtsız) çalışır ama limitler çok daha düşüktür
(günde 25 istek, istek başına 25 seri, 10 yıllık aralık). Ücretsiz anahtar
için: https://data.bls.gov/registrationEngine/
"""

import time
import json
import requests

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

MAX_SERIES_PER_REQUEST = 50
MAX_YEARS_PER_REQUEST = 20
REQUEST_DELAY_SECONDS = 1.0  # BLS sunucusuna nazik davranmak için


def _chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _year_chunks(start_year: int, end_year: int, span: int):
    y = start_year
    while y <= end_year:
        y_end = min(y + span - 1, end_year)
        yield y, y_end
        y = y_end + 1


def fetch_series(series_ids, start_year, end_year, api_key=None):
    """
    Verilen seri ID listesi için start_year-end_year aralığındaki veriyi çeker.

    Dönüş: {series_id: [ {year, period, periodName, value, footnotes}, ... ]}
    """
    all_results = {sid: [] for sid in series_ids}

    for id_chunk in _chunk(series_ids, MAX_SERIES_PER_REQUEST):
        for y_start, y_end in _year_chunks(start_year, end_year, MAX_YEARS_PER_REQUEST):
            payload = {
                "seriesid": id_chunk,
                "startyear": str(y_start),
                "endyear": str(y_end),
            }
            if api_key:
                payload["registrationkey"] = api_key

            response = requests.post(
                BLS_API_URL,
                data=json.dumps(payload),
                headers={"Content-type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "REQUEST_SUCCEEDED":
                messages = data.get("message", [])
                raise RuntimeError(
                    f"BLS API isteği başarısız oldu: {messages}"
                )

            for series in data["Results"]["series"]:
                sid = series["seriesID"]
                for point in series["data"]:
                    all_results[sid].append(
                        {
                            "year": int(point["year"]),
                            "period": point["period"],
                            "periodName": point["periodName"],
                            "value": point["value"],
                            "footnotes": ";".join(
                                f.get("text", "")
                                for f in point.get("footnotes", [])
                                if f.get("text")
                            ),
                        }
                    )

            time.sleep(REQUEST_DELAY_SECONDS)

    return all_results

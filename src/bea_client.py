"""
BEA (Bureau of Economic Analysis) API istemcisi.

FRED, BEA'nın sadece "ana" aylık PCE tablolarını (Mal/Hizmet/Dayanıklı/
Dayanıksız/Gıda/Enerji) yansıtır — Konut, Sağlık, Ulaştırma, Eğlence gibi
daha ayrıntılı alt kalemler FRED'de YOKTUR. Bu ayrıntılı kalemler sadece
BEA'nın kendi "Underlying Detail Tables" (Ayrıntılı Alt Tablolar) setinde,
NIUnderlyingDetail veri kümesinde bulunur — bu yüzden bu kalemler için
BEA'nın kendi API'sine doğrudan bağlanıyoruz.

Ücretsiz API anahtarı: https://apps.bea.gov/API/signup/index.cfm

API dokümantasyonu: https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf

ÖNEMLİ NOT: Aşağıdaki TABLE_NAME ("U20404") BEA'nın NIPA tablo numaralandırma
kuralına (Ayrıntılı Alt Tablo = "U" + ana tablo numarasının rakamları, örn.
Tablo 2.4.4 "Price Indexes for PCE by Type of Product" -> "U20404") dayanarak
belirlenmiştir. Bu isimlendirme BEA'nın resmi tablo listesinden %100 teyit
edilememiştir — ilk çalıştırmada hata alınırsa, BEA API'sinin
GetParameterValues (ParameterName=TableName) çağrısıyla doğru tablo adı
bulunup burada güncellenmelidir.
"""

import requests

BEA_API_URL = "https://apps.bea.gov/api/data"

# Tablo 2.4.4 (Price Indexes for PCE by Type of Product) — Ayrıntılı Alt Tablo
TABLE_NAME = "U20404"


def fetch_underlying_detail_series(api_key: str, series_codes: list, start_year: int, table_name: str = TABLE_NAME):
    """
    BEA'nın NIUnderlyingDetail veri kümesinden, verilen tabloyu TEK SEFERDE
    çekip, sadece istenen series_codes'a ait aylık verileri filtreleyip
    döner.

    Dönüş: {series_code: [ {year, period, periodName, value, footnotes}, ... ]}
           (BLS/FRED ile aynı ortak format — database.upsert_series_points
           doğrudan kullanabilir.)
    """
    params = {
        "UserID": api_key,
        "method": "GetData",
        "DatasetName": "NIUnderlyingDetail",
        "TableName": table_name,
        "Frequency": "M",
        "Year": "ALL",
        "ResultFormat": "JSON",
    }
    response = requests.get(BEA_API_URL, params=params, timeout=90)
    if response.status_code != 200:
        raise RuntimeError(
            f"BEA API hata döndürdü (HTTP {response.status_code}): {response.text[:500]}"
        )

    data = response.json()
    beaapi = data.get("BEAAPI", {})
    results = beaapi.get("Results", {})

    # BEA bazen HTTP 200 ile birlikte içeride bir "Error" düğümü döner.
    if isinstance(results, dict) and "Error" in results:
        raise RuntimeError(f"BEA API hata döndürdü: {results['Error']}")

    rows = results.get("Data") if isinstance(results, dict) else None
    if not rows:
        raise RuntimeError(f"BEA API'den beklenen veri gelmedi: {str(data)[:500]}")

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]

    series_set = set(series_codes)
    out = {code: [] for code in series_codes}

    for row in rows:
        code = row.get("SeriesCode")
        if code not in series_set:
            continue
        time_period = row.get("TimePeriod", "")
        if "M" not in time_period:
            continue  # yıllık/çeyreklik satırları atla, sadece aylık istiyoruz
        try:
            year_str, month_str = time_period.split("M")
            year = int(year_str)
            month = int(month_str)
        except (ValueError, IndexError):
            continue
        if year < start_year:
            continue
        value_str = str(row.get("DataValue", "")).replace(",", "")
        try:
            value = float(value_str)
        except ValueError:
            continue
        out[code].append(
            {
                "year": year,
                "period": f"M{month:02d}",
                "periodName": month_names[month - 1],
                "value": str(value),
                "footnotes": "",
            }
        )

    return out

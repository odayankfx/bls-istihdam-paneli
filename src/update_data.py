"""
Veriyi BLS API'sinden çekip yerel SQLite veritabanına yazan script.

Kullanım:
    python -m src.update_data                 # son 10 yılı çeker
    python -m src.update_data --years 20       # son 20 yılı çeker
    python -m src.update_data --start 2010 --end 2025

Ortam değişkenleri (.env dosyasından okunur):
    BLS_API_KEY   : (opsiyonel ama önerilir) BLS kayıt anahtarı
    FRED_API_KEY  : (opsiyonel ama önerilir) FRED/ALFRED anahtarı — revizyon geçmişi için
    DB_PATH       : (opsiyonel) SQLite dosya yolu, varsayılan data/employment.db

BLS'in Employment Situation raporu her ayın ilk cuma günü yayınlanır;
bu script'i haftada bir (örn. cron ile) çalıştırmak güncel kalmak için yeterlidir.
"""

import argparse
import datetime
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.series_catalog import SERIES_CATALOG, get_series_ids
from src.bls_client import fetch_series
from src.fred_client import fetch_vintage_observations, FRED_SERIES_MAP
from src import database


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="BLS istihdam verisini güncelle")
    parser.add_argument("--years", type=int, default=10, help="Kaç yıl geriye gidilsin")
    parser.add_argument("--start", type=int, default=None, help="Başlangıç yılı (opsiyonel)")
    parser.add_argument("--end", type=int, default=None, help="Bitiş yılı (opsiyonel)")
    parser.add_argument(
        "--skip-revisions",
        action="store_true",
        help="FRED/ALFRED'den revizyon geçmişi çekmeyi atla (daha hızlı, ama revizyon grafiği eksik kalır)",
    )
    args = parser.parse_args()

    current_year = datetime.date.today().year
    end_year = args.end or current_year
    start_year = args.start or (end_year - args.years + 1)

    api_key = os.environ.get("BLS_API_KEY")
    if not api_key:
        print(
            "[UYARI] BLS_API_KEY bulunamadı. Kayıtsız modda devam ediliyor "
            "(çok daha düşük günlük limit). .env dosyasına anahtar eklemeniz önerilir."
        )

    database.init_db()

    series_ids = get_series_ids()
    print(f"{len(series_ids)} seri, {start_year}-{end_year} yılları için çekiliyor...")

    results = fetch_series(series_ids, start_year, end_year, api_key=api_key)

    for series_id, points in results.items():
        meta = SERIES_CATALOG[series_id]
        database.upsert_series_meta(
            series_id, meta["name"], meta["category"], meta["units"]
        )
        if points:
            database.upsert_series_points(series_id, points)
            # Bu anda BLS'in gördüğü değerleri kendi revizyon geçmişimize de
            # "snapshot" olarak kaydediyoruz (FRED karşılığı olmayan seriler için).
            # ÖNEMLİ: FRED eşlemesi olan seriler için BUNU ATLIYORUZ, çünkü BLS'in
            # verdiği ham değer SEVİYE (level), FRED'den çektiğimiz ise AYLIK
            # DEĞİŞİM (units=chg) — ikisini aynı tabloda karıştırmak revizyon
            # hesaplamasını bozar.
            if series_id not in FRED_SERIES_MAP:
                database.snapshot_current_as_revision(series_id, points)
            print(f"  ✓ {series_id} ({meta['name']}): {len(points)} veri noktası")
        else:
            print(f"  ! {series_id} ({meta['name']}): veri dönmedi")

    # ---------------- FRED/ALFRED üzerinden gerçek revizyon geçmişi ----------------
    if not args.skip_revisions:
        fred_api_key = os.environ.get("FRED_API_KEY")
        if not fred_api_key:
            print(
                "[UYARI] FRED_API_KEY bulunamadı, ALFRED revizyon geçmişi atlanıyor. "
                "Ücretsiz anahtar: https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        else:
            for bls_id, fred_id in FRED_SERIES_MAP.items():
                if bls_id not in SERIES_CATALOG:
                    continue
                print(f"FRED/ALFRED'den revizyon geçmişi çekiliyor: {fred_id} ({bls_id})")
                try:
                    vintage_rows = fetch_vintage_observations(
                        fred_id, fred_api_key, start_date=f"{start_year}-01-01"
                    )
                    database.upsert_revisions(bls_id, vintage_rows, source="alfred")
                    print(f"  ✓ {len(vintage_rows)} vintage kaydı yazıldı")
                except Exception as exc:
                    print(f"  ! FRED/ALFRED çekimi başarısız: {exc}")

    print("Tamamlandı. Veritabanı:", database.get_db_path())


if __name__ == "__main__":
    main()

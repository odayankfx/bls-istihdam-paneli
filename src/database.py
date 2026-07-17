"""
SQLite veri katmanı.

Veritabanı dosyası tek bir .db dosyasıdır -> farklı bilgisayarlar arasında
taşımak için bu dosyayı (data/employment.db) git ile commit edebilir ya da
Dropbox/OneDrive gibi senkronize bir klasöre koyup DB_PATH ortam değişkeniyle
gösterebilirsiniz. Bkz. README.md "Taşınabilirlik" bölümü.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "employment.db"
)


def get_db_path():
    return os.environ.get("DB_PATH", DEFAULT_DB_PATH)


@contextmanager
def get_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS series_meta (
                series_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                units TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS series_data (
                series_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                period TEXT NOT NULL,
                period_name TEXT,
                value REAL,
                footnotes TEXT,
                fetched_at TEXT,
                PRIMARY KEY (series_id, year, period)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_series_data_sid ON series_data(series_id)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS revisions (
                series_id TEXT NOT NULL,
                ref_date TEXT NOT NULL,
                realtime_start TEXT NOT NULL,
                value REAL,
                source TEXT NOT NULL,
                PRIMARY KEY (series_id, ref_date, realtime_start)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_revisions_sid_ref ON revisions(series_id, ref_date)"
        )
        conn.commit()


def upsert_series_meta(series_id: str, name: str, category: str, units: str):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO series_meta (series_id, name, category, units)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(series_id) DO UPDATE SET
                name=excluded.name,
                category=excluded.category,
                units=excluded.units
            """,
            (series_id, name, category, units),
        )
        conn.commit()


def upsert_series_points(series_id: str, points: list):
    fetched_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO series_data (series_id, year, period, period_name, value, footnotes, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(series_id, year, period) DO UPDATE SET
                period_name=excluded.period_name,
                value=excluded.value,
                footnotes=excluded.footnotes,
                fetched_at=excluded.fetched_at
            """,
            [
                (
                    series_id,
                    p["year"],
                    p["period"],
                    p["periodName"],
                    _safe_float(p["value"]),
                    p["footnotes"],
                    fetched_at,
                )
                for p in points
            ],
        )
        conn.commit()


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_all_meta():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM series_meta").fetchall()
        return [dict(r) for r in rows]


def get_series_dataframe(series_id: str):
    import pandas as pd

    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT year, period, period_name, value, footnotes, fetched_at
            FROM series_data
            WHERE series_id = ? AND period != 'M13'
            ORDER BY year ASC,
                     CAST(SUBSTR(period, 2) AS INTEGER) ASC
            """,
            conn,
            params=(series_id,),
        )
    if df.empty:
        return df
    df["month"] = df["period"].str.replace("M", "").astype(int)
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
    )
    return df


def upsert_revisions(series_id: str, rows: list, source: str):
    """rows: [{"ref_date": "2024-01-01", "realtime_start": "2024-02-02", "value": 123.4}, ...]"""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO revisions (series_id, ref_date, realtime_start, value, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(series_id, ref_date, realtime_start) DO UPDATE SET
                value=excluded.value,
                source=excluded.source
            """,
            [
                (series_id, r["ref_date"], r["realtime_start"], r["value"], source)
                for r in rows
            ],
        )
        conn.commit()


def snapshot_current_as_revision(series_id: str, points: list):
    """
    update_data.py her çalıştığında, o anki (BLS'in en güncel gördüğü) değerleri
    'source=snapshot' olarak revisions tablosuna da yazar. Böylece FRED/ALFRED
    karşılığı olmayan seriler için de zamanla kendi revizyon geçmişimiz oluşur.
    Aynı gün içinde tekrar çalıştırılırsa üzerine yazar (aynı gün = tek kayıt).
    """
    today = datetime.now(timezone.utc).date().isoformat()
    rows = []
    for p in points:
        month = p["period"].replace("M", "")
        if not month.isdigit() or p["period"] == "M13":
            continue
        ref_date = f"{p['year']}-{int(month):02d}-01"
        value = _safe_float(p["value"])
        if value is not None:
            rows.append({"ref_date": ref_date, "realtime_start": today, "value": value})
    if rows:
        upsert_revisions(series_id, rows, source="snapshot")


def get_revision_history(series_id: str, ref_date: str):
    """Belirli bir dönem (ref_date) için tüm vintage kayıtlarını, tarih sırasıyla döner."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT realtime_start, value, source
            FROM revisions
            WHERE series_id = ? AND ref_date = ?
            ORDER BY realtime_start ASC
            """,
            (series_id, ref_date),
        ).fetchall()
        return [dict(r) for r in rows]


def get_initial_vs_latest(series_id: str, n_periods: int = 12):
    """
    Son n_periods ay için ilk açıklanan (en erken realtime_start) değer ile
    en güncel (en son realtime_start) değeri karşılaştıran bir tablo döner.
    """
    import pandas as pd

    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT ref_date, realtime_start, value
            FROM revisions
            WHERE series_id = ?
            ORDER BY ref_date ASC, realtime_start ASC
            """,
            conn,
            params=(series_id,),
        )
    if df.empty:
        return df

    grouped = df.groupby("ref_date")
    result = grouped.agg(
        ilk_aciklanan=("value", "first"),
        son_revize=("value", "last"),
        revizyon_sayisi=("value", "count"),
    ).reset_index()
    result["fark"] = result["son_revize"] - result["ilk_aciklanan"]
    result["ref_date"] = pd.to_datetime(result["ref_date"])
    result = result.sort_values("ref_date").tail(n_periods)
    return result


def get_last_update_time():
    with get_connection() as conn:
        row = conn.execute("SELECT MAX(fetched_at) FROM series_data").fetchone()
        return row[0] if row else None

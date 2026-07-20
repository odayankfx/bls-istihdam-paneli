"""
Aylık rapor tabloları ve trend göstergeleri için yardımcı fonksiyonlar.

Bu modül hem "Genel Bakış" hem "Tarım Dışı İstihdam Detay" sayfalarında
kullanılan ortak hesaplamaları barındırır: MoM/YoY değişim tablosu, birden
çok seriyi yan yana gösteren geniş tablo, ve "son dönemin trend hızı ortalamaya
göre nasıl" göstergesi.
"""

import pandas as pd


def build_compact_report_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tek bir seri için: Dönem, Değer, Aylık Değişim, Aylık Değişim %,
    Yıllık Değişim, Yıllık Değişim % kolonlarını içeren tablo.

    df: get_series_dataframe() çıktısı (date, value kolonları olmalı)
    """
    if df.empty:
        return df

    out = df[["date", "value"]].sort_values("date").reset_index(drop=True).copy()
    out["Aylık Değişim"] = out["value"].diff()
    out["Aylık Değişim %"] = out["value"].pct_change() * 100
    out["Yıllık Değişim"] = out["value"].diff(12)
    out["Yıllık Değişim %"] = out["value"].pct_change(12) * 100

    out = out.rename(columns={"date": "Dönem", "value": "Değer"})
    out["Dönem"] = out["Dönem"].dt.strftime("%Y-%m")
    return out.sort_values("Dönem", ascending=False).reset_index(drop=True)


def build_wide_report_table(series_data: dict, value_type: str = "change") -> pd.DataFrame:
    """
    Birden çok seriyi (örn. tüm sektörler) yan yana, her ay bir satır olacak
    şekilde birleştiren "geniş" tablo.

    series_data : {seri_adı: dataframe} sözlüğü (her df'de date, value olmalı)
    value_type  : "change" -> aylık değişim gösterilir
                  "level"  -> ham seviye değeri gösterilir
                  "yoy_pct"-> yıllık % değişim gösterilir
    """
    frames = []
    for name, df in series_data.items():
        if df.empty:
            continue
        temp = df[["date", "value"]].sort_values("date").reset_index(drop=True).copy()
        if value_type == "change":
            temp["gösterilen"] = temp["value"].diff()
        elif value_type == "yoy_pct":
            temp["gösterilen"] = temp["value"].pct_change(12) * 100
        else:
            temp["gösterilen"] = temp["value"]
        temp = temp[["date", "gösterilen"]].rename(columns={"gösterilen": name})
        temp = temp.set_index("date")
        frames.append(temp)

    if not frames:
        return pd.DataFrame()

    wide = pd.concat(frames, axis=1, join="outer").sort_index(ascending=False)
    wide.index = wide.index.strftime("%Y-%m")
    wide.index.name = "Dönem"
    return wide.reset_index()


def compute_trend_indicator(df: pd.DataFrame, short_window: int = 3, long_window: int = 12):
    """
    Son short_window ayın ortalama aylık değişimini, son long_window ayın
    ortalama aylık değişimiyle karşılaştırır.

    Dönüş: dict {
        "recent_avg": float,   # son short_window ay ortalama değişim
        "baseline_avg": float, # son long_window ay ortalama değişim
        "direction": "up" | "down" | "flat" | None,
        "diff": float,         # recent_avg - baseline_avg
    }
    Yeterli veri yoksa direction=None döner.
    """
    if df.empty or len(df) < long_window + 1:
        return {"recent_avg": None, "baseline_avg": None, "direction": None, "diff": None}

    df_sorted = df.sort_values("date").reset_index(drop=True)
    changes = df_sorted["value"].diff().dropna()

    if len(changes) < long_window:
        return {"recent_avg": None, "baseline_avg": None, "direction": None, "diff": None}

    recent_avg = changes.tail(short_window).mean()
    baseline_avg = changes.tail(long_window).mean()
    diff = recent_avg - baseline_avg

    # Anlamlı bir fark için baseline'ın belirli bir yüzdesini eşik olarak kullanıyoruz
    threshold = max(abs(baseline_avg) * 0.15, 1.0)
    if diff > threshold:
        direction = "up"
    elif diff < -threshold:
        direction = "down"
    else:
        direction = "flat"

    return {
        "recent_avg": recent_avg,
        "baseline_avg": baseline_avg,
        "direction": direction,
        "diff": diff,
    }


TREND_LABELS = {
    "up": ("📈", "Trend üzerinde (hızlanıyor)"),
    "down": ("📉", "Trend altında (yavaşlıyor)"),
    "flat": ("➡️", "Trende yakın"),
    None: ("", ""),
}

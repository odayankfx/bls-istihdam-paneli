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


def build_breakdown_bar_for_date(ref_date, headline_name: str, headline_df: pd.DataFrame, breakdown_dict: dict):
    """
    Belirli bir ay (ref_date) için: başlık göstergesinin (örn. Toplam Tarım Dışı
    İstihdam) o aydaki aylık değişimini, her bir alt kategorinin (örn. sektörler)
    aynı aydaki değişimiyle yan yana karşılaştıran bir bar grafik verisi üretir.

    Dönüş: DataFrame (Kategori, Değişim, TipGrubu) — TipGrubu "Başlık" ya da
    "Alt Kategori" olur, grafikte renklendirme için kullanılır. Veri yoksa
    boş DataFrame döner.
    """
    ref_date = pd.to_datetime(ref_date)
    rows = []

    h = headline_df.sort_values("date").reset_index(drop=True).copy()
    h["change"] = h["value"].diff()
    match = h[h["date"] == ref_date]
    if not match.empty and pd.notna(match.iloc[0]["change"]):
        rows.append({"Kategori": headline_name, "Değişim": match.iloc[0]["change"], "TipGrubu": "Başlık"})

    for name, df in breakdown_dict.items():
        if df.empty:
            continue
        d = df.sort_values("date").reset_index(drop=True).copy()
        d["change"] = d["value"].diff()
        m = d[d["date"] == ref_date]
        if not m.empty and pd.notna(m.iloc[0]["change"]):
            rows.append({"Kategori": name, "Değişim": m.iloc[0]["change"], "TipGrubu": "Alt Kategori"})

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def build_pct_change_lines(breakdown_dict: dict, pct_type: str = "yoy"):
    """
    Birden çok alt kategori serisinin % değişim (aylık ya da yıllık) zaman
    serisini tek bir grafik verisi olarak döner (uzun format DataFrame:
    date, Kategori, Değişim %).

    pct_type: "yoy" -> 12 aylık % değişim, "mom" -> aylık % değişim
    """
    periods = 12 if pct_type == "yoy" else 1
    frames = []
    for name, df in breakdown_dict.items():
        if df.empty:
            continue
        d = df.sort_values("date").reset_index(drop=True).copy()
        d["Değişim %"] = d["value"].pct_change(periods) * 100
        d["Kategori"] = name
        frames.append(d[["date", "Kategori", "Değişim %"]])
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

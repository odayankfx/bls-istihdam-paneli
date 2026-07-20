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


def render_pct_change_chart(df_long: pd.DataFrame, key_prefix: str, vline_date=None):
    """
    Bir % değişim çizgi grafiğini, üstünde tarih aralığı seçici ve y ekseni
    (ızgara aralığı) kontrolleriyle birlikte render eder.

    Neden gerekli: bazı alt kategorilerde (örn. küçük bir sektörde) tek bir ay
    aşırı yüksek/düşük bir % değişim gösterebilir; bu durum y eksenini o tek
    uç değere göre ölçekleyip diğer tüm çizgileri düz bir çizgiye sıkıştırır.
    Varsayılan olarak eksen aralığını uç değerleri dışlayan bir persentil
    bandına (5-95) göre ayarlıyoruz; kullanıcı isterse elle genişletebilir.

    df_long   : date, Kategori, Değişim % kolonlarını içeren uzun format DataFrame
                (build_pct_change_lines çıktısı)
    key_prefix: Streamlit widget key çakışmalarını önlemek için benzersiz önek
    vline_date: (opsiyonel) grafikte dikey referans çizgisi çizilecek tarih
    """
    import streamlit as st
    import plotly.express as px

    if df_long.empty:
        st.info("Bu görünüm için veri yok.")
        return

    min_date = df_long["date"].min().date()
    max_date = df_long["date"].max().date()

    date_range = st.slider(
        "Tarih aralığı",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MM/YYYY",
        key=f"{key_prefix}_daterange",
    )

    filtered = df_long[
        (df_long["date"].dt.date >= date_range[0]) & (df_long["date"].dt.date <= date_range[1])
    ]

    if filtered.empty:
        st.info("Seçilen tarih aralığında veri yok.")
        return

    values = filtered["Değişim %"].dropna()
    if values.empty:
        st.info("Seçilen tarih aralığında veri yok.")
        return

    # Varsayılan y ekseni aralığı: uç değerleri dışlayan 5-95 persentil bandı + biraz pay.
    p_low, p_high = values.quantile(0.05), values.quantile(0.95)
    pad = max((p_high - p_low) * 0.2, 0.5)
    default_min = round(float(p_low - pad), 1)
    default_max = round(float(p_high + pad), 1)
    data_min = round(float(values.min()), 1)
    data_max = round(float(values.max()), 1)

    auto_scale = st.checkbox(
        "Tüm uç değerleri göster (otomatik ölçekle)",
        value=False,
        key=f"{key_prefix}_autoscale",
        help="İşaretlerseniz eksen, en uçtaki değere göre otomatik ayarlanır — "
             "bu, aşırı bir uç değer varsa diğer çizgileri düzleştirebilir.",
    )

    y_range = None
    if auto_scale:
        y_range = [data_min - abs(data_min) * 0.05 - 0.5, data_max + abs(data_max) * 0.05 + 0.5]
    else:
        col1, col2 = st.columns(2)
        with col1:
            y_min = st.number_input(
                "Y ekseni min (%)", value=default_min, step=0.5, key=f"{key_prefix}_ymin"
            )
        with col2:
            y_max = st.number_input(
                "Y ekseni max (%)", value=default_max, step=0.5, key=f"{key_prefix}_ymax"
            )
        y_range = [y_min, y_max]
        if data_min < y_min or data_max > y_max:
            st.caption(
                f"ℹ️ Veri aralığı ({data_min:+.1f}% / {data_max:+.1f}%) seçtiğiniz eksen sınırlarının "
                "dışına taşıyor olabilir — grafik dışı kalan noktalar kesilir. "
                "'Tüm uç değerleri göster' kutusunu işaretleyerek hepsini görebilirsiniz."
            )

    fig = px.line(
        filtered, x="date", y="Değişim %", color="Kategori",
        labels={"date": "Tarih", "Değişim %": "Değişim %"},
    )
    if vline_date is not None:
        vline_ts = pd.to_datetime(vline_date)
        if filtered["date"].min() <= vline_ts <= filtered["date"].max():
            fig.add_vline(x=vline_ts, line_dash="dot", line_color="gray")
    fig.update_yaxes(range=y_range)
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

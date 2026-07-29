"""
PCE Fiyat Endeksi — Genel Bakış

BEA'nın (Bureau of Economic Analysis) Kişisel Tüketim Harcamaları Fiyat
Endeksi'ni (PCE) gösterir: başlık göstergeleri (Tüm Kalemler, Çekirdek PCE,
Enerji, Gıda, Hizmetler...) ve mal/hizmet alt kategorileri (Dayanıklı/
Dayanıksız Mallar).

ÖNEMLİ: PCE, Fed'in (FOMC) %2 enflasyon hedeflemesinde ESAS ALDIĞI ölçüttür —
CPI değil. Fed'in konuşmalarında/kararlarında referans verilen "enflasyon",
genellikle Çekirdek PCE'dir.

PCE bir SEVİYE değil bir ENDEKS (2017=100 taban yıllı) olduğundan, mutlak
değer karşılaştırması yerine odak HER ZAMAN % değişim (aylık ve yıllık
enflasyon oranı) üzerindedir. Veri BEA'dan gelir ama BEA'nın kendi API'si
yerine (ADP'de olduğu gibi) FRED üzerinden çekilir.
"""

import os
import sys
import subprocess

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import database, report_utils
from src.pce_catalog import get_categories, get_by_category

database.init_db()


@st.cache_data(ttl=300)
def load_series(series_id: str) -> pd.DataFrame:
    return database.get_series_dataframe(series_id)


def latest_index_and_changes(df: pd.DataFrame):
    """PCE endeksi için: son değer, aylık % değişim, yıllık % değişim."""
    if df.empty or len(df) < 13:
        if df.empty or len(df) < 2:
            return None, None, None
        df_sorted = df.sort_values("date")
        latest = df_sorted.iloc[-1]
        prev = df_sorted.iloc[-2]
        mom_pct = (latest["value"] / prev["value"] - 1) * 100
        return latest, mom_pct, None
    df_sorted = df.sort_values("date")
    latest = df_sorted.iloc[-1]
    prev = df_sorted.iloc[-2]
    yoy_row = df_sorted[df_sorted["date"] == latest["date"] - pd.DateOffset(years=1)]
    mom_pct = (latest["value"] / prev["value"] - 1) * 100
    yoy_pct = (
        (latest["value"] / yoy_row.iloc[0]["value"] - 1) * 100 if not yoy_row.empty else None
    )
    return latest, mom_pct, yoy_pct


# ---------------------------------------------------------------- kenar çubuğu
st.sidebar.title("💰 Kontrol Paneli")

last_update = database.get_last_update_time()
if last_update:
    st.sidebar.caption(f"Son veri güncellemesi: {last_update[:19].replace('T', ' ')} UTC")
else:
    st.sidebar.warning(
        "Veritabanı boş görünüyor. Önce şunu çalıştırın:\n\n"
        "`python -m src.update_data`"
    )

if st.sidebar.button("🔄 Veriyi şimdi güncelle"):
    with st.spinner("BLS API'sinden veri çekiliyor..."):
        child_env = os.environ.copy()
        try:
            if "BLS_API_KEY" in st.secrets:
                child_env["BLS_API_KEY"] = st.secrets["BLS_API_KEY"]
            if "FRED_API_KEY" in st.secrets:
                child_env["FRED_API_KEY"] = st.secrets["FRED_API_KEY"]
        except Exception:
            pass

        result = subprocess.run(
            [sys.executable, "-m", "src.update_data"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            env=child_env,
        )
    if result.returncode == 0:
        st.sidebar.success("Güncelleme tamamlandı.")
        st.cache_data.clear()
    else:
        st.sidebar.error("Güncelleme başarısız oldu, detay için terminali kontrol edin.")
        st.sidebar.code(result.stderr[-2000:])

category = st.sidebar.radio("Kategori", get_categories())

# ---------------------------------------------------------------- ana başlık
st.title("💰 PCE Fiyat Endeksi — Genel Bakış")
st.caption("Kaynak: U.S. Bureau of Economic Analysis (BEA) — Personal Consumption Expenditures Price Index, FRED üzerinden")

series_in_category = get_by_category(category)

if not series_in_category:
    st.info("Bu kategoride seri bulunmuyor.")
    st.stop()

card_data = {sid: load_series(sid) for sid in series_in_category}

# ---------------------------------------------------------------- özet kartlar
st.subheader(f"{category} — Güncel PCE Oranları")
cols = st.columns(min(3, len(series_in_category)))
for i, (sid, meta) in enumerate(series_in_category.items()):
    df = card_data[sid]
    latest, mom_pct, yoy_pct = latest_index_and_changes(df)
    col = cols[i % len(cols)]
    with col:
        if latest is not None and yoy_pct is not None:
            st.metric(
                label=meta["name"],
                value=f"{yoy_pct:+.1f}% (yıllık)",
                delta=f"{mom_pct:+.2f}% (aylık)" if mom_pct is not None else None,
                help=f"Endeks değeri: {latest['value']:.2f} (2017=100)",
            )
            trend = report_utils.compute_trend_indicator(df)
            icon, label = report_utils.TREND_LABELS[trend["direction"]]
            if trend["direction"] is not None:
                st.caption(f"{icon} {label}")
        elif latest is not None:
            st.metric(label=meta["name"], value=f"Endeks: {latest['value']:.2f}", help="Yıllık % değişim için 12+ ay veri gerekiyor.")
        else:
            st.metric(label=meta["name"], value="Veri yok")

st.divider()

# ---------------------------------------------------------------- pce bar grafiği (ay seçilebilir)
st.subheader("PCE Oranları Karşılaştırması (Ay Seçilebilir)")
st.caption(
    "Her kalemin seçtiğiniz aydaki % değişimini yan yana gösterir. "
    "Aşağıdan istediğiniz ayı ve yıllık/aylık görünümü seçebilirsiniz."
)

bar_metric = st.radio(
    "Gösterilecek değişim türü",
    ["Yıllık % Değişim", "Aylık % Değişim"],
    horizontal=True,
    key=f"pce_bar_metric_{category}",
)
bar_pct_type = "yoy" if bar_metric == "Yıllık % Değişim" else "mom"

named_for_bar = {meta["name"]: card_data[sid] for sid, meta in series_in_category.items()}
bar_lines_all = report_utils.build_pct_change_lines(named_for_bar, pct_type=bar_pct_type)

if bar_lines_all.empty:
    st.info("Bu kategori için % değişim hesaplanacak yeterli veri yok.")
else:
    available_months = sorted(bar_lines_all["date"].dropna().unique())
    selected_month = st.select_slider(
        "Ay seçin",
        options=available_months,
        value=available_months[-1],
        format_func=lambda d: pd.Timestamp(d).strftime("%B %Y"),
        key=f"pce_bar_month_{category}",
    )

    month_df = bar_lines_all[bar_lines_all["date"] == selected_month].dropna(subset=["Değişim %"])

    if month_df.empty:
        st.info("Seçilen ay için veri yok (bu kalem için yeterli geçmiş veri birikmemiş olabilir).")
    else:
        month_df = month_df.sort_values("Değişim %")
        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                x=month_df["Değişim %"],
                y=month_df["Kategori"],
                orientation="h",
                marker_color=["#d62728" if v >= 0 else "#2ca02c" for v in month_df["Değişim %"]],
                text=month_df["Değişim %"].map(lambda v: f"{v:+.1f}%"),
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            title=f"{category} — {pd.Timestamp(selected_month).strftime('%B %Y')} {bar_metric}",
            height=max(300, 40 * len(month_df)),
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis_title=bar_metric,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Not: PCE'de kırmızı=artış, yeşil=düşüş renklendirmesi kullanılmıştır (istihdam grafiklerinin tersi).")

st.divider()

# ---------------------------------------------------------------- zaman serisi grafiği (endeks + % değişim)
st.subheader("Zaman Serisi Karşılaştırması")

view_mode = st.radio(
    "Gösterim",
    ["Yıllık % Değişim (PCE Oranı)", "Aylık % Değişim", "Ham Endeks Değeri"],
    horizontal=True,
    key="pce_ts_view_mode",
)

selected_series = st.multiselect(
    "Grafikte gösterilecek kalemleri seçin",
    options=list(series_in_category.keys()),
    default=list(series_in_category.keys())[:4],
    format_func=lambda sid: series_in_category[sid]["name"],
)

if selected_series:
    if view_mode == "Ham Endeks Değeri":
        selected_dfs = [card_data.get(sid) for sid in selected_series]
        ts_start, ts_end = report_utils.date_range_slider(selected_dfs, key=f"pce_ts_daterange_{category}")
        fig = go.Figure()
        for sid in selected_series:
            df = card_data.get(sid)
            if df is None or df.empty:
                continue
            mask = (df["date"].dt.date >= ts_start) & (df["date"].dt.date <= ts_end)
            df_f = df[mask]
            fig.add_trace(go.Scatter(x=df_f["date"], y=df_f["value"], mode="lines", name=series_in_category[sid]["name"]))
        fig.update_layout(
            title=f"{category} — Endeks Değeri",
            height=480,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        pct_type = "yoy" if view_mode.startswith("Yıllık") else "mom"
        named = {series_in_category[sid]["name"]: card_data[sid] for sid in selected_series}
        lines = report_utils.build_pct_change_lines(named, pct_type=pct_type)
        report_utils.render_pct_change_chart(
            lines, key_prefix=f"pce_ts_{category}_{pct_type}",
            title=f"{category} — {view_mode}",
        )
else:
    st.info("Karşılaştırmak için en az bir kalem seçin.")

st.divider()

# ---------------------------------------------------------------- aylık rapor tablosu
st.subheader("📅 Aylık Rapor Tablosu")

table_view = st.radio(
    "Görünüm",
    ["Tekli kalem (detaylı)", "Kalemler yan yana (geniş tablo)"],
    horizontal=True,
    key="pce_table_view",
)

if table_view == "Tekli kalem (detaylı)":
    single_sid = st.selectbox(
        "Kalem seçin",
        options=list(series_in_category.keys()),
        format_func=lambda sid: series_in_category[sid]["name"],
        key="pce_report_single",
    )
    df = card_data.get(single_sid)
    compact = report_utils.build_compact_report_table(df)
    if compact.empty:
        st.info("Bu kalem için veri yok.")
    else:
        # PCE'de "Değer" bir endeks (2-3 ondalık anlamlı), Aylık/Yıllık Değişim (index puan
        # cinsinden) ikinci planda — asıl önemli olan % değişim kolonlarıdır.
        st.dataframe(
            compact.style.format(
                {
                    "Değer": "{:.3f}",
                    "Aylık Değişim": "{:+.3f}",
                    "Aylık Değişim %": "{:+.2f}%",
                    "Yıllık Değişim": "{:+.3f}",
                    "Yıllık Değişim %": "{:+.2f}%",
                },
                na_rep="—",
            ),
            use_container_width=True,
            height=400,
        )
        st.download_button(
            "CSV olarak indir",
            data=compact.to_csv(index=False).encode("utf-8"),
            file_name=f"{single_sid}_pce_aylik_rapor.csv",
            mime="text/csv",
            key="download_pce_compact",
        )
else:
    value_type_label = st.radio(
        "Gösterilecek değer",
        ["Yıllık % Değişim", "Aylık % Değişim", "Ham Endeks Değeri"],
        horizontal=True,
        key="pce_wide_value_type",
    )
    value_type_map = {
        "Yıllık % Değişim": "yoy_pct",
        "Aylık % Değişim": "change",  # aşağıda özel işlenecek
        "Ham Endeks Değeri": "level",
    }
    named = {meta["name"]: card_data[sid] for sid, meta in series_in_category.items()}

    if value_type_label == "Aylık % Değişim":
        # build_wide_report_table'ın "change" modu MUTLAK fark verir; PCE için
        # % değişim istiyoruz, bu yüzden burada kendimiz hesaplıyoruz.
        frames = []
        for name, df in named.items():
            if df.empty:
                continue
            temp = df[["date", "value"]].sort_values("date").reset_index(drop=True).copy()
            temp["gösterilen"] = temp["value"].pct_change() * 100
            temp = temp[["date", "gösterilen"]].rename(columns={"gösterilen": name}).set_index("date")
            frames.append(temp)
        if frames:
            wide = pd.concat(frames, axis=1, join="outer").sort_index(ascending=False)
            wide.index = wide.index.strftime("%Y-%m")
            wide.index.name = "Dönem"
            wide = wide.reset_index()
        else:
            wide = pd.DataFrame()
    else:
        wide = report_utils.build_wide_report_table(named, value_type=value_type_map[value_type_label])

    if wide.empty:
        st.info("Bu kategoride veri yok.")
    else:
        fmt = "{:+.2f}%" if value_type_label != "Ham Endeks Değeri" else "{:.2f}"
        st.dataframe(wide.style.format(fmt, subset=wide.columns[1:], na_rep="—"), use_container_width=True, height=400)
        st.download_button(
            "CSV olarak indir",
            data=wide.to_csv(index=False).encode("utf-8"),
            file_name=f"pce_{category.lower()}_genis_tablo.csv",
            mime="text/csv",
            key="download_pce_wide",
        )

st.divider()

# ---------------------------------------------------------------- mevsimsellik karşılaştırması
nsa_capable = {sid: meta for sid, meta in series_in_category.items() if "nsa_pair" in meta}

if nsa_capable:
    st.subheader("🌊 Mevsimsellik Karşılaştırması (Mevsimsel Düzeltmeli vs Ham Veri)")
    st.caption(
        "Mevsimsel düzeltmeli (SA) endeks, her yıl tekrar eden fiyat dalgalanmalarını "
        "(örn. yaz aylarında benzin/seyahat fiyatlarındaki mevsimsel artış) arındırır. "
        "Ham (NSA) endeks bu dalgalanmaları olduğu gibi gösterir."
    )

    nsa_sid = st.selectbox(
        "Kalem seçin",
        options=list(nsa_capable.keys()),
        format_func=lambda sid: nsa_capable[sid]["name"],
        key="pce_nsa_comparison",
    )

    sa_df = card_data.get(nsa_sid)
    nsa_series_id = nsa_capable[nsa_sid]["nsa_pair"]
    nsa_df = load_series(nsa_series_id)

    if sa_df is None or sa_df.empty or nsa_df.empty:
        st.info(
            "Ham (NSA) veri henüz çekilmemiş olabilir. `python -m src.update_data` "
            "çalıştırdığınızda otomatik olarak dahil edilir."
        )
    else:
        fig_nsa = go.Figure()
        fig_nsa.add_trace(go.Scatter(x=sa_df["date"], y=sa_df["value"], mode="lines", name="Mevsimsel Düzeltmeli (SA)"))
        fig_nsa.add_trace(go.Scatter(x=nsa_df["date"], y=nsa_df["value"], mode="lines", name="Ham Veri (NSA)", line=dict(dash="dot")))
        fig_nsa.update_layout(
            title=f"{nsa_capable[nsa_sid]['name']} — Mevsimsel Düzeltmeli vs Ham Veri",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            hovermode="x unified",
        )
        st.plotly_chart(fig_nsa, use_container_width=True)
else:
    st.caption("Bu kategoride mevsimsellik karşılaştırması için ham (NSA) veri eşlemesi tanımlı değil.")

st.divider()

# ---------------------------------------------------------------- ham veri indirme
with st.expander("📄 Ham veriyi görüntüle / indir (tüm kategori)"):
    combined = []
    for sid, meta in series_in_category.items():
        df = card_data.get(sid)
        if df is None or df.empty:
            continue
        temp = df[["date", "value"]].copy()
        temp["series"] = meta["name"]
        combined.append(temp)
    if combined:
        combined_df = pd.concat(combined).sort_values(["series", "date"])
        st.dataframe(combined_df, use_container_width=True)
        st.download_button(
            "CSV olarak indir",
            data=combined_df.to_csv(index=False).encode("utf-8"),
            file_name=f"pce_{category.lower()}_data.csv",
            mime="text/csv",
        )

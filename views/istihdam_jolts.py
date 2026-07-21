"""
JOLTS (Job Openings and Labor Turnover Survey) — Detaylı Görünüm

BLS'in ayrı bir anketi; işgücü talebini (iş ilanları) ve işgücü devir hızını
(işe alım, işten ayrılma) ölçer. Bu sayfa şunları içerir:
    1. Güncel durum kartları + trend göstergeleri
    2. Net İşe Alım (İşe Alımlar - Toplam Ayrılmalar) — net istihdam akışı
    3. Zaman serisi karşılaştırması
    4. Aylık rapor tablosu — "Toplam Ayrılmalar" seçilirse, bir tarihe tıklayınca
       bunun Gönüllü Ayrılma + İşten Çıkarma + Diğer olarak kırılımı gösterilir
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import database, report_utils
from src.series_catalog import get_by_category

database.init_db()

JOLTS_SEPARATIONS_BREAKDOWN = {
    # "Toplam Ayrılmalar" bu üç serinin toplamına eşittir.
    "JTS000000000000000QUL": "Gönüllü İşten Ayrılmalar (Quits)",
    "JTS000000000000000LDL": "İşten Çıkarmalar (Layoffs & Discharges)",
    "JTS000000000000000OSL": "Diğer Ayrılmalar (Other Separations)",
}
TOTAL_SEPARATIONS_ID = "JTS000000000000000TSL"
HIRES_ID = "JTS000000000000000HIL"


@st.cache_data(ttl=300)
def load_series(series_id: str) -> pd.DataFrame:
    return database.get_series_dataframe(series_id)


st.title("🧩 JOLTS — İş İlanları ve İşgücü Devir Hızı")
st.caption("Kaynak: BLS Job Openings and Labor Turnover Survey (JOLTS)")

jolts_series = get_by_category("JOLTS")

if not jolts_series:
    st.warning("JOLTS serileri kataloğa henüz eklenmemiş.")
    st.stop()

card_data = {sid: load_series(sid) for sid in jolts_series}

if all(df.empty for df in card_data.values()):
    st.warning(
        "Henüz veri yok. GitHub Actions üzerinden `update_data` workflow'unu "
        "çalıştırın ya da Genel Bakış sayfasındaki '🔄 Veriyi şimdi güncelle' "
        "butonunu kullanın."
    )
    st.stop()

# ============================================================== 1) Güncel durum kartları
st.subheader("Güncel Durum")


def latest_value_and_change(df: pd.DataFrame):
    if df.empty or len(df) < 2:
        return None, None
    df_sorted = df.sort_values("date")
    latest = df_sorted.iloc[-1]
    prev = df_sorted.iloc[-2]
    return latest, latest["value"] - prev["value"]


cols = st.columns(3)
for i, (sid, meta) in enumerate(jolts_series.items()):
    df = card_data[sid]
    latest, mom = latest_value_and_change(df)
    col = cols[i % 3]
    with col:
        if latest is not None:
            st.metric(
                label=meta["name"],
                value=f"{latest['value']:,.0f}K",
                delta=f"{mom:+,.0f}K (aylık)" if mom is not None else None,
            )
            trend = report_utils.compute_trend_indicator(df)
            icon, label = report_utils.TREND_LABELS[trend["direction"]]
            if trend["direction"] is not None:
                st.caption(f"{icon} {label}")
        else:
            st.metric(label=meta["name"], value="Veri yok")

st.divider()

# ============================================================== 2) Net İşe Alım
st.subheader("Net İşe Alım (İşe Alımlar − Toplam Ayrılmalar)")
st.caption(
    "Pozitifse işgücü piyasasına net istihdam ekleniyor demektir, negatifse "
    "işe alımlardan daha fazla kişi işten ayrılıyor/çıkarılıyor demektir."
)

hires_df = card_data.get(HIRES_ID)
total_sep_df = card_data.get(TOTAL_SEPARATIONS_ID)

if hires_df is not None and total_sep_df is not None and not hires_df.empty and not total_sep_df.empty:
    merged = pd.merge(
        hires_df[["date", "value"]], total_sep_df[["date", "value"]],
        on="date", suffixes=("_hires", "_sep"),
    )
    merged["net"] = merged["value_hires"] - merged["value_sep"]

    fig_net = go.Figure()
    fig_net.add_trace(
        go.Bar(
            x=merged["date"],
            y=merged["net"],
            marker_color=["#2ca02c" if v >= 0 else "#d62728" for v in merged["net"]],
        )
    )
    fig_net.add_hline(y=0, line_width=1, line_color="gray")
    fig_net.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Bin Kişi (Net)",
        xaxis_title="Ay",
    )
    st.plotly_chart(fig_net, use_container_width=True)

    last_row = merged.sort_values("date").iloc[-1]
    st.metric(
        f"{last_row['date'].strftime('%B %Y')} Net İşe Alım",
        f"{last_row['net']:+,.0f}K",
    )
else:
    st.info("Net işe alım hesaplamak için hem İşe Alımlar hem Toplam Ayrılmalar verisi gerekiyor.")

st.divider()

# ============================================================== 3) Zaman serisi karşılaştırması
st.subheader("Zaman Serisi Karşılaştırması")

selected_series = st.multiselect(
    "Grafikte gösterilecek serileri seçin",
    options=list(jolts_series.keys()),
    default=list(jolts_series.keys())[:3],
    format_func=lambda sid: jolts_series[sid]["name"],
)

if selected_series:
    fig = go.Figure()
    for sid in selected_series:
        df = card_data.get(sid)
        if df is None or df.empty:
            continue
        fig.add_trace(
            go.Scatter(x=df["date"], y=df["value"], mode="lines", name=jolts_series[sid]["name"])
        )
    fig.update_layout(
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        margin=dict(l=10, r=10, t=20, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Karşılaştırmak için en az bir seri seçin.")

st.divider()

# ============================================================== 4) Aylık rapor tablosu
st.subheader("📅 Aylık Rapor Tablosu")
st.caption(
    "'Toplam Ayrılmalar'ı seçip bir tarihe tıklarsanız, bunun Gönüllü Ayrılma + "
    "İşten Çıkarma + Diğer olarak kırılımını görebilirsiniz."
)

single_sid = st.selectbox(
    "Seri seçin",
    options=list(jolts_series.keys()),
    format_func=lambda sid: jolts_series[sid]["name"],
    key="jolts_report_series",
)

df = card_data.get(single_sid)
compact = report_utils.build_compact_report_table(df) if df is not None else pd.DataFrame()

if compact.empty:
    st.info("Bu seri için veri yok.")
else:
    select_event = st.dataframe(
        compact.style.format(
            {
                "Değer": "{:,.1f}",
                "Aylık Değişim": "{:+,.1f}",
                "Aylık Değişim %": "{:+,.2f}%",
                "Yıllık Değişim": "{:+,.1f}",
                "Yıllık Değişim %": "{:+,.2f}%",
            },
            na_rep="—",
        ),
        use_container_width=True,
        height=400,
        on_select="rerun",
        selection_mode="single-row",
        key="jolts_report_table",
    )
    st.download_button(
        "CSV olarak indir",
        data=compact.to_csv(index=False).encode("utf-8"),
        file_name=f"{single_sid}_jolts_aylik_rapor.csv",
        mime="text/csv",
    )

    selected_rows = select_event.selection.rows if select_event and select_event.selection else []

    if selected_rows and single_sid == TOTAL_SEPARATIONS_ID:
        selected_period = compact.iloc[selected_rows[0]]["Dönem"]
        selected_date = pd.to_datetime(selected_period + "-01")

        breakdown_data = {
            name: load_series(sid) for sid, name in JOLTS_SEPARATIONS_BREAKDOWN.items()
        }

        with st.container(border=True):
            st.markdown(f"### 🔎 {selected_date.strftime('%B %Y')} — Ayrılmaların Kırılımı")

            st.markdown("**1) O Ayki Değişim: Toplam vs Bileşenler**")
            bar_data = report_utils.build_breakdown_bar_for_date(
                selected_date, "Toplam Ayrılmalar", df, breakdown_data
            )
            if bar_data.empty:
                st.info("Bu ay için kırılım verisi bulunamadı.")
            else:
                bar_data = bar_data.sort_values("Değişim")
                fig_breakdown = go.Figure()
                fig_breakdown.add_trace(
                    go.Bar(
                        x=bar_data["Değişim"],
                        y=bar_data["Kategori"],
                        orientation="h",
                        marker_color=[
                            "#1f77b4" if t == "Başlık" else ("#2ca02c" if v >= 0 else "#d62728")
                            for t, v in zip(bar_data["TipGrubu"], bar_data["Değişim"])
                        ],
                        text=bar_data["Değişim"].map(lambda v: f"{v:+,.0f}K"),
                        textposition="outside",
                    )
                )
                fig_breakdown.update_layout(
                    height=max(250, 40 * len(bar_data)),
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title="Aylık Değişim (Bin Kişi)",
                )
                st.plotly_chart(fig_breakdown, use_container_width=True)

            st.markdown("**2) Bileşenlerin Yıllık % Değişimi (Zaman İçinde)**")
            yoy_lines = report_utils.build_pct_change_lines(breakdown_data, pct_type="yoy")
            report_utils.render_pct_change_chart(yoy_lines, key_prefix="jolts_yoy", vline_date=selected_date)

            st.markdown("**3) Bileşenlerin Aylık % Değişimi (Zaman İçinde)**")
            mom_lines = report_utils.build_pct_change_lines(breakdown_data, pct_type="mom")
            report_utils.render_pct_change_chart(mom_lines, key_prefix="jolts_mom", vline_date=selected_date)
    elif selected_rows and single_sid != TOTAL_SEPARATIONS_ID:
        st.caption(
            "ℹ️ Kırılım detayı sadece 'Toplam Ayrılmalar' serisi için tanımlı "
            "(Gönüllü Ayrılma + İşten Çıkarma + Diğer bileşenlerine ayrıştırılıyor)."
        )
    else:
        st.caption("👆 Detayı görmek için tablodan bir satır (tarih) seçin.")

st.divider()

# ---------------------------------------------------------------- ham veri indirme
with st.expander("📄 Ham veriyi görüntüle / indir (tüm JOLTS serileri)"):
    combined = []
    for sid, meta in jolts_series.items():
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
            file_name="jolts_data.csv",
            mime="text/csv",
        )

"""
Tarım Dışı İstihdam (Nonfarm Payroll) — Derinlemesine Analiz

Bu sayfa şunları içerir:
    1. Aylık net değişim (kaç bin kişi eklendi/çıkarıldı)
    2. Revizyonlar: ilk açıklanan değer vs en güncel (son revize) değer
    3. Kümülatif artış: kullanıcının seçtiği tarihten bugüne toplam net artış
    4. Yıllar arası karşılaştırma: farklı yılların aynı ay bazında kıyası
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import database

NONFARM_SERIES_ID = "CES0000000001"

st.set_page_config(page_title="Tarım Dışı İstihdam Detay", page_icon="📈", layout="wide")

database.init_db()

st.title("📈 Tarım Dışı İstihdam — Derinlemesine Analiz")
st.caption("Kaynak: BLS Current Employment Statistics (CES) + FRED/ALFRED (revizyon geçmişi)")


@st.cache_data(ttl=300)
def load_level_df():
    df = database.get_series_dataframe(NONFARM_SERIES_ID)
    if df.empty:
        return df
    df = df.sort_values("date").reset_index(drop=True)
    df["net_degisim"] = df["value"].diff()
    return df


@st.cache_data(ttl=300)
def load_revisions_df(n_periods=18):
    return database.get_initial_vs_latest(NONFARM_SERIES_ID, n_periods=n_periods)


level_df = load_level_df()

if level_df.empty:
    st.warning(
        "Henüz veri yok. Ana sayfadaki '🔄 Veriyi şimdi güncelle' butonunu kullanın "
        "ya da GitHub Actions üzerinden `update_data` workflow'unu çalıştırın."
    )
    st.stop()

# ============================================================== 1) Genel görünüm
st.subheader("Genel Görünüm")
latest = level_df.iloc[-1]
prev = level_df.iloc[-2]
col1, col2, col3 = st.columns(3)
col1.metric(
    "Son Ay Net Değişim",
    f"{latest['net_degisim']:+,.0f}K",
    help=f"{latest['date'].strftime('%B %Y')} verisi",
)
col2.metric("Toplam Tarım Dışı İstihdam", f"{latest['value']:,.0f}K")
col3.metric(
    "12 Aylık Ortalama Net Değişim",
    f"{level_df['net_degisim'].tail(12).mean():+,.0f}K",
)

fig_level = px.line(
    level_df, x="date", y="value", labels={"date": "Tarih", "value": "Bin Kişi"}
)
fig_level.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig_level, use_container_width=True)

st.divider()

# ============================================================== 2) Aylık net değişim
st.subheader("Aylık Net Değişim")
st.caption("Her ay bir önceki aya göre kaç bin kişilik istihdam artışı/azalışı olduğunu gösterir.")

n_months = st.slider("Kaç aylık veri gösterilsin?", 6, 60, 24, key="net_change_months")
recent = level_df.tail(n_months)

fig_bar = go.Figure()
fig_bar.add_trace(
    go.Bar(
        x=recent["date"],
        y=recent["net_degisim"],
        marker_color=["#2ca02c" if v >= 0 else "#d62728" for v in recent["net_degisim"]],
    )
)
fig_bar.update_layout(
    height=350,
    margin=dict(l=10, r=10, t=20, b=10),
    yaxis_title="Bin Kişi",
    xaxis_title="Ay",
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ============================================================== 3) Revizyonlar
st.subheader("Revizyonlar: İlk Açıklanan vs Güncel Değer")

rev_df = load_revisions_df(n_periods=18)

if rev_df.empty:
    st.info(
        "Henüz revizyon verisi yok. Bunun için `FRED_API_KEY` tanımlı olarak "
        "`python -m src.update_data` çalıştırılmalı (bkz. README → Revizyon Takibi). "
        "Anahtar tanımlıysa ve script bir kez çalıştıysa bu grafik otomatik dolacaktır."
    )
else:
    fig_rev = go.Figure()
    fig_rev.add_trace(
        go.Bar(x=rev_df["ref_date"], y=rev_df["ilk_aciklanan"], name="İlk Açıklanan")
    )
    fig_rev.add_trace(
        go.Bar(x=rev_df["ref_date"], y=rev_df["son_revize"], name="Güncel (Son Revize)")
    )
    fig_rev.update_layout(
        barmode="group",
        height=400,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Bin Kişi",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    total_rev = rev_df["fark"].sum()
    avg_rev = rev_df["fark"].mean()
    c1, c2 = st.columns(2)
    c1.metric("Toplam Revizyon Etkisi (gösterilen dönem)", f"{total_rev:+,.0f}K")
    c2.metric("Ortalama Aylık Revizyon", f"{avg_rev:+,.1f}K")

    with st.expander("📄 Revizyon detay tablosu"):
        display_df = rev_df.copy()
        display_df["ref_date"] = display_df["ref_date"].dt.strftime("%Y-%m")
        display_df.columns = [
            "Dönem", "İlk Açıklanan", "Güncel", "Revizyon Sayısı", "Fark",
        ]
        st.dataframe(display_df, use_container_width=True)

    with st.expander("🔍 Belirli bir ayın tüm revizyon geçmişini gör"):
        available_periods = sorted(level_df["date"].dt.strftime("%Y-%m-01").unique(), reverse=True)
        selected_period = st.selectbox("Dönem seçin", available_periods)
        history = database.get_revision_history(NONFARM_SERIES_ID, selected_period)
        if history:
            hist_df = pd.DataFrame(history)
            hist_df.columns = ["Yayın Tarihi", "Değer", "Kaynak"]
            st.dataframe(hist_df, use_container_width=True)
        else:
            st.caption("Bu dönem için kayıtlı revizyon geçmişi yok.")

st.divider()

# ============================================================== 4) Kümülatif artış
st.subheader("Kümülatif Artış")
st.caption("Seçtiğiniz tarihten bugüne kadar toplanan net istihdam artışı.")

min_date = level_df["date"].min().date()
max_date = level_df["date"].max().date()
default_start = level_df["date"].iloc[max(0, len(level_df) - 25)].date()

start_date = st.date_input(
    "Başlangıç tarihi",
    value=default_start,
    min_value=min_date,
    max_value=max_date,
)

cum_df = level_df[level_df["date"].dt.date >= start_date].copy()
if not cum_df.empty:
    baseline = cum_df.iloc[0]["value"]
    cum_df["kumulatif_artis"] = cum_df["value"] - baseline

    fig_cum = px.area(
        cum_df, x="date", y="kumulatif_artis",
        labels={"date": "Tarih", "kumulatif_artis": "Kümülatif Artış (Bin Kişi)"},
    )
    fig_cum.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_cum, use_container_width=True)

    st.metric(
        f"{start_date.strftime('%B %Y')}'den bugüne toplam artış",
        f"{cum_df['kumulatif_artis'].iloc[-1]:+,.0f}K",
    )
else:
    st.info("Seçilen tarih aralığında veri yok.")

st.divider()

# ============================================================== 5) Yıllar arası karşılaştırma
st.subheader("Yıllar Arası Karşılaştırma")
st.caption("Farklı yılların Ocak ayından itibaren kümülatif istihdam artışı, aynı eksende karşılaştırılır.")

level_df["yil"] = level_df["date"].dt.year
level_df["ay"] = level_df["date"].dt.month

available_years = sorted(level_df["yil"].unique(), reverse=True)
default_years = available_years[:3]

selected_years = st.multiselect(
    "Karşılaştırılacak yılları seçin",
    options=available_years,
    default=default_years,
)

if selected_years:
    fig_years = go.Figure()
    for year in sorted(selected_years):
        year_df = level_df[level_df["yil"] == year].sort_values("ay")
        if year_df.empty:
            continue
        baseline = year_df.iloc[0]["value"]
        year_df = year_df.copy()
        year_df["kumulatif"] = year_df["value"] - baseline
        fig_years.add_trace(
            go.Scatter(
                x=year_df["ay"],
                y=year_df["kumulatif"],
                mode="lines+markers",
                name=str(year),
            )
        )
    fig_years.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(
            title="Ay",
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
        ),
        yaxis_title="Ocak'tan İtibaren Kümülatif Artış (Bin Kişi)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        hovermode="x unified",
    )
    st.plotly_chart(fig_years, use_container_width=True)
else:
    st.info("Karşılaştırmak için en az bir yıl seçin.")

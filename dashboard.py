"""
ABD İstihdam Verileri Dashboard'u (BLS API + SQLite + Streamlit)

Çalıştırmak için:
    streamlit run dashboard.py
"""

import os
import sys
import subprocess

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import database
from src.series_catalog import SERIES_CATALOG, get_categories, get_by_category

st.set_page_config(
    page_title="ABD İstihdam Verileri",
    page_icon="📊",
    layout="wide",
)

database.init_db()


# ---------------------------------------------------------------- yardımcılar
@st.cache_data(ttl=300)
def load_series(series_id: str) -> pd.DataFrame:
    return database.get_series_dataframe(series_id)


def latest_value_and_change(df: pd.DataFrame):
    if df.empty or len(df) < 2:
        return None, None, None
    df_sorted = df.sort_values("date")
    latest = df_sorted.iloc[-1]
    prev = df_sorted.iloc[-2]
    yoy_row = df_sorted[df_sorted["date"] == latest["date"] - pd.DateOffset(years=1)]
    mom_change = latest["value"] - prev["value"]
    yoy_change = (
        latest["value"] - yoy_row.iloc[0]["value"] if not yoy_row.empty else None
    )
    return latest, mom_change, yoy_change


# ---------------------------------------------------------------- kenar çubuğu
st.sidebar.title("📊 Kontrol Paneli")

last_update = database.get_last_update_time()
if last_update:
    st.sidebar.caption(f"Son veri güncellemesi: {last_update[:19].replace('T', ' ')} UTC")
else:
    st.sidebar.warning(
        "Veritabanı boş görünüyor. Önce şunu çalıştırın:\n\n"
        "`python -m src.update_data`"
    )

if st.sidebar.button("🔄 Veriyi şimdi güncelle (BLS API)"):
    with st.spinner("BLS API'sinden veri çekiliyor..."):
        # BLS_API_KEY'i önce Streamlit secrets'tan, yoksa ortam değişkeninden al
        # ve alt sürece (subprocess) aktar.
        child_env = os.environ.copy()
        try:
            if "BLS_API_KEY" in st.secrets:
                child_env["BLS_API_KEY"] = st.secrets["BLS_API_KEY"]
            if "FRED_API_KEY" in st.secrets:
                child_env["FRED_API_KEY"] = st.secrets["FRED_API_KEY"]
        except Exception:
            pass  # secrets.toml tanımlı değilse sessizce geç

        result = subprocess.run(
            [sys.executable, "-m", "src.update_data"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
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

st.sidebar.caption(
    "Not: Bulut ortamında yerel dosya sistemi geçicidir — buradan yapılan "
    "manuel güncelleme sadece bu oturum için geçerlidir. Kalıcı güncellemeler "
    "GitHub Actions üzerinden haftalık otomatik yapılır ve repoya commit edilir."
)

category = st.sidebar.radio("Kırılım kategorisi", get_categories())

year_range = st.sidebar.slider(
    "Yıl aralığı",
    min_value=2000,
    max_value=pd.Timestamp.today().year,
    value=(2015, pd.Timestamp.today().year),
)

# ---------------------------------------------------------------- ana başlık
st.title("🇺🇸 ABD İstihdam Verileri Dashboard'u")
st.caption("Kaynak: U.S. Bureau of Labor Statistics (BLS) Public Data API")

series_in_category = get_by_category(category)

if not series_in_category:
    st.info("Bu kategoride seri bulunmuyor.")
    st.stop()

# ---------------------------------------------------------------- özet kartlar
st.subheader(f"{category} — Güncel Durum")
cols = st.columns(min(4, len(series_in_category)))
card_data = {}
for i, (sid, meta) in enumerate(series_in_category.items()):
    df = load_series(sid)
    card_data[sid] = df
    latest, mom, yoy = latest_value_and_change(df)
    col = cols[i % len(cols)]
    with col:
        if latest is not None:
            unit_suffix = "%" if meta["units"] == "percent" else "K"
            st.metric(
                label=meta["name"],
                value=f"{latest['value']:.1f}{unit_suffix}",
                delta=f"{mom:+.1f} (aylık)" if mom is not None else None,
            )
        else:
            st.metric(label=meta["name"], value="Veri yok")

st.divider()

# ---------------------------------------------------------------- zaman serisi grafiği
st.subheader("Zaman Serisi Karşılaştırması")

selected_series = st.multiselect(
    "Grafikte gösterilecek serileri seçin",
    options=list(series_in_category.keys()),
    default=list(series_in_category.keys())[:3],
    format_func=lambda sid: series_in_category[sid]["name"],
)

if selected_series:
    fig = go.Figure()
    for sid in selected_series:
        df = card_data.get(sid, load_series(sid))
        if df.empty:
            continue
        mask = (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])
        df_filtered = df[mask]
        fig.add_trace(
            go.Scatter(
                x=df_filtered["date"],
                y=df_filtered["value"],
                mode="lines",
                name=series_in_category[sid]["name"],
            )
        )
    fig.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Karşılaştırmak için en az bir seri seçin.")

st.divider()

# ---------------------------------------------------------------- son dönem karşılaştırma (bar)
st.subheader("Son Dönem Kırılım Karşılaştırması")

bar_rows = []
for sid, meta in series_in_category.items():
    df = card_data.get(sid, load_series(sid))
    if df.empty:
        continue
    latest = df.sort_values("date").iloc[-1]
    bar_rows.append({"Seri": meta["name"], "Değer": latest["value"], "Birim": meta["units"]})

if bar_rows:
    bar_df = pd.DataFrame(bar_rows).sort_values("Değer", ascending=True)
    fig_bar = px.bar(
        bar_df,
        x="Değer",
        y="Seri",
        orientation="h",
        text="Değer",
        color="Değer",
        color_continuous_scale="Blues",
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_bar.update_layout(height=max(300, 40 * len(bar_df)), margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ---------------------------------------------------------------- ham veri tablosu ve indirme
with st.expander("📄 Ham veriyi görüntüle / indir"):
    combined = []
    for sid, meta in series_in_category.items():
        df = card_data.get(sid, load_series(sid))
        if df.empty:
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
            file_name=f"bls_{category.lower()}_data.csv",
            mime="text/csv",
        )

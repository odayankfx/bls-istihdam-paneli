"""
ABD İstihdam Verileri — Genel Bakış (BLS + FRED/ADP + SQLite + Streamlit)

Bu, "💼 ABD İstihdam" bölümünün ana sayfasıdır. Kategori seçerek (Headline,
Industry, Demographic, ADP, ADP - İşletme Büyüklüğü) o kategorideki tüm
serileri karşılaştırmalı olarak gösterir. Ayrıca:
    - Her sektör için trend göstergesi (son 3 ay ortalaması, son 12 ay
      ortalamasının üzerinde mi altında mı)
    - Aylık rapor tablosu (tekli seri ya da tüm sektörler yan yana)
    - Mevsimsellik karşılaştırması (mevsimsel düzeltmeli vs ham veri)
içerir.
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
from src.series_catalog import SERIES_CATALOG, get_categories, get_by_category

database.init_db()

# Bazı "başlık" serilerinin hangi kırılım kategorisiyle detaylandırılabileceğini
# tanımlar. Bir seri burada varsa, rapor tablosunda o satıra tıklandığında
# alt kategori kırılımı (bar + trend grafikleri) gösterilir.
HEADLINE_BREAKDOWN_MAP = {
    "CES0000000001": "Industry",   # Toplam Tarım Dışı İstihdam -> BLS sektörleri
    "ADPMNUSNERSA": "ADP",         # ADP Toplam -> ADP sektörleri (kendisi hariç tutulur)
}


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

if st.sidebar.button("🔄 Veriyi şimdi güncelle"):
    with st.spinner("BLS ve FRED API'lerinden veri çekiliyor..."):
        # Anahtarları önce Streamlit secrets'tan, yoksa ortam değişkeninden al
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
st.title("🇺🇸 ABD İstihdam Verileri — Genel Bakış")
st.caption("Kaynak: U.S. Bureau of Labor Statistics (BLS) + FRED/ADP National Employment Report")

series_in_category = get_by_category(category)

if not series_in_category:
    st.info("Bu kategoride seri bulunmuyor.")
    st.stop()

# Tüm serileri önceden yükleyelim (kartlar, trend, tablo, grafikler hepsi kullanacak)
card_data = {sid: load_series(sid) for sid in series_in_category}

# ---------------------------------------------------------------- özet kartlar + trend rozetleri
st.subheader(f"{category} — Güncel Durum")
cols = st.columns(min(4, len(series_in_category)))
for i, (sid, meta) in enumerate(series_in_category.items()):
    df = card_data[sid]
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
            trend = report_utils.compute_trend_indicator(df)
            icon, label = report_utils.TREND_LABELS[trend["direction"]]
            if trend["direction"] is not None:
                st.caption(f"{icon} {label}  (3 ay ort: {trend['recent_avg']:+.0f}, 12 ay ort: {trend['baseline_avg']:+.0f})")
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

# ---------------------------------------------------------------- aylık rapor tablosu
st.subheader("📅 Aylık Rapor Tablosu")

table_view = st.radio(
    "Görünüm",
    ["Tekli seri (detaylı)", "Sektörler yan yana (geniş tablo)"],
    horizontal=True,
    key="report_table_view",
)

if table_view == "Tekli seri (detaylı)":
    single_sid = st.selectbox(
        "Seri seçin",
        options=list(series_in_category.keys()),
        format_func=lambda sid: series_in_category[sid]["name"],
        key="report_table_single_series",
    )
    df = card_data.get(single_sid, load_series(single_sid))
    compact = report_utils.build_compact_report_table(df)
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
            key="genel_report_table_single",
        )
        st.download_button(
            "CSV olarak indir",
            data=compact.to_csv(index=False).encode("utf-8"),
            file_name=f"{single_sid}_aylik_rapor.csv",
            mime="text/csv",
            key="download_compact_table",
        )

        selected_rows = select_event.selection.rows if select_event and select_event.selection else []

        if selected_rows and single_sid in HEADLINE_BREAKDOWN_MAP:
            selected_period = compact.iloc[selected_rows[0]]["Dönem"]
            selected_date = pd.to_datetime(selected_period + "-01")

            breakdown_category = HEADLINE_BREAKDOWN_MAP[single_sid]
            breakdown_series = get_by_category(breakdown_category)
            # Başlık serisinin kendisi kırılım listesindeyse çıkar (örn. ADP Toplam, ADP kategorisinde de var)
            breakdown_data = {
                meta["name"]: load_series(sid)
                for sid, meta in breakdown_series.items()
                if sid != single_sid
            }

            with st.container(border=True):
                st.markdown(f"### 🔎 {selected_date.strftime('%B %Y')} — Kırılım Detayı")

                st.markdown("**1) O Ayki Değişim: Toplam vs Alt Kategoriler**")
                bar_data = report_utils.build_breakdown_bar_for_date(
                    selected_date, series_in_category[single_sid]["name"], df, breakdown_data
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
                        height=max(300, 40 * len(bar_data)),
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_title="Aylık Değişim (Bin Kişi)",
                    )
                    st.plotly_chart(fig_breakdown, use_container_width=True)

                st.markdown("**2) Alt Kategorilerin Yıllık % Değişimi (Zaman İçinde)**")
                yoy_lines = report_utils.build_pct_change_lines(breakdown_data, pct_type="yoy")
                if not yoy_lines.empty:
                    fig_yoy = px.line(
                        yoy_lines, x="date", y="Değişim %", color="Kategori",
                        labels={"date": "Tarih", "Değişim %": "Yıllık Değişim %"},
                    )
                    fig_yoy.add_vline(x=selected_date, line_dash="dot", line_color="gray")
                    fig_yoy.update_layout(
                        height=400,
                        margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig_yoy, use_container_width=True)

                st.markdown("**3) Alt Kategorilerin Aylık % Değişimi (Zaman İçinde)**")
                mom_lines = report_utils.build_pct_change_lines(breakdown_data, pct_type="mom")
                if not mom_lines.empty:
                    fig_mom = px.line(
                        mom_lines, x="date", y="Değişim %", color="Kategori",
                        labels={"date": "Tarih", "Değişim %": "Aylık Değişim %"},
                    )
                    fig_mom.add_vline(x=selected_date, line_dash="dot", line_color="gray")
                    fig_mom.update_layout(
                        height=400,
                        margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig_mom, use_container_width=True)
        elif selected_rows and single_sid not in HEADLINE_BREAKDOWN_MAP:
            st.caption(
                "ℹ️ Bu seri için tanımlı bir alt kategori kırılımı yok "
                "(şu an sadece Toplam Tarım Dışı İstihdam ve ADP Toplam için mevcut)."
            )
        else:
            st.caption("👆 Kırılım detayını görmek için tablodan bir satır (tarih) seçin.")
else:
    value_type_label = st.radio(
        "Gösterilecek değer",
        ["Aylık Değişim", "Seviye (Ham Değer)", "Yıllık % Değişim"],
        horizontal=True,
        key="wide_table_value_type",
    )
    value_type_map = {
        "Aylık Değişim": "change",
        "Seviye (Ham Değer)": "level",
        "Yıllık % Değişim": "yoy_pct",
    }
    series_named = {meta["name"]: card_data[sid] for sid, meta in series_in_category.items()}
    wide = report_utils.build_wide_report_table(series_named, value_type=value_type_map[value_type_label])
    if wide.empty:
        st.info("Bu kategoride veri yok.")
    else:
        st.dataframe(wide.style.format("{:+,.1f}", subset=wide.columns[1:], na_rep="—"), use_container_width=True, height=400)
        st.download_button(
            "CSV olarak indir",
            data=wide.to_csv(index=False).encode("utf-8"),
            file_name=f"{category.lower()}_genis_tablo.csv",
            mime="text/csv",
            key="download_wide_table",
        )

st.divider()

# ---------------------------------------------------------------- mevsimsellik karşılaştırması
nsa_capable = {
    sid: meta for sid, meta in series_in_category.items() if "nsa_pair" in meta
}

if nsa_capable:
    st.subheader("🌊 Mevsimsellik Karşılaştırması (Mevsimsel Düzeltmeli vs Ham Veri)")
    st.caption(
        "Mevsimsel düzeltmeli (SA) seri, her yıl tekrar eden mevsimsel dalgalanmaları "
        "(örn. yaz aylarında artan turizm istihdamı) matematiksel olarak arındırır. "
        "Ham (NSA) seri bu dalgalanmaları olduğu gibi gösterir — aradaki fark, o ayın "
        "mevsimsel etkisinin büyüklüğünü verir."
    )

    nsa_sid = st.selectbox(
        "Seri seçin",
        options=list(nsa_capable.keys()),
        format_func=lambda sid: nsa_capable[sid]["name"],
        key="nsa_comparison_series",
    )

    sa_df = card_data.get(nsa_sid, load_series(nsa_sid))
    nsa_series_id = nsa_capable[nsa_sid]["nsa_pair"]
    nsa_df = load_series(nsa_series_id)

    if sa_df.empty or nsa_df.empty:
        st.info(
            "Ham (NSA) veri henüz çekilmemiş olabilir. `python -m src.update_data` "
            "çalıştırdığınızda otomatik olarak dahil edilir."
        )
    else:
        fig_nsa = go.Figure()
        fig_nsa.add_trace(
            go.Scatter(x=sa_df["date"], y=sa_df["value"], mode="lines", name="Mevsimsel Düzeltmeli (SA)")
        )
        fig_nsa.add_trace(
            go.Scatter(x=nsa_df["date"], y=nsa_df["value"], mode="lines", name="Ham Veri (NSA)", line=dict(dash="dot"))
        )
        fig_nsa.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            hovermode="x unified",
        )
        st.plotly_chart(fig_nsa, use_container_width=True)

        # son ortak ayda SA vs NSA farkı = o ayın mevsimsel etkisi
        merged = pd.merge(
            sa_df[["date", "value"]], nsa_df[["date", "value"]],
            on="date", suffixes=("_sa", "_nsa"),
        )
        if not merged.empty:
            last_row = merged.sort_values("date").iloc[-1]
            seasonal_effect = last_row["value_nsa"] - last_row["value_sa"]
            st.metric(
                f"{last_row['date'].strftime('%B %Y')} Mevsimsel Etki (Ham − Düzeltmeli)",
                f"{seasonal_effect:+,.0f}K",
                help="Pozitifse o ay mevsimsel olarak normalden daha fazla istihdam vardır (örn. yaz sezonu), negatifse daha az.",
            )
else:
    st.caption("Bu kategoride mevsimsellik karşılaştırması için ham (NSA) veri eşlemesi tanımlı değil.")

st.divider()

# ---------------------------------------------------------------- ham veri tablosu ve indirme
with st.expander("📄 Ham veriyi görüntüle / indir (tüm kategori)"):
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

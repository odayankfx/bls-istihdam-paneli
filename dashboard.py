"""
ABD Ekonomik Veri Paneli — ana giriş noktası (navigasyon).

Bu dosya sadece sayfa yönlendirmesini kurar; gerçek sayfa içerikleri
views/ klasöründe. Yeni bir bölüm (örn. "Enflasyon") eklemek için:
    1. views/ klasörüne yeni sayfa dosyaları ekleyin
    2. Aşağıdaki st.navigation() sözlüğüne yeni bir bölüm/sayfa girin

Çalıştırmak için:
    streamlit run dashboard.py
"""

import streamlit as st

st.set_page_config(
    page_title="ABD Ekonomik Veri Paneli",
    page_icon="📊",
    layout="wide",
)

home_page = st.Page("views/home.py", title="Ana Sayfa", icon="🏠", default=True)

istihdam_genel = st.Page("views/istihdam_genel.py", title="Genel Bakış", icon="📊")
istihdam_nonfarm_detay = st.Page(
    "views/istihdam_nonfarm_detay.py", title="Tarım Dışı İstihdam Detay", icon="📈"
)

pg = st.navigation(
    {
        "": [home_page],
        "💼 ABD İstihdam": [istihdam_genel, istihdam_nonfarm_detay],
        # "💰 Enflasyon": [...],  # ileride buraya CPI/PPI/PCE sayfaları eklenecek
    }
)
pg.run()

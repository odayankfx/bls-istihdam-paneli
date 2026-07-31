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


def check_password():
    """
    Basit şifre koruması. Panel WordPress sitesine iframe ile gömülü olduğu
    için, doğrudan Streamlit Cloud linkini bilenlerin de içeriği görmemesi
    için buradan girmiş olmaları gerekir.

    Şifre Streamlit Cloud'daki Secrets kısmında APP_PASSWORD olarak
    tanımlanmalıdır.
    """

    def password_entered():
        if st.session_state.get("password_input") == st.secrets.get("APP_PASSWORD", ""):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Giriş Gerekli")
    st.text_input("Şifre", type="password", key="password_input", on_change=password_entered)
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Şifre yanlış, tekrar deneyin.")
    return False


if not check_password():
    st.stop()

home_page = st.Page("views/home.py", title="Ana Sayfa", icon="🏠", default=True)

istihdam_genel = st.Page("views/istihdam_genel.py", title="Genel Bakış", icon="📊")
istihdam_nonfarm_detay = st.Page(
    "views/istihdam_nonfarm_detay.py", title="Tarım Dışı İstihdam Detay", icon="📈"
)
istihdam_jolts = st.Page("views/istihdam_jolts.py", title="JOLTS", icon="🧩")

enflasyon_genel = st.Page("views/enflasyon_genel.py", title="Genel Bakış (CPI)", icon="💰")
enflasyon_ppi = st.Page("views/enflasyon_ppi.py", title="Genel Bakış (ÜFE/PPI)", icon="🏭")
enflasyon_pce = st.Page("views/enflasyon_pce.py", title="Genel Bakış (PCE)", icon="🏦")

pg = st.navigation(
    {
        "": [home_page],
        "💼 ABD İstihdam": [istihdam_genel, istihdam_nonfarm_detay, istihdam_jolts],
        "💰 Enflasyon": [enflasyon_genel, enflasyon_ppi, enflasyon_pce],
    }
)
pg.run()

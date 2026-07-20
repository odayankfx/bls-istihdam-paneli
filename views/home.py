"""
Ana Sayfa — şimdilik boş / karşılama ekranı.

İleride buraya genel bir özet (tüm bölümlerden birer öne çıkan gösterge gibi)
eklenebilir. Şimdilik sadece yönlendirme amaçlı.
"""

import streamlit as st

st.title("🇺🇸 ABD Ekonomik Veri Paneli")

st.markdown(
    """
    Sol menüden bir bölüm seçin:

    - **💼 ABD İstihdam** — BLS ve ADP istihdam verileri, tarım dışı istihdam
      detayları, revizyon takibi ve kırılımlar.

    Yakında eklenecek:
    - **💰 Enflasyon** — CPI, PPI, PCE verileri.
    """
)

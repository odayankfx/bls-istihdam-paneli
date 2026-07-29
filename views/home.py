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
      detayları, JOLTS, revizyon takibi ve kırılımlar.
    - **💰 Enflasyon** — BLS Tüketici Fiyat Endeksi (CPI-U): başlık göstergeleri,
      çekirdek enflasyon, ana harcama kategorileri.

    Yakında eklenecek:
    - PPI, PCE ve Challenger Job Cuts verileri.
    """
)

import streamlit as st
import psycopg2
import os
from db import get_balance, get_offers

st.set_page_config(page_title="Bybit Dual Asset Bot", layout="wide")

st.title("📊 Bybit Dual Asset Bot (Consultivo + Scanner)")

tabs = st.tabs(["💰 Saldo & Alocação", "📈 Melhores Ofertas (Dual Asset)"])

with tabs[0]:
    st.subheader("Saldo da Conta (Unified)")
    balance = get_balance()
    if balance:
        st.metric("Total Equity", f"${balance['totalEquity']:.2f}")
        st.metric("Wallet Balance", f"${balance['walletBalance']:.2f}")
        st.metric("Available", f"${balance['availableBalance']:.2f}")
    else:
        st.error("Erro ao buscar saldo.")

with tabs[1]:
    st.subheader("Melhores Ofertas Dual Asset")
    offers = get_offers()
    if offers:
        st.dataframe(offers)
    else:
        st.warning("Nenhuma oferta encontrada.")

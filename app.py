import streamlit as st
import pandas as pd
from pybit.unified_trading import HTTP

import os

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)

st.title("📊 Bybit Dual Asset Bot (Consultivo)")

try:
    balance = session.get_wallet_balance(accountType="UNIFIED")
    st.subheader("💰 Saldo da Conta (Unified)")
    st.json(balance)
except Exception as e:
    st.error(f"Erro ao buscar saldo: {e}")

st.markdown("---")
st.info("Este painel mostra apenas dados consultivos. Nenhuma ordem é executada automaticamente ainda.")

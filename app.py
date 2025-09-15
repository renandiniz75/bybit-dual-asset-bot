import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
from db import engine, ensure_schema
from bybit_api import get_unified_balance

st.set_page_config(page_title="Bybit Dual Asset Bot", layout="wide")

st.title("📊 Bybit Dual Asset Bot (Consultivo)")

# garante schema ao subir
try:
    ensure_schema()
except Exception as e:
    st.error(f"Erro ao preparar o schema do banco: {e}")

with st.sidebar:
    st.header("Configurações")
    apr_min = st.number_input(
        "APR mínimo (decimal)",
        min_value=0.0, max_value=5.0,
        value=float(os.getenv("APR_MIN", 0.50)),
        step=0.05
    )
    st.caption("Ex.: 0.50 = 50% a.a.")

tab1, tab2, tab3 = st.tabs(["💰 Saldo (UNIFIED)", "🔥 Best Picks", "📈 Histórico / Gráficos"])

with tab1:
    st.subheader("Saldo da Conta (UNIFIED)")
    resp = get_unified_balance()
    if isinstance(resp, dict) and resp.get("error"):
        st.error(resp["error"])
    else:
        st.code(resp, language="json")

with tab2:
    st.subheader("Ofertas acima do APR mínimo")
    try:
        eng = engine()
        df = pd.read_sql(
            "SELECT * FROM offers WHERE apr >= :m ORDER BY apr DESC LIMIT 100",
            eng,
            params={"m": apr_min}
        )
        if df.empty:
            st.info("Sem dados na tabela 'offers'. Insira dados de teste ou ative o coletor.")
        else:
            st.dataframe(df, use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.scatter(df, x="strike", y="apr", color="asset", symbol="side", hover_data=["tenor_d"])
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                hm = df.groupby(["side", "tenor_d"], as_index=False)["apr"].mean()
                if not hm.empty:
                    fig2 = px.density_heatmap(hm, x="tenor_d", y="side", z="apr", color_continuous_scale="Viridis")
                    st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao consultar o banco: {e}")

with tab3:
    st.subheader("Histórico de Best Picks (últimas 24h)")
    try:
        eng = engine()
        hist = pd.read_sql(
            """
            SELECT * FROM best_picks_history
            WHERE ts >= NOW() - INTERVAL '24 hours'
            ORDER BY ts DESC LIMIT 1000
            """,
            eng
        )
        if hist.empty:
            st.info("Nenhum registro ainda em best_picks_history.")
        else:
            fig3 = px.line(hist, x="ts", y="apr", color="asset", line_group="side", markers=True, hover_data=["tenor_d", "strike", "dist"])
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(hist.head(200), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao consultar histórico: {e}")

\
    import os, time
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    from sqlalchemy import text
    from db import engine, ensure_schema
    from bybit_api import get_unified_balance

    st.set_page_config(page_title="Bybit Dual Asset Bot", layout="wide")
    st.title("📊 Bybit Dual Asset Bot (Consultivo)")

    # garante schema
    try:
        ensure_schema()
    except Exception as e:
        st.error(f"Erro ao preparar schema: {e}")

    with st.sidebar:
        st.header("Configurações")
        apr_min = st.number_input("APR mínimo (decimal)", 0.0, 5.0, float(os.getenv("APR_MIN", 0.50)), 0.05)
        tenors = st.multiselect("Tenor (dias)", options=[2,3,4], default=[2,3,4])
        auto_refresh = st.toggle("Auto-refresh", value=True)
        refresh_sec = st.number_input("Intervalo (s)", min_value=10, max_value=300, value=30, step=5)

    tab1, tab2, tab3 = st.tabs(["💰 Saldo (UNIFIED)", "🔥 Best Picks / Ofertas", "📈 Histórico"])

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
            q = """
            SELECT ts, asset, side, tenor_d, strike::float AS strike, apr::float AS apr
            FROM offers
            WHERE apr >= :m AND tenor_d = ANY(:tenors)
            ORDER BY ts DESC, apr DESC
            LIMIT 500
            """
            df = pd.read_sql(text(q), eng, params={"m": apr_min, "tenors": tenors})
            if df.empty:
                st.info("Sem dados na tabela 'offers'. Insira dados de teste ou ative o coletor.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.scatter(df, x="strike", y="apr", color="asset", symbol="side",
                                     hover_data=["tenor_d","ts"], title="APR × Strike (ofertas filtradas)")
                    fig.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    hm = df.groupby(["side","tenor_d"], as_index=False)["apr"].mean()
                    if not hm.empty:
                        fig2 = px.density_heatmap(hm, x="tenor_d", y="side", z="apr",
                                                  color_continuous_scale="Viridis",
                                                  title="Heatmap — APR médio por Tenor × Direção")
                        fig2.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=0))
                        st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao consultar banco: {e}")

    with tab3:
        st.subheader("Histórico de Best Picks (últimas 24h)")
        try:
            eng = engine()
            hist = pd.read_sql(text(\"\"\"
                SELECT ts, asset, side, tenor_d, strike::float AS strike, apr::float AS apr, dist::float AS dist
                FROM best_picks_history
                WHERE ts >= NOW() - INTERVAL '24 hour'
                ORDER BY ts ASC
            \"\"\"), eng)
            if hist.empty:
                st.info("Ainda não há registros em best_picks_history.")
            else:
                hist["key"] = hist["asset"] + "-" + hist["side"].str.slice(0,1) + "-" + hist["tenor_d"].astype(str)+"d"
                fig3 = px.line(hist, x="ts", y="apr", color="key",
                               title="Evolução de APR dos Best Picks (24h)")
                fig3.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig3, use_container_width=True)
                st.dataframe(hist.tail(200), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro ao consultar histórico: {e}")

    # Auto refresh
    if auto_refresh:
        time.sleep(max(10, int(refresh_sec)))
        st.rerun()

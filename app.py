
import os, json, pandas as pd, plotly.express as px, streamlit as st
from dotenv import load_dotenv
from bybit_api import get_unified_balance
from utils import usd, pct, safe_float, sum_coin_usd
from offers_client import rank_offers

load_dotenv()

st.set_page_config(page_title="Bybit Dual Asset Bot", page_icon="📊", layout="wide")

API_KEY = os.getenv("API_KEY","").strip()
API_SECRET = os.getenv("API_SECRET","").strip()
MIN_APR = float(os.getenv("MIN_APR","0.5"))
SCAN_SYMBOLS = [s.strip().upper() for s in os.getenv("SCAN_SYMBOLS","BTC,ETH").split(",") if s.strip()]
SCAN_DURATIONS = [int(x) for x in os.getenv("SCAN_DURATIONS_DAYS","2,3,4,7").split(",") if x.strip().isdigit()]

# HEADER
st.markdown("## 📊 Bybit Dual Asset Bot (Consultivo + Scanner)")

tab1, tab2 = st.tabs(["📋 Saldo & Alocação", "🔎 Melhores Ofertas (Dual Asset)"])

with tab1:
    if not API_KEY or not API_SECRET:
        st.error("Configure API_KEY e API_SECRET nas variáveis de ambiente.")
    else:
        try:
            data = get_unified_balance(API_KEY, API_SECRET)
            st.caption("Resposta bruta de saldo (para debug/desenvolvedor):")
            with st.expander("Ver JSON"):
                st.json(data)
            lst = (data.get("result",{}).get("list") or [])
            row = lst[0] if lst else {}
            coins = row.get("coin",[])
            # Cards topo
            total_wallet = safe_float(row.get("totalWalletBalance",0.0))
            total_avail = safe_float(row.get("totalAvailableBalance",0.0))
            total_equity = safe_float(row.get("totalEquity",0.0))
            c1,c2,c3 = st.columns(3)
            c1.metric("Total Equity", usd(total_equity))
            c2.metric("Wallet Balance", usd(total_wallet))
            c3.metric("Available", usd(total_avail))

            # Tabela de moedas
            records=[]
            for c in coins:
                sym = c.get("coin")
                rec = {
                    "Ativo": sym,
                    "Equity": safe_float(c.get("equity",0.0)),
                    "Free": safe_float(c.get("free",0.0)),
                    "Wallet": safe_float(c.get("walletBalance",0.0)),
                    "USD Value": safe_float(c.get("usdValue",0.0)),
                    "Unreal. PnL": safe_float(c.get("unrealisedPnl",0.0)),
                }
                records.append(rec)
            df = pd.DataFrame(records).sort_values("USD Value", ascending=False)
            st.markdown("#### 📄 Detalhe por Ativo")
            st.dataframe(
                df.style.format({
                    "Equity":"{:.6f}",
                    "Free":"{:.6f}",
                    "Wallet":"{:.6f}",
                    "USD Value":"${:,.2f}",
                    "Unreal. PnL":"${:,.2f}",
                }),
                use_container_width=True,
                hide_index=True
            )

            # Pizza de alocação
            if not df.empty:
                fig = px.pie(df, values="USD Value", names="Ativo", title="Alocação por USD", hole=0.35)
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao buscar saldo: {e}")

with tab2:
    st.markdown("##### Parâmetros do Scanner")
    c1,c2,c3 = st.columns(3)
    with c1:
        min_apr_in = st.number_input("APR mínimo (anualizado)", value=MIN_APR, step=0.05, min_value=0.0, max_value=5.0, format="%.2f")
    with c2:
        symbols_in = st.multiselect("Símbolos", options=["BTC","ETH"], default=SCAN_SYMBOLS)
    with c3:
        days_in = st.multiselect("Durações (dias)", options=[2,3,4,7,14], default=SCAN_DURATIONS)
    st.caption("Clique em **Escanear** para buscar e ranquear ofertas públicas. Se o site mudar, alguns endpoints podem falhar – o app tenta múltiplas rotas automaticamente.")
    if st.button("🚀 Escanear", type="primary"):
        try:
            ranked = rank_offers(symbols_in, min_apr_in, days_in)
            if not ranked:
                st.warning("Nenhuma oferta encontrada (ou endpoints indisponíveis). Você pode tentar novamente, ajustar APR/dias, ou fornecer `BYBIT_COOKIES_JSON`.")
            else:
                # DataFrame bonito
                df = pd.DataFrame(ranked)
                df["APR %"] = (df["apr"]*100.0).round(2)
                df["Distância %"] = (df["distance_pct"]*100.0).round(2)
                df = df.rename(columns={
                    "direction":"Direção",
                    "symbol":"Símbolo",
                    "days":"Dias",
                    "target":"Preço Alvo",
                })
                cols = ["product","Direção","Símbolo","Dias","Preço Alvo","APR %","Distância %"]
                st.markdown("#### 🏆 Top Ofertas")
                st.dataframe(
                    df[cols].style.format({
                        "Preço Alvo":"${:,.2f}",
                        "APR %":"{:,.2f}%",
                        "Distância %":"{:,.2f}%"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                # Heatmap simples APR por símbolo vs dias
                heat = (
                    df.groupby(["Símbolo","Dias"])["APR %"]
                      .max()
                      .reset_index()
                      .pivot(index="Símbolo", columns="Dias", values="APR %")
                )
                st.markdown("#### 🔥 Heatmap – Melhor APR por Símbolo x Dias")
                st.dataframe(heat.style.background_gradient(cmap="Greens").format("{:,.2f}%"), use_container_width=True)
        except Exception as e:
            st.error(f"Falha ao escanear: {e}")
    st.info("Este scanner é *consultivo* e não envia ordens. Para execução automática, podemos evoluir para um worker separado com regras de risco.")

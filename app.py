import os
import streamlit as st
import pandas as pd
from pybit.unified_trading import HTTP
from db import get_conn, init_schema

APR_MIN = float(os.getenv("APR_MIN","0.50"))
MIN_DIST_BTC = float(os.getenv("MIN_DIST_BTC","0.015"))
MIN_DIST_ETH = float(os.getenv("MIN_DIST_ETH","0.020"))
API_KEY = os.getenv("API_KEY","")
API_SECRET = os.getenv("API_SECRET","")

st.set_page_config(page_title="Bybit Dual Asset Bot", page_icon="📈", layout="centered")
st.title("📊 Bybit Dual Asset Bot (Autônomo)")

init_schema()

@st.cache_data(ttl=30)
def get_spot(symbol):
    s = HTTP(api_key=API_KEY, api_secret=API_SECRET)
    d = s.get_tickers(category="spot", symbol=symbol)
    return float(d["result"]["list"][0]["lastPrice"])

@st.cache_data(ttl=15)
def pull_offers_df():
    with get_conn() as c:
        return pd.read_sql(
            "SELECT ts, asset, side, tenor_d, strike::float AS strike, apr::float AS apr FROM offers WHERE ts > NOW() - INTERVAL '1 hour'",
            c
        )

try:
    btc = get_spot("BTCUSDT")
    eth = get_spot("ETHUSDT")
    st.metric("BTCUSDT", f"{btc:,.2f}")
    st.metric("ETHUSDT", f"{eth:,.2f}")
except Exception as e:
    st.error(f"Erro spot: {e}")
    btc = eth = None

df = pull_offers_df()
if df.empty:
    st.warning("Ainda sem ofertas recentes no banco. Aguarde o scraper (~2 min).")
else:
    price_map = {"BTC": btc, "ETH": eth}
    min_map = {"BTC": MIN_DIST_BTC, "ETH": MIN_DIST_ETH}
    df["spot"] = df["asset"].map(price_map)
    df = df.dropna(subset=["spot"])

    def dist_frac(row):
        if row["side"] == "SELL":
            return abs(row["strike"]/row["spot"] - 1.0)
        else:
            return abs(1.0 - row["strike"]/row["spot"])
    df["dist"] = df.apply(dist_frac, axis=1)
    df["apr_ann"] = df["apr"]/100.0
    df["ok"] = (df["apr_ann"] >= APR_MIN) & (df.apply(lambda r: r["dist"] >= min_map.get(r["asset"],0), axis=1))
    df["score"] = 0.7*df["dist"] + 0.3*df["apr_ann"]

    top = (df[df["ok"]]
           .sort_values(["asset","side","tenor_d","score"], ascending=[True,True,True,False])
           .groupby(["asset","side","tenor_d"])
           .head(1))

    st.subheader(f"🏆 Best picks (APR ≥ {int(APR_MIN*100)}% e maior distância)")
    if top.empty:
        st.info("Nenhuma oferta bateu a regra no momento.")
    else:
        out = top[["asset","side","tenor_d","strike","spot","dist","apr"]].copy()
        out.rename(columns={"tenor_d":"tenor(d)","dist":"dist_frac","apr":"apr_%_ann"}, inplace=True)
        out["dist_%"] = (out["dist_frac"]*100).round(3)
        out["apr_%"] = out["apr_%_ann"].round(2)
        st.dataframe(out[["asset","side","tenor(d)","strike","spot","dist_%","apr_%"]], use_container_width=True)

    with st.expander("📋 Ofertas recentes (≤ 1h)"):
        show = df.sort_values("ts", ascending=False).copy()
        show["dist_%"] = (show["dist"]*100).round(3)
        st.dataframe(show[["ts","asset","side","tenor_d","strike","spot","dist_%","apr"]], use_container_width=True)

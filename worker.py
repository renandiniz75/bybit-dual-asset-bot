import os
import time
import pandas as pd
from pybit.unified_trading import HTTP

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

session = HTTP(testnet=False, api_key=API_KEY, api_secret=API_SECRET)

def best_pick_dual_asset():
    # Exemplo simplificado: puxar apenas preços atuais ETH e BTC
    try:
        eth_price = session.get_tickers(category="spot", symbol="ETHUSDT")
        btc_price = session.get_tickers(category="spot", symbol="BTCUSDT")
        return {
            "ETH": eth_price["result"]["list"][0]["lastPrice"],
            "BTC": btc_price["result"]["list"][0]["lastPrice"]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    while True:
        print("🔎 Checando melhores opções...")
        data = best_pick_dual_asset()
        print(data)
        time.sleep(60)  # roda a cada 1 min

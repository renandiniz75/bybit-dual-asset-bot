import psycopg2
import os
import requests
import hmac, hashlib, time

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def get_balance():
    try:
        ts = str(int(time.time() * 1000))
        payload = f"api_key={API_KEY}&timestamp={ts}"
        sign = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        url = f"https://api.bybit.com/v5/account/wallet-balance?accountType=UNIFIED&api_key={API_KEY}&timestamp={ts}&sign={sign}"
        r = requests.get(url).json()
        if 'result' in r and 'list' in r['result'] and len(r['result']['list']) > 0:
            acc = r['result']['list'][0]
            return {
                "totalEquity": float(acc.get("totalEquity", 0)),
                "walletBalance": float(acc.get("totalWalletBalance", 0)),
                "availableBalance": float(acc.get("totalAvailableBalance", 0))
            }
    except Exception as e:
        print("Erro get_balance:", e)
    return None

def get_offers():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT symbol, apr, duration, strikePrice, side, ts FROM dual_asset_offers ORDER BY ts DESC LIMIT 20")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("Erro get_offers:", e)
    return []

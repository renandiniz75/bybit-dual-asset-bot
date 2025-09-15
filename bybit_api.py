import os
from pybit.unified_trading import HTTP

def get_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if not api_key or not api_secret:
        return None
    return HTTP(testnet=False, api_key=api_key, api_secret=api_secret)

def get_unified_balance():
    client = get_client()
    if client is None:
        return {"error": "API_KEY/API_SECRET não configurados."}
    try:
        resp = client.get_wallet_balance(accountType="UNIFIED")
        return resp
    except Exception as e:
        return {"error": str(e)}

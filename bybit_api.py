
import os, time, hmac, hashlib, requests
from typing import Dict, Any

BASE = "https://api.bybit.com"

def _auth_headers(api_key: str, api_secret: str, query: str = "", body: str = "") -> Dict[str, str]:
    ts = str(int(time.time()*1000))
    recv = "5000"
    prehash = ts + api_key + recv + query + body
    sig = hmac.new(api_secret.encode(), prehash.encode(), hashlib.sha256).hexdigest()
    return {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": ts,
        "X-BAPI-RECV-WINDOW": recv,
        "X-BAPI-SIGN": sig,
        "Content-Type": "application/json"
    }

def get_unified_balance(api_key: str, api_secret: str):
    url = f"{BASE}/v5/account/wallet-balance"
    params = {"accountType":"UNIFIED"}
    headers = _auth_headers(api_key, api_secret, query="accountType=UNIFIED")
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

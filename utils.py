
import math

def usd(x):
    try:
        return "${:,.2f}".format(float(x))
    except Exception:
        return "-"

def pct(x, decimals=2):
    try:
        return f"{float(x)*100:.{decimals}f}%"
    except Exception:
        return "-"

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def sum_coin_usd(coin):
    return safe_float(coin.get("usdValue",0.0))

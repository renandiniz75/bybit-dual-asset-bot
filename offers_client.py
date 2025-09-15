
import os, json, time, requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"

def _maybe_cookies() -> dict:
    cj = os.getenv("BYBIT_COOKIES_JSON","").strip()
    if not cj: return {}
    try:
        return json.loads(cj)
    except Exception:
        return {}

def _get(url: str, params: dict=None) -> Optional[requests.Response]:
    try:
        resp = requests.get(url, params=params or {}, timeout=20, headers={"User-Agent": USER_AGENT}, cookies=_maybe_cookies())
        if resp.status_code==200:
            return resp
        return None
    except Exception:
        return None

def try_fetch_dual_asset(symbol: str) -> List[Dict[str,Any]]:
    """
    Tenta diversos endpoints públicos/semipúblicos da Bybit Web para listar ofertas do Dual Asset.
    Retorna lista padronizada com: product, direction, symbol, days, target, apr, distance_pct, raw.
    """
    results: List[Dict[str,Any]] = []
    # 1) Endpoint usado em algumas builds web (pode variar com o tempo)
    # Observação: mantemos múltiplas tentativas; se nenhuma responder, retorna vazio.
    trial_urls = [
        # hipotéticos / históricos (podem mudar):
        "https://api2.bybit.com/priapi/earn/v1/dual-asset/list",
        "https://api2.bybit.com/priapi/earn/v3/dual-asset/list",
        "https://www.bybit.com/priapi/earn/v1/dual-asset/list",
    ]
    params = {"symbol": symbol.upper()}
    for u in trial_urls:
        r = _get(u, params)
        if r is None: 
            continue
        try:
            data = r.json()
        except Exception:
            # fallback: às vezes vem HTML com JSON embutido
            try:
                soup = BeautifulSoup(r.text, "html.parser")
                pre = soup.find("pre")
                if pre:
                    data = json.loads(pre.text)
                else:
                    continue
            except Exception:
                continue
        # Normaliza caminhos comuns
        items = None
        for key in ("result","data","list","items"):
            if isinstance(data, dict) and key in data:
                items = data[key]
                break
        if items is None and isinstance(data, list):
            items = data
        if not items:
            # alguns formatos aninham mais um nível
            for k,v in (data.items() if isinstance(data, dict) else []):
                if isinstance(v, (list,dict)):
                    items = v
                    break
        # Converte itens comuns
        def coerce_float(x, default=0.0):
            try:
                return float(str(x))
            except Exception:
                return default
        def add_item(d):
            results.append({
                "product":"Dual Asset",
                "direction": d.get("direction") or d.get("side") or d.get("mode") or "",
                "symbol": d.get("symbol") or d.get("pair") or symbol.upper(),
                "days": int(d.get("days") or d.get("duration") or d.get("tenor") or 0),
                "target": coerce_float(d.get("targetPrice") or d.get("target") or d.get("strike") or 0.0),
                "apr": coerce_float(d.get("apr") or d.get("annualApr") or d.get("estApr") or 0.0),
                "distance_pct": coerce_float(d.get("distancePct") or d.get("distance") or 0.0),
                "raw": d
            })
        if isinstance(items, list):
            for d in items:
                add_item(d)
        elif isinstance(items, dict):
            inner = items.get("list") or items.get("items") or []
            for d in inner:
                add_item(d)
        if results:
            break
    return results

def rank_offers(symbols: List[str], min_apr: float, durations: List[int]) -> List[Dict[str,Any]]:
    ranked: List[Dict[str,Any]] = []
    for sym in symbols:
        offers = try_fetch_dual_asset(sym)
        # filtra por dias desejados, min APR, e segura maiores distâncias primeiro
        filtered = []
        for o in offers:
            if o["days"] in durations and o["apr"]>=min_apr:
                filtered.append(o)
        # ordena por distância desc, depois APR desc
        filtered.sort(key=lambda x: (x.get("distance_pct",0.0), x.get("apr",0.0)), reverse=True)
        ranked += filtered[:50]
    # ordena geral e retorna top 100
    ranked.sort(key=lambda x: (x.get("apr",0.0), x.get("distance_pct",0.0)), reverse=True)
    return ranked[:100]

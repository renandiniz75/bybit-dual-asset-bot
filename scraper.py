import os, asyncio, time, json, re
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from db import init_schema, insert_batch

BYBIT_COOKIES_JSON = os.getenv("BYBIT_COOKIES_JSON", "")

DUAL_URL = "https://www.bybit.com/earn/dual-asset/"
PAIRS = [
    ("BTC", "Sell High", "SELL"),
    ("BTC", "Buy Low",  "BUY"),
    ("ETH", "Sell High", "SELL"),
    ("ETH", "Buy Low",  "BUY"),
]
TENORS = [2,3,4]  # dias

def parse_apr_and_strike_from_html(html_text):
    offers = []
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text(" ", strip=True)
    pat = re.compile(r"(\d{3,6}[\.,]?\d*)[^%]{0,40}(\d{1,3}\.\d{1,2})%")
    for m in pat.finditer(text):
        strike_raw = m.group(1)
        apr_raw = m.group(2)
        try:
            strike = float(strike_raw.replace(".","").replace(",",""))
            apr = float(apr_raw)
            offers.append((strike, apr))
        except:
            continue
    return offers

async def scrape_once():
    rows_total = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context()
        if BYBIT_COOKIES_JSON:
            try:
                cookies = json.loads(BYBIT_COOKIES_JSON)
                await ctx.add_cookies(cookies)
            except Exception as e:
                print("Erro carregando cookies JSON:", e)

        page = await ctx.new_page()
        await page.goto(DUAL_URL, wait_until="networkidle")

        for asset, tab_label, side in PAIRS:
            try:
                await page.get_by_text(asset, exact=True).first.click()
                await page.wait_for_timeout(300)
            except:
                pass
            try:
                await page.get_by_role("tab", name=tab_label).click()
                await page.wait_for_timeout(400)
            except:
                pass

            for tenor in TENORS:
                try:
                    await page.get_by_text(f"{tenor} Days", exact=True).click()
                    await page.wait_for_timeout(700)
                except:
                    pass

                html = await page.content()
                parsed = parse_apr_and_strike_from_html(html)
                seen = set(); cleaned=[]
                for strike, apr in parsed:
                    key = (asset, side, tenor, strike)
                    if key in seen: 
                        continue
                    seen.add(key)
                    cleaned.append((asset, side, tenor, strike, apr))
                rows_total.extend(cleaned)

        await browser.close()

    if rows_total:
        insert_batch(rows_total)
    print(datetime.utcnow().isoformat(), f"scrape: {len(rows_total)} linhas salvas")
    return rows_total

def main():
    init_schema()
    while True:
        try:
            asyncio.run(scrape_once())
        except Exception as e:
            print("scrape erro:", e)
        time.sleep(120)

if __name__ == "__main__":
    main()

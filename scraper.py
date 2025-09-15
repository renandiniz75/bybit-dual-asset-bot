import os, requests, psycopg2, time

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def scrape():
    url = "https://api.bybit.com/v5/earn/dual/list"
    r = requests.get(url).json()
    offers = r.get("result", {}).get("list", [])
    if not offers:
        print("Nenhuma oferta encontrada.")
        return
    conn = get_conn()
    cur = conn.cursor()
    for o in offers:
        cur.execute(
            "INSERT INTO dual_asset_offers (symbol, apr, duration, strikePrice, side) VALUES (%s,%s,%s,%s,%s)",
            (o.get("symbol"), o.get("apr"), o.get("duration"), o.get("strikePrice"), o.get("side"))
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"{len(offers)} ofertas salvas.")

if __name__ == "__main__":
    while True:
        scrape()
        time.sleep(int(os.getenv("SCRAPER_INTERVAL", 60)))

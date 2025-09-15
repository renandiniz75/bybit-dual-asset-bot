import time, os
from db import ensure_schema, engine

def scrape_once():
    ensure_schema()
    print("Scraper placeholder executado - aguardando coleta real...")

if __name__ == "__main__":
    interval = int(os.getenv("SCRAPE_INTERVAL", 90))
    while True:
        scrape_once()
        time.sleep(interval)

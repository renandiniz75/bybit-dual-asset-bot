import time, os
from db import ensure_schema

def scrape_once():
    # Placeholder: trocaremos por coleta real depois.
    ensure_schema()
    print("[scraper] schema ok — aguardando implementação de coleta real.")

if __name__ == "__main__":
    interval = int(os.getenv("SCRAPE_INTERVAL", 90))
    while True:
        try:
            scrape_once()
        except Exception as e:
            print("[scraper] erro:", e)
        time.sleep(interval)

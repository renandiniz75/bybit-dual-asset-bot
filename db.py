import os
import psycopg2
import psycopg2.extras

def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

def init_schema():
    sql = '''
    CREATE TABLE IF NOT EXISTS offers (
      id BIGSERIAL PRIMARY KEY,
      ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      asset TEXT NOT NULL,
      side TEXT NOT NULL,
      tenor_d INT NOT NULL,
      strike NUMERIC NOT NULL,
      apr NUMERIC NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_offers_recent ON offers(asset, side, tenor_d, ts DESC);
    '''
    with get_conn() as c:
        with c.cursor() as cur:
            cur.execute(sql)

def insert_batch(rows):
    if not rows:
        return
    with get_conn() as c:
        with c.cursor() as cur:
            cur.executemany(
                "INSERT INTO offers(asset, side, tenor_d, strike, apr) VALUES(%s,%s,%s,%s,%s)",
                rows
            )

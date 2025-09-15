import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

_engine = None

def engine():
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL não definido")
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine

SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS offers (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  asset TEXT NOT NULL,
  side  TEXT NOT NULL,
  tenor_d INT  NOT NULL,
  strike NUMERIC NOT NULL,
  apr    NUMERIC NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_offers_ts   ON offers(ts DESC);
CREATE INDEX IF NOT EXISTS idx_offers_key  ON offers(asset, side, tenor_d, ts DESC);

CREATE TABLE IF NOT EXISTS snapshots (
  snap_id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS best_picks_history (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  asset TEXT NOT NULL,
  side  TEXT NOT NULL,
  tenor_d INT NOT NULL,
  strike NUMERIC NOT NULL,
  apr    NUMERIC NOT NULL,
  dist   NUMERIC NOT NULL
);
'''

def ensure_schema():
    eng = engine()
    with eng.begin() as con:
        for stmt in SCHEMA_SQL.split(";"):
            s = stmt.strip()
            if s:
                con.execute(text(s))

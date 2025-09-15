-- Criação manual das tabelas (se preferir rodar no console do Postgres)
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

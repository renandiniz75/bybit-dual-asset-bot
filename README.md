# Bybit Dual Asset Bot — Full v6 (Render-ready)

## Conteúdo
- `runtime.txt` e `.python-version`: força Python 3.11.9
- `requirements.txt`: deps com wheels para py3.11
- `render.yaml`: web + worker (build otimizado), região frankfurt
- `app.py`: painel Streamlit (saldo, ofertas, gráficos, histórico)
- `db.py`: Postgres + criação automática de schema
- `init.sql`: opcional para criação manual via console
- `bybit_api.py`, `scraper.py`, `.streamlit/config.toml`

## Deploy (GitHub → Render)
1. Suba estes arquivos **na raiz** do seu repositório no GitHub.
2. No Render: **New → Blueprint** e aponte para o repo (ou redeploy o blueprint existente).
3. Crie um **PostgreSQL** (Frankfurt) e copie a **Internal Database URL**.
4. Em **dualasset-web** e **dualasset-scraper**, adicione `DATABASE_URL` = Internal URL.
5. Em **dualasset-web**, adicione `API_KEY` e `API_SECRET` (Bybit) para ver saldo UNIFIED.
6. **Manual Deploy → Clear cache & Deploy** em web e worker.

## Teste rápido (dados fictícios)
Rode no console do Postgres:
```sql
INSERT INTO offers(asset, side, tenor_d, strike, apr) VALUES
('BTC','SELL',4,120000,68.2),
('BTC','BUY', 4,108000,55.5),
('ETH','SELL',4,4850,102.3),
('ETH','BUY', 4,4400,61.7);
```
Abra o painel e veja as tabelas/gráficos.

## Notas
- O `scraper.py` é **placeholder**. Assim que você confirmar que o painel está ok, eu te envio o scraper real.

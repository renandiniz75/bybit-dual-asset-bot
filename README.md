# Bybit Dual Asset Bot

## Serviços
- **dualasset-web**: Painel Streamlit (saldo + alocação + ofertas).
- **dualasset-scraper**: Worker que salva ofertas públicas Dual Asset no Postgres.

## Como usar
1. Crie um Postgres no Render.
2. Rode o `sql/create_tables.sql` para criar a tabela.
3. Configure variáveis de ambiente:
   - `DATABASE_URL`
   - `API_KEY`
   - `API_SECRET`
   - `SCRAPER_INTERVAL` (opcional)
4. Faça deploy via Render Blueprint (`render.yaml`).

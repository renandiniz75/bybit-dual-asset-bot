# Bybit Dual Asset Bot — Deploy no Render (copia/cola)

Este pacote sobe **dois serviços** no Render (região **Frankfurt/EU**):
- **dualasset-web** (Streamlit): painel consultivo, lê do Postgres e mostra os **Best Picks**.
- **dualasset-scraper** (Playwright): entra na página do **Dual Asset** da Bybit e **coleta as ofertas automaticamente**, salvando no Postgres.

> **Motivo do Playwright**: a Bybit não expõe API pública estável para Dual Asset. O scraper lê exatamente o que a página mostra para você (autônomo, sem colar nada).

---

## Passo a passo (sem terminal)

### 1) GitHub
- Crie um repositório (ex.: `bybit-dual-asset-bot`).
- Faça **upload de todos os arquivos deste ZIP** (inclusive `render.yaml`).
- **Commit**.

### 2) Render — Blueprint
- Render → **New → Blueprint**.
- Cole a URL do repositório e **Apply**.

### 3) Postgres
- Render → **New → PostgreSQL** (Frankfurt).
- Copie a `DATABASE_URL` e configure em **dualasset-web** e **dualasset-scraper** (Environment).

### 4) Variáveis
**Web:**
- `API_KEY`, `API_SECRET` (subconta Bybit, valores puros)
- `DATABASE_URL`
- (opcional) `APR_MIN=0.50`, `MIN_DIST_BTC=0.015`, `MIN_DIST_ETH=0.020`

**Scraper:**
- `BYBIT_COOKIES_JSON` = JSON exportado da sua sessão bybit.com (extensão Cookie-Editor → Export JSON)
- `DATABASE_URL`

### 5) Deploy
- Em cada serviço (web e scraper) clique **Manual Deploy**.
- Abra o **web**; se vier “sem ofertas”, aguarde o scraper (até 2 min).

# Bybit Dual Asset Bot – v4 (Consultivo + Postgres)

## Passo a passo rápido
1. **Suba este repositório no GitHub** (pasta inteira).
2. **Render → New → Blueprint** e aponte para o repo (o `render.yaml` cria web + worker).
3. **Crie um PostgreSQL** no Render (mesmo projeto/region) e copie a **Internal Database URL**.
4. Em **dualasset-web** e **dualasset-scraper** adicione a env **DATABASE_URL** com a Internal URL.
5. (Opcional) Adicione **API_KEY** e **API_SECRET** da Bybit para ver o saldo em *UNIFIED*.
6. Manual Deploy nos dois serviços.

O painel:
- Mostra **saldo UNIFIED** (se API estiver configurada).
- Lê a tabela **offers** (se houver dados) e mostra: tabela, scatter APR×Strike, heatmap por Tenor×Side.
- Lê **best_picks_history** para o histórico (se houver dados).

> O `scraper.py` é um placeholder. Quando quiser, eu envio a versão que coleta as ofertas reais automaticamente e grava no Postgres.

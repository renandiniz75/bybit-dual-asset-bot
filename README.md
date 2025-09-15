# Bybit Dual Asset Bot – v8 (Consultivo + Scanner de Ofertas)

Painel Streamlit consultivo para saldo da conta *Unified* e **Scanner de Melhores Ofertas** do Dual Asset (BTC/ETH).

> **Modo consultivo:** não envia ordens. Só lê saldo e consulta endpoints públicos da Bybit. Opcionalmente você pode fornecer cookies para endpoints privados (vide `.env` abaixo).

## Variáveis de ambiente necessárias
- `API_KEY` – chave API da **subconta** (Somente Leitura é suficiente para esse painel).
- `API_SECRET` – segredo da chave API.
- `MIN_APR` – (opcional) mínimo de APR anualizado para destacar/filtrar (ex.: `0.5` para 50%). Padrão: `0.5`.
- `SCAN_SYMBOLS` – (opcional) lista separada por vírgula, padrão: `BTC,ETH`.
- `SCAN_DURATIONS_DAYS` – (opcional) dias que o scanner tenta: padrão `2,3,4,7`.
- `BYBIT_COOKIES_JSON` – (opcional) JSON com cookies (string única) caso queira habilitar endpoints que exijam sessão web.

## Deploy (Render)
1. Faça upload de todos os arquivos para o seu repositório.
2. No Render, conecte o repo e deixe o `render.yaml` guiar o serviço.
3. Em **Environment**, configure as variáveis acima.
4. Deploy.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# agente-IA

Projeto completo para um agente de trading automatizado (ICT) com FastAPI, módulo adaptativo e dashboard React.

## Estrutura
```
trading_agent/
  api/              # FastAPI e schemas
  agent/            # Decision engine rule-based e bandit adaptativo
  strategy/         # Detectores ICT
  execution/        # Broker paper e gerenciador de posições
  execution/binance.py # Broker Binance Futures Testnet (ccxt)
  backtest/         # Runner de backtests
  data/             # Modelos SQLAlchemy e inicialização de banco
  services/         # WebSocket stream manager
storage/            # Estados de modelos
trading.db          # Banco SQLite padrão
dashboard/          # Front-end React + Tailwind (Vite)
```

## Backend (FastAPI)
```bash
pip install -e .[dev]
uvicorn trading_agent.api.main:app --reload
```

Endpoints principais:
- `GET /health`
- `GET/PUT /config`
- `POST /decide` para rodar rule-based ou adaptativo (`mode=adaptive`)
- `POST /execute` para enviar decisão ao broker paper
- `WS /stream` para sinais/posições em tempo real

### Testnet Binance (ccxt)
- O dashboard permite escolher `paper` / `testnet` / `live` e enviar `api_key` / `api_secret` direto para a API (`PUT /config`).
- Para testnet, escolha `execution.broker="binance_testnet"` (modo é ajustado pelo dashboard automaticamente); para live use `binance_live` (respeite `allow_live`).
- O broker usa `ccxt.binanceusdm`; em testnet usa sandbox mode, em live desabilita sandbox.
- Para backtest em modo testnet é possível informar `backtest_duration_minutes` (dashboard exibe o campo quando `testnet` é selecionado).

## Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### Servir dashboard pelo backend
```bash
cd dashboard
npm install
npm run build
cd ..
uvicorn trading_agent.api.main:app --reload
```
Quando `dashboard/dist` existir, o FastAPI serve a UI na raiz `/`.

## Backtest rápido
```python
from trading_agent.backtest.runner import Backtester
from trading_agent.strategy.detectors import Candle

candles = [Candle(timestamp=i, open=1, high=1.1, low=0.9, close=1.05, volume=10) for i in range(100)]
Backtester().run("BTCUSDT", "5m", candles)
```

## Segurança e configuração
- Secrets via `.env`
- Live trading bloqueado por feature flag no `ExecutionConfig.allow_live`
- Logs explicáveis publicados no stream `signals`

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
- Exporte credenciais de testnet: `BINANCE_API_KEY` e `BINANCE_API_SECRET`.
- Envie `PUT /config` com `execution.broker="binance_testnet"` (ou `mode="testnet"`) para trocar o broker para Binance Futures Testnet.
- O broker usa `ccxt.binanceusdm` em sandbox mode; tamanho/preço vêm do `Decision` (`symbol` e `entry`).

## Dashboard
```bash
cd dashboard
npm install
npm run dev
```

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

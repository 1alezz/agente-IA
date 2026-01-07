# Agente de Trading Automatizado com IA

Estrutura inicial para um agente de trading automatizado com IA usando conceitos ICT, integração com Binance e um dashboard web em FastAPI.

## Estrutura

- `src/agent/core/agent.py`: núcleo de decisão com confluência de sinais.
- `src/agent/strategies/`: detectores de sinais (Order Blocks, FVG, Liquidity Sweeps, RSI Divergence, etc.).
- `src/agent/rl/`: ambiente de RL (Gymnasium) e stub de treinamento PPO.
- `src/agent/dashboard/app.py`: dashboard web com endpoints de configuração e logs.

## Executar dashboard

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Acesse `http://localhost:8000` para visualizar o painel básico.

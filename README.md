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

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/main.py
```

> Observação: utilize Python 3.9–3.12 para evitar incompatibilidades com algumas dependências.

Acesse `http://localhost:8000` para visualizar o painel básico.

FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .[dev]
COPY trading_agent ./trading_agent
CMD ["uvicorn", "trading_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

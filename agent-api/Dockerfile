FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app
WORKDIR /app

RUN uv sync --frozen --no-cache
RUN uv pip install -e .

CMD ["/app/.venv/bin/uvicorn", "src.agent_api.api:app", "--port", "8080", "--host", "0.0.0.0", "--loop", "asyncio"]
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y ffmpeg libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app


RUN uv sync --frozen --no-cache
RUN uv pip install -e .

CMD ["/app/.venv/bin/python", "src/kubrick_api/api.py", "--port", "8080", "--host", "0.0.0.0"]

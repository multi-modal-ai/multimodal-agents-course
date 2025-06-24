FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install application dependencies
COPY . /app
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the FastMCP CLI
CMD ["/app/.venv/bin/fastmcp", "run", "src/kubrick_mcp/server.py", "--port", "9090", "--host", "0.0.0.0", "--transport", "streamable-http"]

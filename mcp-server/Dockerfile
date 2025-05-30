FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Install application dependencies
COPY uv.lock pyproject.toml README.md ./
RUN uv sync --frozen --no-cache

# Copy the application into the container
COPY src/sport_assistant sport_assistant/

# Run the FastAPI application using uvicorn
CMD ["/app/.venv/bin/fastapi", "run", "sport_assistant/infrastructure/api.py", "--port", "8000", "--host", "0.0.0.0"]
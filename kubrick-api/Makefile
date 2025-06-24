CHECK_DIRS := .

# --- Ruff ---

format-fix:
	uv run ruff format $(CHECK_DIRS) 
	uv run ruff check --select I --fix

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)

# --- MCP Server ---

start-agent-api: stop-agent-api
	docker build -t agent-api . && \
	docker run -d -p 8080:8080 --name agent-api --env-file .env agent-api

stop-agent-api:
	docker stop agent-api || true && \
	docker rm agent-api || true

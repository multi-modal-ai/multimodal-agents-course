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

start-kubrick-api: stop-kubrick-api
	docker build -t kubrick-api . && \
	docker run -d -p 8080:8080 --name kubrick-api --env-file .env kubrick-api

stop-kubrick-api:
	docker stop kubrick-api || true && \
	docker rm kubrick-api || true

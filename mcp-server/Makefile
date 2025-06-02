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

start-mcp-server: stop-mcp-server
	docker build -t mcp-server . && \
	docker run -d -p 8000:8000 --name mcp-server --env-file .env -v ./videos:/app/videos -v ./.pixeltable:/root/.pixeltable -v ./.records:/app/.records mcp-server

stop-mcp-server:
	docker stop mcp-server || true && \
	docker rm mcp-server || true && \
	rm -rf .pixeltable && \
	rm -rf .records

# --- FFmpeg ---

convert-video:
	ffmpeg -i $(input) -c:v libx264 -c:a copy $(output)


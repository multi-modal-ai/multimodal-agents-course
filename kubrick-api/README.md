<p align="center">
        <img alt="logo" src="static/agent_architecture.gif" width=1000 />
    <h1 align="center">⚡ Kubrick API ⚡</h1>
    <h3 align="center">A FastAPI backend for serving Kubrick’s video tools</h3>
</p>

Welcome to the Kubrick API!


This is the layer that connects it all—exposing the tools and prompts defined by Kubrick MCP and making them accessible through a clean, efficient FastAPI interface.


Kubrick API is one of three core components of the full Kubrick stack (take a peek at the [Docker Compose file](../docker-compose.yml) to see them all), and while it works best with its companions, it can also run solo if needed.


## Table of contents

- [Initial setup](#initial-setup)
- [Running the API Server](#running-the-api-server)
- [Stopping the API Server](#stopping-the-api-server)

## Initial setup

Kubrick API is built with Python and FastAPI, and uses uv for managing dependencies.


### 1. Install uv 

We’re using `uv` as our Python package manager instead of `pip` or `poetry`.

To install `uv`, simply follow this [instructions](https://docs.astral.sh/uv/getting-started/installation/). 

### 2. Set up your environment

First, create a virtual environment and install the dependencies:

```bash
uv venv .venv
# macOS / Linux
. .venv/bin/activate # or source .venv/bin/activate
# Windows
. .\.venv\Scripts\Activate.ps1 # or .\.venv\Scripts\activate
uv pip install -e .
```

Just to make sure that everything is working, simply run the following command:

```bash
 uv run python --version
```

The Python version should be `Python 3.12.8`.

### 3. Configure environment variables

You’ll need to set some environment variables. Start by copying the example file:

```
cp .env.example .env
```

Then open `.env` and fill in the required values:

```
GROQ_API_KEY=

# Set LLM_PROVIDER=minimax to use the direct MiniMax OpenAI-compatible API.
LLM_PROVIDER=groq
MINIMAX_API_KEY=
MINIMAX_REGION=global_en
MINIMAX_MODEL=MiniMax-M3.1-Flash

OPIK_API_KEY=
OPIK_PROJECT=kubrick-api
```

The default provider remains Groq. Set `LLM_PROVIDER=minimax` and provide `MINIMAX_API_KEY` to use the direct MiniMax endpoint. `MINIMAX_REGION=global_en` uses `https://api.minimax.io/v1`; `MINIMAX_REGION=cn_zh` uses `https://api.minimaxi.com/v1`. The ordinary MiniMax model choices are `MiniMax-M3.1-Flash` (default) and `MiniMax-M3`.

## Running the API Server

To start things up:

```bash
make start-kubrick-api
```

This command builds the image and spins up the FastAPI container. Once it's up, you can head to:

`http://localhost:8000/docs`

Here you'll find the interactive API docs, powered by Swagger UI. Great for exploring endpoints and testing things out quickly.

> Of course, the API will only work properly if the MCP server is running.

## Stopping the API Server

To stop the API server, run:

```bash
make stop-kubrick-api
```

This stops the container and cleans up volumes.

---

Now that this project is set up, time to go back to the [parent README.md](../README.md)! 

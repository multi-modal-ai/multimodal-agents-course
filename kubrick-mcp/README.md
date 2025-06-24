<p align="center">
        <img alt="logo" src="static/kubrick_mcp_diagram.png" width=1000 />
    <h1 align="center">🔌 Kubrick MCP 🔌</h1>
    <h3 align="center">An MCP server for serious video processing</h3>
</p>

Welcome to the Kubrick MCP server! 

This is the brains behind the scenes: generating prompts, managing resources, and handling the tools Kubrick needs to process your videos.

Kubrick MCP is one of three core components of the full Kubrick app (check out the [Docker Compose](../docker-compose.yml) file for the full stack), but it can also run on its own if needed.

## Table of contents

- [Initial setup](#initial-setup)
- [Running the MCP Server](#running-the-mcp-server)
- [Stopping the MCP Server](#stopping-the-mcp-server)

## Initial setup

Kubrick MCP is a Python project at heart, so getting it up and running locally is straightforward.


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
OPENAI_API_KEY=

OPIK_API_KEY=
OPIK_WORKSPACE=
OPIK_PROJECT=
```

The `OPENAI_API_KEY` is used for image captioning and embedding. The rest are for Opik, our tool for managing and versioning Kubrick prompts (which live in the MCP server and are accessed by the API).

## Running the MCP Server

Now that the project is set up, you can start the MCP server.

```bash
make start-kubrick-mcp
```

This will build the Docker image and run the container. If you want to interact with the server, you can use the following command:

```bash
make inspect-kubrick-mcp
```

The command will open a browser window with the MCP inspector. You can use this to test the server and see the available tools and prompts.

## Adding a video to the MCP Server

You can add your own videos to the MCP Server by adding them to the `notebooks/data` folder.

Just make sure to run this command to fix the video format (otherwise the server will not be able to process it):

```bash
make fix-video-format input=notebooks/data/video.mp4 output=notebooks/data/video_fixed.mp4
```

You can also use the video we have already added to the `notebooks/data` folder: `pass_the_butter_rick_and_morty.mp4`. 


## Understanding the MCP Server

If you want to understand what's happening under the hood, you should follow the notebook [video_ingestion_process.ipynb](notebooks/video_ingestion_process.ipynb), that details, step by step, every pixeltable operation needed to ingest a video into the MCP server.


## Stopping the MCP Server

To stop the MCP server, run:

```bash
make stop-kubrick-mcp
```

This command will stop the container and remove any volumes associated with it.

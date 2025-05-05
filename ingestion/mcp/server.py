from tools import mcp

if __name__ == "__main__":
    mcp.run(transport="sse", port=9090, host="127.0.0.1")

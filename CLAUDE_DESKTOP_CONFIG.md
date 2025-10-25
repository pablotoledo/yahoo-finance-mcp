# Claude Desktop Configuration

Add this configuration to your Claude Desktop MCP settings file:

## For STDIO Transport (Recommended for Claude Desktop)

### macOS/Linux
`~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/yahoo-finance-mcp/main.py"
      ],
      "env": {
        "YF_MCP_TRANSPORT": "stdio",
        "YF_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Replace `/absolute/path/to/yahoo-finance-mcp/` with the actual path to your installation.

## Alternative: Using the startup script

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "bash",
      "args": [
        "/absolute/path/to/yahoo-finance-mcp/run_stdio.sh"
      ]
    }
  }
}
```

## For HTTP Transport (Remote Deployment)

If running the server remotely via HTTP:

1. Start the server on your remote machine:
   ```bash
   ./run_http.sh
   ```

2. Configure Claude Desktop to connect via HTTP client (if supported by your Claude version)

## Environment Variables

You can customize the server behavior using environment variables:

- `YF_MCP_TRANSPORT`: Set to `stdio` or `http`
- `YF_MCP_LOG_LEVEL`: Set logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `YF_MCP_HTTP__HOST`: HTTP server host (default: `0.0.0.0`)
- `YF_MCP_HTTP__PORT`: HTTP server port (default: `3000`)
- `YF_MCP_HTTP__STATELESS`: Enable stateless HTTP mode (default: `false`)

## Verification

After adding the configuration:

1. Restart Claude Desktop
2. Look for "Yahoo Finance" in the MCP tools list
3. Try a simple command like: "Get the current stock price for AAPL"

## Troubleshooting

If the server doesn't appear in Claude Desktop:

1. Check the Claude Desktop logs for errors
2. Verify the path to `main.py` is correct
3. Ensure `uv` is installed and in your PATH
4. Test the server manually:
   ```bash
   cd /path/to/yahoo-finance-mcp
   ./run_stdio.sh
   ```

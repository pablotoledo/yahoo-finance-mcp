[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/alex2yang97-yahoo-finance-mcp-badge.png)](https://mseep.ai/app/alex2yang97-yahoo-finance-mcp)

# Yahoo Finance MCP Server v2.0

<div align="right">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a>
</div>

**Python SDK**: 1.19.0+ | **Protocol**: 2025-06-18

A modernized Model Context Protocol (MCP) server that provides comprehensive financial data from Yahoo Finance. This v2.0 release features structured outputs with Pydantic validation, dual transport support (STDIO + HTTP), and comprehensive testing.

## ✨ What's New in v2.0

- ✅ **MCP 1.19+ Compliance**: Upgraded to latest SDK and Protocol 2025-06-18
- ✅ **Structured Outputs**: Automatic Pydantic validation for all tool responses
- ✅ **Dual Transport**: STDIO (local) + Streamable HTTP (remote deployment)
- ✅ **Progress Reporting**: Real-time updates for long-running operations
- ✅ **Comprehensive Testing**: 75% code coverage with 68 unit tests
- ✅ **Type Safety**: Complete type hints throughout the codebase
- ✅ **Robust Error Handling**: Structured error responses with helpful suggestions
- ✅ **Production Ready**: Docker support with health checks and env-based configuration

[![smithery badge](https://smithery.ai/badge/@Alex2Yang97/yahoo-finance-mcp)](https://smithery.ai/server/@Alex2Yang97/yahoo-finance-mcp)

## Demo

![MCP Demo](assets/demo.gif)

## MCP Tools

The server exposes the following tools through the Model Context Protocol:

### Stock Information

| Tool | Description |
|------|-------------|
| `get_historical_stock_prices` | Get historical OHLCV data for a stock with customizable period and interval |
| `get_stock_info` | Get comprehensive stock data including price, metrics, and company details |
| `get_yahoo_finance_news` | Get latest news articles for a stock |
| `get_stock_actions` | Get stock dividends and splits history |

### Financial Statements

| Tool | Description |
|------|-------------|
| `get_financial_statement` | Get income statement, balance sheet, or cash flow statement (annual/quarterly) |
| `get_holder_info` | Get major holders, institutional holders, mutual funds, or insider transactions |

### Options Data

| Tool | Description |
|------|-------------|
| `get_option_expiration_dates` | Get available options expiration dates |
| `get_option_chain` | Get options chain for a specific expiration date and type (calls/puts) |

### Analyst Information

| Tool | Description |
|------|-------------|
| `get_recommendations` | Get analyst recommendations or upgrades/downgrades history |

## Real-World Use Cases

With this MCP server, you can use Claude to:

### Stock Analysis

- **Price Analysis**: "Show me the historical stock prices for AAPL over the last 6 months with daily intervals."
- **Financial Health**: "Get the quarterly balance sheet for Microsoft."
- **Performance Metrics**: "What are the key financial metrics for Tesla from the stock info?"
- **Trend Analysis**: "Compare the quarterly income statements of Amazon and Google."
- **Cash Flow Analysis**: "Show me the annual cash flow statement for NVIDIA."

### Market Research

- **News Analysis**: "Get the latest news articles about Meta Platforms."
- **Institutional Activity**: "Show me the institutional holders of Apple stock."
- **Insider Trading**: "What are the recent insider transactions for Tesla?"
- **Options Analysis**: "Get the options chain for SPY with expiration date 2024-06-21 for calls."
- **Analyst Coverage**: "What are the analyst recommendations for Amazon over the last 3 months?"

### Investment Research

- "Create a comprehensive analysis of Microsoft's financial health using their latest quarterly financial statements."
- "Compare the dividend history and stock splits of Coca-Cola and PepsiCo."
- "Analyze the institutional ownership changes in Tesla over the past year."
- "Generate a report on the options market activity for Apple stock with expiration in 30 days."
- "Summarize the latest analyst upgrades and downgrades in the tech sector over the last 6 months."

## Requirements

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip for package management
- Dependencies as listed in `pyproject.toml`:
  - `mcp[cli]>=1.19.0` - MCP Python SDK (latest)
  - `yfinance>=0.2.66` - Yahoo Finance API wrapper
  - `pydantic>=2.12.3` - Data validation
  - `pydantic-settings>=2.11.0` - Configuration management
  - `pandas>=2.0` - Data processing

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/Alex2Yang97/yahoo-finance-mcp.git
cd yahoo-finance-mcp

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 2. Run in Development Mode

Test the server with MCP Inspector:

```bash
# STDIO mode (default)
uv run mcp dev src/server.py

# Or directly
uv run python main.py
```

## 🚀 Running the Server

### STDIO Mode (Local/Claude Desktop)

For use with Claude Desktop or other local MCP clients:

**Option 1: Using helper script**
```bash
chmod +x run_stdio.sh
./run_stdio.sh
```

**Option 2: Using environment variables**
```bash
export YF_MCP_TRANSPORT=stdio
export YF_MCP_LOG_LEVEL=INFO
uv run python main.py
```

**Option 3: With MCP Inspector (development)**
```bash
uv run mcp dev src/server.py
```

### HTTP Mode (Remote Deployment)

For deployment as a web service accessible to remote clients:

**Option 1: Using helper script**
```bash
chmod +x run_http.sh
./run_http.sh
```

**Option 2: Using environment variables**
```bash
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__HOST=0.0.0.0
export YF_MCP_HTTP__PORT=3000
export YF_MCP_LOG_LEVEL=INFO
uv run python main.py
```

**Option 3: With Docker Compose**
```bash
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables

Configure the server using environment variables (all prefixed with `YF_MCP_`):

| Variable | Values | Default | Description |
|----------|---------|---------|-------------|
| `YF_MCP_TRANSPORT` | `stdio`, `http` | `stdio` | Transport type |
| `YF_MCP_HTTP__HOST` | IP/hostname | `0.0.0.0` | HTTP server host (HTTP mode only) |
| `YF_MCP_HTTP__PORT` | 1024-65535 | `3000` | HTTP server port (HTTP mode only) |
| `YF_MCP_HTTP__STATELESS` | `true`, `false` | `false` | Stateless mode (no session state) |
| `YF_MCP_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | Logging level |

**Example `.env` file:**
```bash
# Transport Configuration
YF_MCP_TRANSPORT=http

# HTTP Configuration (nested with __)
YF_MCP_HTTP__HOST=0.0.0.0
YF_MCP_HTTP__PORT=3000
YF_MCP_HTTP__STATELESS=false

# Logging
YF_MCP_LOG_LEVEL=INFO
```

### Integration with Claude for Desktop

To integrate this server with Claude for Desktop:

1. Install [Claude for Desktop](https://claude.ai/download) on your local machine
2. Open the Claude Desktop configuration file:
   - **macOS**: `code ~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - **Windows**: `code $env:AppData\Claude\claude_desktop_config.json`

3. Add the server configuration:

   **macOS:**
   ```json
   {
     "mcpServers": {
       "yfinance": {
         "command": "uv",
         "args": [
           "--directory",
           "/ABSOLUTE/PATH/TO/PARENT/FOLDER/yahoo-finance-mcp",
           "run",
           "python",
           "main.py"
         ],
         "env": {
           "YF_MCP_TRANSPORT": "stdio",
           "YF_MCP_LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

   **Windows:**
   ```json
   {
     "mcpServers": {
       "yfinance": {
         "command": "uv",
         "args": [
           "--directory",
           "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\yahoo-finance-mcp",
           "run",
           "python",
           "main.py"
         ],
         "env": {
           "YF_MCP_TRANSPORT": "stdio",
           "YF_MCP_LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

   > **Note**: Replace `/ABSOLUTE/PATH/TO/PARENT/FOLDER/yahoo-finance-mcp` with the actual path to your installation. You may need to use the full path to the `uv` executable (find it with `which uv` on macOS/Linux or `where uv` on Windows).

4. Restart Claude for Desktop

The server will now be available in Claude Desktop. Look for the 🔌 icon to confirm the connection.

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_tools.py

# Run specific test
uv run pytest tests/test_tools.py::TestGetHistoricalStockPrices::test_valid_ticker_returns_data -v

# Verbose output
uv run pytest -vv

# Watch mode (requires pytest-watch)
uv run ptw
```

**Test Statistics:**
- **68 tests** implemented (ALL PASSING ✅)
- **75% code coverage** achieved
- **Fast execution**: ~1.2 seconds for full suite
- **No API dependencies**: All yfinance calls mocked

## 📖 Migration from v1.x

If you're upgrading from v1.x, see the [Migration Guide](MIGRATION_GUIDE.md) for detailed instructions.

**Key Changes:**
- Entry point changed: `server.py` → `main.py`
- All tools now return structured Pydantic models
- Claude Desktop config requires `env` parameter
- Error responses are now structured with helpful suggestions

**Quick Migration:**
```json
// OLD (v1.x)
{
  "command": "uv",
  "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "server.py"]
}

// NEW (v2.0)
{
  "command": "uv",
  "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "python", "main.py"],
  "env": {"YF_MCP_TRANSPORT": "stdio"}
}
```

## License

MIT

## 📚 Additional Resources

- [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Detailed migration instructions from v1.x
- [MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md) - Complete modernization plan and architecture
- [Phase Documentation](.) - Detailed phase-by-phase implementation docs
- [MCP Specification](https://spec.modelcontextprotocol.io) - Official MCP protocol documentation
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Python SDK repository

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 Support

If you encounter any issues or have questions:
1. Check the [Migration Guide](MIGRATION_GUIDE.md) if upgrading from v1.x
2. Review the [Phase Documentation](.) for implementation details
3. Open an issue on GitHub with detailed information

---

**Maintained by**: [@Alex2Yang97](https://github.com/Alex2Yang97)  
**Modernized by**: AI Assistant (Claude) following MCP best practices  
**Version**: 2.0.0

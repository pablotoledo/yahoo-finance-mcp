# Yahoo Finance MCP Server

A Model Context Protocol (MCP) server providing comprehensive financial data from Yahoo Finance. Access real-time stock prices, financial statements, options data, and analyst recommendations through a standardized interface.

## Features

- **9 Financial Tools**: Historical prices, stock info, news, financials, options, analyst recommendations
- **Dual Transport**: STDIO (local) and HTTP (remote) support
- **No API Key Required**: Uses free Yahoo Finance data
- **Type-Safe**: Pydantic-validated responses
- **Production Ready**: Docker support, comprehensive testing (75% coverage)
- **Latest MCP SDK**: Built with MCP SDK 1.19.0+ and Protocol 2025-06-18

## Available Tools

### Stock Information

| Tool | Description |
|------|-------------|
| `get_historical_stock_prices` | Historical OHLCV data with customizable period/interval |
| `get_stock_info` | Comprehensive real-time stock data, metrics, and ratios |
| `get_yahoo_finance_news` | Latest news articles and headlines |
| `get_stock_actions` | Dividend payments and stock splits history |

### Financial Statements

| Tool | Description |
|------|-------------|
| `get_financial_statement` | Income statement, balance sheet, or cash flow (annual/quarterly) |
| `get_holder_info` | Institutional holders, mutual funds, insiders, and transactions |

### Options Data

| Tool | Description |
|------|-------------|
| `get_option_expiration_dates` | Available options contract expiration dates |
| `get_option_chain` | Detailed options chain (calls/puts) with Greeks and premiums |

### Analyst Information

| Tool | Description |
|------|-------------|
| `get_recommendations` | Analyst ratings, upgrades/downgrades history |

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 16+ (for MCP Inspector testing, optional)
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone repository
git clone https://github.com/pablotoledo/yahoo-finance-mcp.git
cd yahoo-finance-mcp

# Install with uv (recommended)
uv sync

# OR with pip
pip install -e .
```

### Running the Server

**STDIO Mode** (for Claude Desktop, Cline, etc.):

```bash
export YF_MCP_TRANSPORT=stdio
uv run python main.py
```

**HTTP Mode** (for web/remote access):

```bash
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3001
uv run python main.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Using Docker

```bash
# Build image
docker build -t yahoo-finance-mcp .

# Run container
docker run -d \
  -p 3001:3001 \
  -e YF_MCP_TRANSPORT=http \
  -e YF_MCP_HTTP__PORT=3001 \
  --name yfinance-mcp \
  yahoo-finance-mcp
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `YF_MCP_TRANSPORT` | `stdio` | Transport protocol (`stdio` or `http`) |
| `YF_MCP_HTTP__HOST` | `0.0.0.0` | HTTP server bind address |
| `YF_MCP_HTTP__PORT` | `3000` | HTTP server port |
| `YF_MCP_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Example .env File

```bash
YF_MCP_TRANSPORT=http
YF_MCP_HTTP__PORT=3001
YF_MCP_LOG_LEVEL=INFO
```

## Claude Desktop Integration

1. **Open Configuration File**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add Server Configuration**:

   ```json
   {
     "mcpServers": {
       "yahoo-finance": {
         "command": "uv",
         "args": [
           "--directory",
           "/ABSOLUTE/PATH/TO/yahoo-finance-mcp",
           "run",
           "python",
           "main.py"
         ],
         "env": {
           "YF_MCP_TRANSPORT": "stdio"
         }
       }
     }
   }
   ```

   > **Important**: Replace `/ABSOLUTE/PATH/TO/yahoo-finance-mcp` with your actual installation path.

3. **Restart Claude Desktop**

## Testing

### Run Tests

```bash
# All tests
uv run pytest

# With coverage report
uv run pytest --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_tools.py
```

### Test with MCP Inspector

```bash
# Start server in HTTP mode
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3001
uv run python main.py

# In another terminal, start MCP Inspector
npx @modelcontextprotocol/inspector
# Configure: Streamable HTTP, http://localhost:3001/mcp
```

## Usage Examples

### Stock Analysis

**Get Historical Prices**:
> "Show me AAPL's historical prices for the last 6 months with daily intervals"

**Analyze Financial Health**:
> "Get Microsoft's latest quarterly balance sheet"

**Check Key Metrics**:
> "What are Tesla's key financial ratios?"

### Market Research

**Latest News**:
> "Get the latest news about Meta"

**Institutional Holdings**:
> "Show me Apple's institutional holders"

**Options Analysis**:
> "Get SPY options chain for the next monthly expiration"

## Development

### Project Structure

```
yahoo-finance-mcp/
├── src/
│   ├── server.py              # Main MCP server with tools
│   ├── config/                # Configuration management
│   └── models/                # Pydantic response models
├── tests/                     # Unit tests
├── main.py                    # Entry point
├── pyproject.toml             # Dependencies and metadata
└── docker-compose.yml         # Docker orchestration
```

### Code Quality

```bash
# Run all checks
uv run pytest && uv run mypy src/ && uv run ruff check src/
```

## Troubleshooting

**Port already in use**:
```bash
lsof -ti:3001 | xargs kill -9
```

**Module not found**:
```bash
uv sync --reinstall
```

**Claude Desktop not connecting**:
- Verify absolute path in `claude_desktop_config.json`
- Check `uv` is in PATH: `which uv`
- Restart Claude Desktop after config changes

**Debug logging**:
```bash
export YF_MCP_LOG_LEVEL=DEBUG
uv run python main.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add tests for new features
5. Update documentation
6. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original Author: [@Alex2Yang97](https://github.com/Alex2Yang97)
- MCP Team for the protocol and SDK
- Yahoo Finance for providing free financial data

## Support

- **Issues**: [GitHub Issues](https://github.com/pablotoledo/yahoo-finance-mcp/issues)
- **Documentation**: [MCP Specification](https://modelcontextprotocol.io)

---

Made with ❤️ using [MCP](https://modelcontextprotocol.io)

# Yahoo Finance MCP Server

A production-ready Model Context Protocol (MCP) server providing comprehensive financial data from Yahoo Finance. Built with the latest MCP SDK (1.19.0+) and Protocol 2025-06-18, featuring structured outputs, dual transport support, and 100% Phase 6 compliance with Field() parameter documentation.

## 🌟 Key Features

- ✅ **MCP Protocol 2025-06-18**: Latest specification compliance
- ✅ **Field() Documentation**: All 18 parameters documented with examples and descriptions
- ✅ **Structured Outputs**: Pydantic-validated responses for type safety
- ✅ **Dual Transport**: STDIO (local) + Streamable HTTP (remote/web)
- ✅ **Production Ready**: Docker support, comprehensive testing (75% coverage)
- ✅ **9 Financial Tools**: Stock data, news, financials, options, analyst recommendations
- ✅ **MCP Inspector Compatible**: Full UI parameter descriptions visible
- ✅ **Zero API Key Required**: Uses free Yahoo Finance data

## 📊 What's New - Phase 6 Complete

**Phase 6: Tool Docstring Refactoring** ✅ COMPLETE

All 9 tools now follow MCP best practices with \`Field(description=...)\` for every parameter:

\`\`\`python
# Example: get_historical_stock_prices
async def get_historical_stock_prices(
    ticker: str = Field(description="Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'TSLA')"),
    period: str = Field(description="Time period: '1d'=1 day, '1mo'=1 month, '1y'=1 year..."),
    interval: str = Field(description="Data granularity: '1m'=1 min, '1h'=1 hour, '1d'=1 day...")
) -> HistoricalPriceResponse | TickerValidationError:
    """Get historical OHLCV stock price data for analysis and charting."""
\`\`\`

**Benefits:**
- 🤖 LLMs receive parameter descriptions in inputSchema (300% more context)
- 🎯 Examples guide valid inputs ('AAPL', 'MSFT', 'TSLA')
- �� MCP Inspector shows descriptions as placeholders
- ✨ Self-documenting API - no external docs needed

**Testing:**
- ✅ STDIO: 8/9 tools tested (88.9% success) - [Results](PHASE6_TEST_RESULTS.md)
- ✅ HTTP: Validated with MCP Inspector + Playwright - [Results](HTTP_INSPECTOR_TEST_RESULTS.md)
- ✅ Docker: Verified build and docker-compose deployment

**Documentation:**
- [TOOL_DOCSTRING_BEST_PRACTICES.md](TOOL_DOCSTRING_BEST_PRACTICES.md) - MCP guidelines (400+ lines)
- [PHASE6_TOOL_DOCSTRINGS.md](PHASE6_TOOL_DOCSTRINGS.md) - Complete changelog (300+ lines)
- [PHASE6_TEST_RESULTS.md](PHASE6_TEST_RESULTS.md) - STDIO test results (400+ lines)
- [HTTP_INSPECTOR_TEST_RESULTS.md](HTTP_INSPECTOR_TEST_RESULTS.md) - HTTP test results (430+ lines)

## 🛠️ Available Tools

### Stock Information

| Tool | Description | Example Parameters |
|------|-------------|-------------------|
| \`get_historical_stock_prices\` | Historical OHLCV data with customizable period/interval | ticker: "AAPL", period: "1mo", interval: "1d" |
| \`get_stock_info\` | Comprehensive real-time stock data, metrics, ratios | ticker: "MSFT" |
| \`get_yahoo_finance_news\` | Latest news articles and headlines | ticker: "TSLA" |
| \`get_stock_actions\` | Dividend payments and stock splits history | ticker: "AAPL" |

### Financial Statements

| Tool | Description | Example Parameters |
|------|-------------|-------------------|
| \`get_financial_statement\` | Income statement, balance sheet, or cash flow (annual/quarterly) | ticker: "AAPL", financial_type: "income_stmt" |
| \`get_holder_info\` | Institutional holders, mutual funds, insiders, transactions | ticker: "AAPL", holder_type: "major_holders" |

### Options Data

| Tool | Description | Example Parameters |
|------|-------------|-------------------|
| \`get_option_expiration_dates\` | Available options contract expiration dates | ticker: "AAPL" |
| \`get_option_chain\` | Detailed options chain (calls/puts) with Greeks and premiums | ticker: "AAPL", expiration_date: "2024-12-20", option_type: "calls" |

### Analyst Information

| Tool | Description | Example Parameters |
|------|-------------|-------------------|
| \`get_recommendations\` | Analyst ratings, upgrades/downgrades history | ticker: "AAPL", recommendation_type: "recommendations", months_back: 3 |

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Required)
- **[uv](https://docs.astral.sh/uv/)** (Recommended) or pip
- **Node.js 16+** (For MCP Inspector testing)
- **Docker** (Optional, for containerized deployment)

### Installation

\`\`\`bash
# Clone repository
git clone https://github.com/pablotoledo/yahoo-finance-mcp.git
cd yahoo-finance-mcp

# Install with uv (recommended)
uv sync

# OR with pip
pip install -e .
\`\`\`

### Run Locally

**STDIO Mode** (for Claude Desktop, Cline, etc.):

\`\`\`bash
# Using helper script
chmod +x run_stdio.sh
./run_stdio.sh

# OR with environment variables
export YF_MCP_TRANSPORT=stdio
export YF_MCP_LOG_LEVEL=INFO
uv run python main.py
\`\`\`

**HTTP Mode** (for web/remote access):

\`\`\`bash
# Using helper script
chmod +x run_http.sh
./run_http.sh

# OR with environment variables
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3001
export YF_MCP_LOG_LEVEL=INFO
uv run python main.py
\`\`\`

### Test with MCP Inspector

\`\`\`bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector

# Then in Inspector UI:
# - Transport: Streamable HTTP
# - URL: http://localhost:3001/mcp
# - Click Connect
# - Go to Tools tab → List Tools
\`\`\`

## 🐳 Docker Deployment

### Docker Compose (Recommended)

\`\`\`bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop service
docker-compose down
\`\`\`

**Configuration**: Edit \`docker-compose.yml\` to change port or environment variables.

### Docker Build

\`\`\`bash
# Build image
docker build -t yahoo-finance-mcp .

# Run container
docker run -d \\
  -p 3001:3001 \\
  -e YF_MCP_TRANSPORT=http \\
  -e YF_MCP_HTTP__PORT=3001 \\
  -e YF_MCP_LOG_LEVEL=INFO \\
  --name yfinance-mcp \\
  yahoo-finance-mcp

# View logs
docker logs -f yfinance-mcp

# Stop container
docker stop yfinance-mcp
docker rm yfinance-mcp
\`\`\`

## ⚙️ Configuration

### Environment Variables

All variables use the \`YF_MCP_\` prefix:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| \`YF_MCP_TRANSPORT\` | \`stdio\` \\| \`http\` | \`stdio\` | Transport protocol |
| \`YF_MCP_HTTP__HOST\` | string | \`0.0.0.0\` | HTTP server bind address |
| \`YF_MCP_HTTP__PORT\` | int (1024-65535) | \`3000\` | HTTP server port |
| \`YF_MCP_HTTP__STATELESS\` | bool | \`false\` | Stateless mode (no sessions) |
| \`YF_MCP_HTTP__CORS_ORIGINS\` | list[str] | \`["*"]\` | CORS allowed origins |
| \`YF_MCP_LOG_LEVEL\` | \`DEBUG\` \\| \`INFO\` \\| \`WARNING\` \\| \`ERROR\` | \`INFO\` | Logging verbosity |

### Example \`.env\` File

\`\`\`bash
# Transport
YF_MCP_TRANSPORT=http

# HTTP Configuration (use __ for nested)
YF_MCP_HTTP__HOST=0.0.0.0
YF_MCP_HTTP__PORT=3001
YF_MCP_HTTP__STATELESS=false
YF_MCP_HTTP__CORS_ORIGINS=["*"]

# Logging
YF_MCP_LOG_LEVEL=INFO
\`\`\`

## 🔗 Integration with Claude Desktop

1. **Install Claude Desktop**: [Download](https://claude.ai/download)

2. **Open Configuration File**:
   - **macOS**: \`~/Library/Application Support/Claude/claude_desktop_config.json\`
   - **Windows**: \`%APPDATA%\\Claude\\claude_desktop_config.json\`
   - **Linux**: \`~/.config/Claude/claude_desktop_config.json\`

3. **Add Server Configuration**:

   \`\`\`json
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
           "YF_MCP_TRANSPORT": "stdio",
           "YF_MCP_LOG_LEVEL": "INFO"
         }
       }
     }
   }
   \`\`\`

   > **Important**: Replace \`/ABSOLUTE/PATH/TO/yahoo-finance-mcp\` with your actual installation path.
   >
   > **Windows**: Use double backslashes: \`C:\\\\Users\\\\YourName\\\\yahoo-finance-mcp\`

4. **Restart Claude Desktop**

5. **Verify Connection**: Look for the 🔌 icon indicating MCP server connection.

## 🧪 Testing

### Run Test Suite

\`\`\`bash
# All tests (68 tests, 75% coverage)
uv run pytest

# With coverage report
uv run pytest --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_tools.py

# Specific test function
uv run pytest tests/test_tools.py::TestGetHistoricalStockPrices::test_valid_ticker -v

# Verbose output
uv run pytest -vv
\`\`\`

### Test Statistics

- ✅ **68 unit tests** - All passing
- ✅ **75% code coverage** - High reliability
- ✅ **~1.2 seconds** - Fast execution
- ✅ **No API calls** - All mocked for speed

### Manual Testing

**STDIO Transport**:
\`\`\`bash
# Run comprehensive test suite
uv run python test_stdio_comprehensive.py
\`\`\`

**HTTP Transport**:
\`\`\`bash
# Start server
./run_http.sh

# In another terminal, use MCP Inspector
npx @modelcontextprotocol/inspector
# Configure: Streamable HTTP, http://localhost:3001/mcp
\`\`\`

## 📖 Use Cases & Examples

### Stock Analysis with Claude

**Price History**:
> "Show me AAPL's historical prices for the last 6 months with daily intervals"

**Financial Health**:
> "Get Microsoft's latest quarterly balance sheet and analyze their financial position"

**Performance Metrics**:
> "What are Tesla's key financial ratios from the stock info?"

### Market Research

**News Analysis**:
> "Get the latest news about Meta and summarize the sentiment"

**Institutional Activity**:
> "Show me Apple's institutional holders and calculate ownership concentration"

**Options Strategy**:
> "Get SPY options chain for the next monthly expiration and identify profitable spreads"

### Investment Research

**Comprehensive Analysis**:
> "Create a detailed report on NVDA including: historical prices (1 year), latest financials, institutional ownership, and analyst recommendations"

**Dividend Strategy**:
> "Compare dividend history for KO and PEP over the last 5 years"

**Sector Analysis**:
> "Get analyst upgrades and downgrades for AAPL, MSFT, GOOGL, and AMZN over the last 6 months"

## 📚 Documentation

### Phase Documentation

- **[TOOL_DOCSTRING_BEST_PRACTICES.md](TOOL_DOCSTRING_BEST_PRACTICES.md)** - MCP Field() documentation guide
- **[PHASE6_TOOL_DOCSTRINGS.md](PHASE6_TOOL_DOCSTRINGS.md)** - Phase 6 implementation details
- **[PHASE6_TEST_RESULTS.md](PHASE6_TEST_RESULTS.md)** - STDIO transport test results
- **[HTTP_INSPECTOR_TEST_RESULTS.md](HTTP_INSPECTOR_TEST_RESULTS.md)** - HTTP transport validation
- **[MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md)** - Complete modernization roadmap

### Legacy Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrading from v1.x

### External Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18) - Official protocol docs
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - SDK repository
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Testing tool
- [FastMCP](https://github.com/jlowin/fastmcp) - Framework documentation

## 🔧 Development

### Project Structure

\`\`\`
yahoo-finance-mcp/
├── src/
│   ├── server.py              # Main MCP server with 9 tools
│   ├── config/                # Configuration management
│   │   ├── settings.py        # Pydantic settings with env support
│   │   └── __init__.py
│   └── models/                # Pydantic response models
│       ├── stock_models.py    # Stock data models
│       ├── financial_models.py # Financial statement models
│       └── ...
├── tests/                     # Unit tests (68 tests, 75% coverage)
├── main.py                    # Entry point
├── pyproject.toml             # Dependencies and project metadata
├── Dockerfile                 # Docker build configuration
├── docker-compose.yml         # Docker Compose orchestration
├── run_stdio.sh               # STDIO mode helper script
├── run_http.sh                # HTTP mode helper script
└── test_stdio_comprehensive.py # Manual STDIO test suite
\`\`\`

### Adding a New Tool

1. **Define Pydantic Models** in \`src/models/\`:
   \`\`\`python
   class YourResponse(BaseModel):
       """Response model with Field() descriptions."""
       field: str = Field(description="Clear description with examples")
   \`\`\`

2. **Create Tool Function** in \`src/server.py\`:
   \`\`\`python
   @mcp.tool(name="your_tool", description="Clear one-line description")
   async def your_tool(
       param: str = Field(description="Parameter with examples (e.g., 'example')"),
       ctx: Context | None = None
   ) -> YourResponse | TickerValidationError:
       """
       Tool purpose in 1-2 lines.
       Include use case and practical application.
       """
       # Implementation
   \`\`\`

3. **Add Tests** in \`tests/\`:
   \`\`\`python
   class TestYourTool:
       async def test_valid_input(self):
           # Test successful case
       
       async def test_invalid_input(self):
           # Test error handling
   \`\`\`

4. **Update Documentation**: Add to this README's tool table

### Code Quality

\`\`\`bash
# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Formatting
uv run black src/

# All checks
uv run pytest && uv run mypy src/ && uv run ruff check src/
\`\`\`

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Port already in use"
\`\`\`bash
# Find and kill process using port 3001
lsof -ti:3001 | xargs kill -9
\`\`\`

**Issue**: "Module not found: mcp"
\`\`\`bash
# Reinstall dependencies
uv sync --reinstall
\`\`\`

**Issue**: "Docker container unhealthy"
\`\`\`bash
# Check logs
docker-compose logs -f

# Verify port accessibility
curl -v http://localhost:3001/mcp
\`\`\`

**Issue**: "Claude Desktop not connecting"
- Verify absolute path in \`claude_desktop_config.json\`
- Check \`uv\` is in PATH: \`which uv\` (macOS/Linux) or \`where uv\` (Windows)
- Restart Claude Desktop after config changes
- Check logs in Claude Desktop settings

### Debug Mode

\`\`\`bash
# Enable debug logging
export YF_MCP_LOG_LEVEL=DEBUG
uv run python main.py
\`\`\`

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Follow existing code style (use \`black\`, \`ruff\`, \`mypy\`)
4. Add tests for new features
5. Update documentation
6. Commit with clear messages
7. Push and create a Pull Request

### Development Workflow

\`\`\`bash
# Setup
git clone https://github.com/pablotoledo/yahoo-finance-mcp.git
cd yahoo-finance-mcp
uv sync

# Make changes
# ...

# Test
uv run pytest
uv run mypy src/

# Commit
git add .
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature
\`\`\`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Author**: [@Alex2Yang97](https://github.com/Alex2Yang97)
- **Phase 6 Modernization**: Collaborative AI-assisted development
- **MCP Team**: For the excellent protocol and SDK
- **Yahoo Finance**: For providing free financial data

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pablotoledo/yahoo-finance-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pablotoledo/yahoo-finance-mcp/discussions)
- **Documentation**: See [📚 Documentation](#-documentation) section above

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ using [MCP](https://modelcontextprotocol.io)

</div>

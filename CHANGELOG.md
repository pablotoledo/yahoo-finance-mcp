# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-25

### Added

#### Core Functionality
- **Python SDK 1.19+ Support**: Upgraded from SDK 1.6.0 to 1.19.0 (Oct 24, 2025 release)
- **Protocol 2025-06-18**: Implements current stable MCP protocol specification
- **Dual Transport System**: Support for both STDIO (local) and Streamable HTTP (remote)
- **Structured Outputs**: Pydantic models for all tool responses with automatic validation
  - `HistoricalPricePoint` - Historical price data with proper types
  - `StockInfoResponse` - Comprehensive stock information
  - `NewsArticle` / `NewsListResponse` - News data structures
  - `StockActionsResponse` - Dividends and splits
  - `FinancialStatementResponse` - Income, balance sheet, cash flow
  - `HolderInfoResponse` - Holder information (major, institutional, etc.)
  - `OptionExpirationDatesResponse` / `OptionChainResponse` - Options data
  - `RecommendationsResponse` - Analyst recommendations
  - `TickerValidationError` - Structured error responses

#### Infrastructure
- **Lifespan Management**: Proper startup/shutdown handling with `asynccontextmanager`
- **Configuration System**: Environment-based config with `pydantic-settings`
  - `ServerConfig` - Main configuration model
  - `HTTPConfig` - HTTP transport settings
  - `TransportType` enum for type-safe transport selection
  - Support for nested environment variables (e.g., `YF_MCP_HTTP__PORT`)
- **Context API**: Structured logging with `await ctx.info()`, `await ctx.error()`, `await ctx.debug()`
- **Progress Reporting**: Real-time progress updates for long operations (`await ctx.report_progress()`)

#### Testing & Quality
- **Comprehensive Test Suite**: 68 unit tests with 75% code coverage
  - `tests/conftest.py` - Shared fixtures and mocks (195 lines)
  - `tests/test_tools.py` - Tool tests (347 lines, 23 tests)
  - `tests/test_models.py` - Model validation tests (328 lines, 25 tests)
  - `tests/test_config.py` - Configuration tests (186 lines, 20 tests)
- **Mock Strategy**: All yfinance calls mocked to avoid API rate limits
- **Fast Execution**: Full test suite runs in ~1.2 seconds
- **pytest Configuration**: Async support, coverage reporting, strict markers

#### Deployment
- **Docker Support**: Updated Dockerfile with health checks
- **docker-compose.yml**: HTTP deployment with environment configuration
- **Startup Scripts**: `run_stdio.sh` and `run_http.sh` for easy server startup
- **Health Checks**: HTTP endpoint monitoring for production deployments

#### Documentation
- **Migration Guide**: Comprehensive guide for v1.x → v2.0 upgrade
- **Phase Documentation**: Detailed phase-by-phase implementation docs
  - `PHASE0_BASELINE.md` - Baseline documentation
  - `PHASE1_AUDIT.md` - Dependency audit and preparation
  - `PHASE2_CORE_MODERNIZATION.md` - Core MCP modernization
  - `PHASE3_DUAL_TRANSPORT.md` - Dual transport implementation
  - `PHASE4_COMPREHENSIVE_TESTS.md` - Testing strategy and results
  - `PHASE5_DOCUMENTATION_FINAL.md` - Final improvements
- **Updated README**: New sections for features, deployment, testing, migration
- **CHANGELOG.md**: This file, following Keep a Changelog format
- **Configuration Example**: `.env.example` with all available settings

### Changed

#### Breaking Changes
- **Entry Point**: Changed from `server.py` to `main.py`
  - Old: `uv run server.py`
  - New: `uv run python main.py`
  - Rationale: Clearer separation between server implementation and entry point
- **Tool Responses**: All tools now return structured Pydantic models
  - Backward compatible: Text content still included alongside structured data
  - Clients supporting structured outputs get validated, typed responses
- **Claude Desktop Configuration**: Now requires `env` parameter for configuration
  ```json
  {
    "env": {
      "YF_MCP_TRANSPORT": "stdio",
      "YF_MCP_LOG_LEVEL": "INFO"
    }
  }
  ```

#### Improvements
- **Error Handling**: Typed `TickerValidationError` model with helpful suggestions
  - Before: Plain text error messages
  - After: Structured errors with `error`, `ticker`, and `suggestion` fields
- **Logging**: Structured logging using MCP Context API
  - Before: `print()` statements to console
  - After: `await ctx.info()`, `await ctx.error()`, `await ctx.debug()`
- **Type Safety**: Complete type hints throughout codebase
  - All functions have parameter and return type annotations
  - Pydantic models ensure runtime type validation
- **Configuration**: Environment-based configuration replaces hardcoded values
  - Transport type, HTTP settings, log level all configurable via env vars
  - Validation ensures configuration correctness at startup
- **Docker Deployment**: Enhanced with health checks and proper signal handling
- **HTTP Transport**: Modernized to use Streamable HTTP (SSE deprecated)
  - CORS configuration for browser-based clients
  - Stateless and stateful modes supported
  - Proper session management

#### Dependencies
- **MCP SDK**: Upgraded from 1.6.0 to 1.19.0
  - Protocol version: 2025-06-18
  - FastMCP for simplified server creation
  - Context API for structured logging
- **yfinance**: Upgraded from 0.2.62 to 0.2.66
  - Bug fixes for intraday prices
  - Enhanced screener support
  - Better exception handling
- **Pydantic**: Added explicit dependency (≥2.12.3)
  - Previously transitive via other packages
  - Now used throughout for data validation
- **pydantic-settings**: Added for configuration management (≥2.11.0)
- **Development Dependencies**: Added comprehensive testing tools
  - pytest 8.4.2 - Testing framework
  - pytest-asyncio 1.2.0 - Async test support
  - pytest-cov 7.0.0 - Coverage reporting
  - pytest-mock 3.15.1 - Mocking support
  - pytest-httpx 0.35.0 - HTTP testing
  - ruff 0.14.2 - Modern linter (replaces flake8, black, isort)

### Deprecated
- **Direct execution of `server.py`**: Use `main.py` instead
  - `server.py` still exists but renamed to `src/server.py` in the new structure
  - Direct execution not recommended; use `main.py` entry point
- **SSE Transport**: Replaced by Streamable HTTP in MCP specification
  - SSE still supported by SDK but not recommended for new implementations

### Fixed
- **Rate Limiting**: Mock strategy in tests avoids yfinance API rate limits
- **Type Validation**: Proper Pydantic validation catches type errors early
- **Error Messages**: Clear, actionable error messages with suggestions
- **DataFrame Handling**: Proper index management in historical price data
- **Holder Data**: Accepts both dict and list formats from yfinance API
- **Async Context**: Proper `await` on all async context methods

### Security
- **Type Safety**: Pydantic validation prevents malformed data
- **Input Validation**: All tool parameters validated before processing
- **Error Isolation**: Structured error handling prevents information leakage
- **CORS Configuration**: Configurable CORS settings for HTTP transport

## [1.0.0] - 2024-XX-XX

### Added
- Initial release with MCP 1.6.0 support
- Basic tools for Yahoo Finance data retrieval:
  - `get_historical_stock_prices` - Historical OHLCV data
  - `get_stock_info` - Company information and metrics
  - `get_yahoo_finance_news` - Latest news articles
  - `get_stock_actions` - Dividends and stock splits
  - `get_financial_statement` - Financial statements (income, balance sheet, cash flow)
  - `get_holder_info` - Holder information (major, institutional, mutual funds, insiders)
  - `get_option_expiration_dates` - Options expiration dates
  - `get_option_chain` - Options chain data (calls/puts)
  - `get_recommendations` - Analyst recommendations and upgrades/downgrades
- STDIO transport for local use (Claude Desktop)
- Basic yfinance integration
- README with usage examples
- MIT License

### Known Limitations (v1.0)
- Single transport mode (STDIO only)
- Plain text responses (no structured outputs)
- Limited error handling
- No tests
- Hardcoded configuration
- Console logging with `print()`
- No type hints
- No validation of responses

---

## Migration Guide

For detailed migration instructions from v1.x to v2.0, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

**Quick Summary:**
1. Update Claude Desktop config to use `main.py` and add `env` parameter
2. Update dependencies: `uv sync --upgrade`
3. Expect structured responses from all tools (backward compatible)
4. Use environment variables for configuration (e.g., `YF_MCP_TRANSPORT`)
5. Test the new setup: `uv run pytest`

---

## Links

- **Repository**: https://github.com/Alex2Yang97/yahoo-finance-mcp
- **MCP Specification**: https://spec.modelcontextprotocol.io
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Smithery**: https://smithery.ai/server/@Alex2Yang97/yahoo-finance-mcp

---

**Note**: This project follows [Semantic Versioning](https://semver.org/). Version 2.0.0 introduces breaking changes; please review the migration guide before upgrading.

# Modernization Plan: Yahoo Finance MCP Server v2.0

> **Upgrade Python SDK from 1.6.0 → 1.19.0 with Protocol 2025-06-18 and dual STDIO/HTTP support**

---

## 🔍 Version Clarification

**Important**: This plan upgrades TWO distinct versioning systems:

1. **Python SDK Version**: 1.6.0 → **1.19.0** (latest as of Oct 24, 2025)
2. **MCP Protocol Version**: **2025-06-18** (current stable protocol specification)

The SDK version and protocol version are independent. The SDK v1.19.0 implements the 2025-06-18 protocol specification.

---

## 📊 Executive Summary

This modernization plan upgrades the Yahoo Finance MCP server from the legacy SDK 1.6.0 to the latest 1.19.0 release, implementing the current 2025-06-18 protocol specification. The upgrade adds:

- ✅ **Structured outputs** with automatic Pydantic validation
- ✅ **Dual transport support** (STDIO for local + Streamable HTTP for remote)
- ✅ **Type-safe context system** with proper async/await patterns
- ✅ **Progress reporting** for long-running operations
- ✅ **Comprehensive testing** (>80% coverage with mocked API calls)
- ✅ **Production-ready deployment** (Docker, health checks, env config)

**Estimated Time**: 16-22 hours (3-4 days) + 25% buffer  
**Breaking Changes**: Entry point changes (`server.py` → `main.py`), all tools return structured models  
**Backward Compatibility**: Maintained via dual content (text + structured)

---

## 📋 Table of Contents

1. [Main Objectives](#-main-objectives)
2. [Phase 1: Audit and Preparation](#phase-1-audit-and-preparation)
3. [Phase 2: Core MCP Modernization](#phase-2-core-mcp-modernization)
4. [Phase 3: Dual Transport System](#phase-3-dual-transport-system)
5. [Phase 4: Comprehensive Unit Tests](#phase-4-comprehensive-unit-tests)
6. [Phase 5: Documentation and Final Improvements](#phase-5-documentation-and-final-improvements)
7. [Implementation Timeline](#-implementation-timeline)
8. [Validation Checklist](#-final-validation-checklist)

---

## 🎯 Main Objectives

1. **Upgrade Python SDK from 1.6.0 → 1.19.0** (latest release: Oct 24, 2025)
2. **Implement Protocol 2025-06-18** (current stable MCP specification)
3. **Add dual STDIO + Streamable HTTP support** (HTTP supersedes deprecated SSE)
4. **Flexible configuration system** with environment-based config
5. **Modernize all tools** with structured Pydantic outputs
6. **Add comprehensive unit tests** (>80% coverage target)
7. **Improve error handling** with typed validation models
8. **Structured logging** using MCP Context API

---

## ⚠️ Pre-Implementation Requirements

**PHASE 0: Baseline and Backup** (Estimated: 30 minutes)

Before starting any implementation:

- [ ] **Create baseline documentation**
  ```bash
  # Document current state
  git add -A
  git commit -m "chore: baseline before modernization"
  git tag v1.x-baseline
  ```

- [ ] **Test current functionality**
  - Verify server starts: `uv run python server.py`
  - Test at least one tool via Claude Desktop
  - Document working ticker examples (e.g., "AAPL", "MSFT")

- [ ] **Create feature branch with protection**
  ```bash
  git checkout -b feat/modernize-mcp-1.19
  git push -u origin feat/modernize-mcp-1.19
  ```

---

## PHASE 1: Audit and Preparation

**Estimated duration:** 2-3 hours

### 1.1 Deprecation Analysis

**Critical Changes from SDK 1.6.0 → 1.19.0:**

- [ ] **Context System Changes**:
  - OLD: `Context` parameter optional and untyped
  - NEW: Type-safe `Context[ServerSession, AppContext]` with generic typing
  - Context methods now properly awaitable (`await ctx.info()`, not `ctx.info()`)

- [ ] **Structured Output (NEW in 2025-06-18 protocol)**:
  - Tools can now return Pydantic models, TypedDict, or dataclasses
  - Automatic schema generation and validation
  - Backward-compatible with text content

- [ ] **Transport Changes**:
  - SSE transport **deprecated** → Use Streamable HTTP instead
  - Streamable HTTP supports stateful and stateless modes
  - CORS headers required for browser-based clients

- [ ] **Progress Reporting** (SDK 1.10+):
  - `await ctx.report_progress(progress, total, message)`
  - Requires client support for progress notifications

- [ ] **Breaking Changes**:
  - `mcp.run()` parameters changed for HTTP transport
  - CORS configuration moved to `mcp.settings.cors`
  - Lifespan management now uses `asynccontextmanager`

- [ ] **Document current server.py dependencies**:
  ```bash
  # List current tool signatures
  grep -n "@yfinance_server.tool" server.py
  
  # Check for print() statements (should use logging)
  grep -n "print(" server.py
  
  # List all return types
  grep -A 3 "async def" server.py | grep "return"
  ```

### 1.2 Dependency Analysis

**Update `pyproject.toml`:**

```toml
[project]
name = "yahoo-finance-mcp"
version = "2.0.0"
description = "MCP server implementation for yahoo finance integration (Python SDK 1.19+, Protocol 2025-06-18)"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=1.19.0",      # ← UPDATED: Python SDK (was 1.6.0)
    "yfinance>=0.2.62",      # Keep current version
    "pydantic>=2.0",         # NEW: For structured validation
    "pydantic-settings>=2.0", # NEW: For configuration management
    "pandas>=2.0",           # Explicit (was transitive via yfinance)
]

[project.optional-dependencies]
dev = [
    "pre-commit>=3.6.0",
    "black>=24.2.0",
    "isort>=5.13.2",
    "ruff>=0.1.0",           # NEW: Modern linter (replaces flake8)
    "pytest>=8.0",           # NEW: Testing framework
    "pytest-asyncio>=0.23",  # NEW: Async test support
    "pytest-cov>=4.1",       # NEW: Coverage reporting
    "pytest-mock>=3.12",     # NEW: Mocking yfinance calls
    "httpx>=0.27",           # NEW: HTTP client for transport tests
    "pytest-httpx>=0.30",    # NEW: Mock HTTP requests
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Dependency Notes:**
- `mcp[cli]` includes CLI tools (`uv run mcp dev`, `uv run mcp install`)
- `pytest-mock` essential for mocking yfinance API calls (avoid rate limits)
- `httpx` and `pytest-httpx` for testing HTTP transport
- `ruff` replaces multiple linters (flake8, isort, black) with single tool

### 1.3 Prepare Development Environment

```bash
# Create working branch (if not done in Phase 0)
git checkout -b feat/modernize-mcp-1.19

# Backup current server (critical!)
cp server.py server_legacy.py
git add server_legacy.py
git commit -m "chore: backup legacy server before modernization"

# Update dependencies
uv sync --upgrade

# Install with dev dependencies
uv pip install -e ".[dev]"

# Verify installations
uv run python -c "import mcp; print(f'MCP SDK: {mcp.__version__}')"
uv run python -c "import yfinance as yf; print(f'yfinance: {yf.__version__}')"
uv run pytest --version

# Create directory structure
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
```

**Expected output:**
```
MCP SDK: 1.19.0
yfinance: 0.2.62 (or higher)
pytest 8.0.0 (or higher)
```

⚠️ **Checkpoint**: If any version doesn't match, resolve before proceeding.

---

## PHASE 2: Core MCP Modernization

**Estimated duration:** 4-6 hours

### 2.1 Update Base Server Structure

**Create file: `server.py` (modernized)**

```python
"""
Yahoo Finance MCP Server - Modernized for MCP 1.19+
Supports STDIO and Streamable HTTP transports with dynamic configuration.
"""
import os
import json
from enum import Enum
from typing import Annotated, Literal
from contextlib import asynccontextmanager

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP, Context, Icon
from mcp.server.session import ServerSession
from mcp.types import CallToolResult, TextContent


# ============================================================================
# ENUMS (no changes, but with better documentation)
# ============================================================================

class FinancialType(str, Enum):
    """Available financial statement types."""
    income_stmt = "income_stmt"
    quarterly_income_stmt = "quarterly_income_stmt"
    balance_sheet = "balance_sheet"
    quarterly_balance_sheet = "quarterly_balance_sheet"
    cashflow = "cashflow"
    quarterly_cashflow = "quarterly_cashflow"


class HolderType(str, Enum):
    """Types of holder information."""
    major_holders = "major_holders"
    institutional_holders = "institutional_holders"
    mutualfund_holders = "mutualfund_holders"
    insider_transactions = "insider_transactions"
    insider_purchases = "insider_purchases"
    insider_roster_holders = "insider_roster_holders"


class RecommendationType(str, Enum):
    """Types of analyst recommendations."""
    recommendations = "recommendations"
    upgrades_downgrades = "upgrades_downgrades"


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUTS (NEW IN PROTOCOL 2025-06-18)
# ============================================================================
# These models enable automatic schema generation and validation.
# Tools returning these types will have structured_content in responses.

class TickerValidationError(BaseModel):
    """Error model for ticker not found."""
    error: str
    ticker: str
    suggestion: str | None = None


class HistoricalPricePoint(BaseModel):
    """Historical price data point."""
    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None
    adj_close: float | None = Field(None, alias="Adj Close")

    class Config:
        populate_by_name = True


class StockInfoResponse(BaseModel):
    """Structured stock information response."""
    symbol: str
    shortName: str | None = None
    longName: str | None = None
    currentPrice: float | None = None
    marketCap: int | None = None
    # ... add more fields as needed


# ============================================================================
# LIFESPAN CONTEXT (NEW - better than global variables)
# ============================================================================

class AppContext(BaseModel):
    """Application context shared during lifecycle."""
    cache: dict = Field(default_factory=dict)
    request_count: int = 0

    class Config:
        arbitrary_types_allowed = True


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Handles server initialization and cleanup."""
    context = AppContext()

    # Startup: initialize resources
    print("🚀 Yahoo Finance MCP Server starting...")
    print(f"📊 yfinance version: {yf.__version__}")

    try:
        yield context
    finally:
        # Cleanup: close connections, save cache, etc.
        print(f"📈 Total requests processed: {context.request_count}")
        print("👋 Server shutting down...")


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

mcp = FastMCP(
    "Yahoo Finance",
    lifespan=app_lifespan,
    instructions="""
# Yahoo Finance MCP Server (v2.0)

**Python SDK**: 1.19.0 | **Protocol**: 2025-06-18

Modernized MCP server for Yahoo Finance financial data.
Supports STDIO and Streamable HTTP transports.

## Key features:
- Structured outputs with Pydantic validation
- Robust error handling with typed error models
- Structured logging via Context API
- Progress reporting for long operations
- Dual transport: STDIO (local) + Streamable HTTP (remote)
- Environment-based configuration

## Available transports:
- **STDIO**: For Claude Desktop and local clients
- **Streamable HTTP**: For remote deployment with optional auth
  (Note: SSE transport is deprecated, use Streamable HTTP)
""",
)

# Modern icons
mcp.icons = [
    Icon(
        src="https://s.yimg.com/cv/apiv2/default/icons/favicon_y19_32x32.ico",
        mimeType="image/x-icon",
        sizes="32x32"
    )
]
```

### 2.2 Modernize Tools with Structured Output

**Example: Modernized `get_historical_stock_prices`**

```python
@mcp.tool(
    name="get_historical_stock_prices",
    description="Get historical OHLCV prices for a Yahoo Finance ticker"
)
async def get_historical_stock_prices(
    ticker: str,
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1mo",
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"] = "1d",
    ctx: Context[ServerSession, AppContext] | None = None
) -> list[HistoricalPricePoint] | TickerValidationError:
    """
    Get historical price data.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        period: Time period to query
        interval: Interval between data points
        ctx: MCP context (injected automatically)

    Returns:
        List of historical price points or validation error
    """
    if ctx:
        await ctx.info(f"Querying historical data for {ticker} (period={period}, interval={interval})")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Modern ticker validation
        if company.isin is None:
            if ctx:
                await ctx.warning(f"Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker,
                suggestion="Check the symbol or try the full ticker (e.g., AAPL.MX for Mexico)"
            )

        # Get historical data
        hist_data = company.history(period=period, interval=interval)

        if hist_data.empty:
            return TickerValidationError(
                error=f"No data available for {ticker} in period {period}",
                ticker=ticker
            )

        # Convert to Pydantic model
        hist_data = hist_data.reset_index(names="Date")
        records = hist_data.to_dict(orient="records")

        result = [
            HistoricalPricePoint(
                date=str(rec["Date"]),
                open=rec.get("Open"),
                high=rec.get("High"),
                low=rec.get("Low"),
                close=rec.get("Close"),
                volume=int(rec["Volume"]) if rec.get("Volume") else None,
                adj_close=rec.get("Adj Close")
            )
            for rec in records
        ]

        if ctx:
            await ctx.info(f"✅ Returning {len(result)} data points for {ticker}")

        return result

    except Exception as e:
        if ctx:
            await ctx.error(f"Error getting historical data for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )
```

### 2.3 Add Progress Handling (SDK 1.10+ Feature)

**Important**: Progress reporting requires client support. Claude Desktop supports progress notifications in recent versions.

```python
@mcp.tool(
    name="get_multiple_stock_info",
    description="Get information for multiple stocks with progress reporting"
)
async def get_multiple_stock_info(
    tickers: list[str],
    ctx: Context[ServerSession, AppContext]
) -> dict[str, StockInfoResponse | TickerValidationError]:
    """
    Get info for multiple tickers with progress.

    Demonstrates ctx.report_progress() - SDK 1.10+ feature.
    Requires client support for progress notifications.
    """
    await ctx.info(f"Querying {len(tickers)} tickers...")

    results = {}
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        # Report progress
        await ctx.report_progress(
            progress=i / total,
            total=1.0,
            message=f"Processing {ticker} ({i}/{total})"
        )

        try:
            company = yf.Ticker(ticker)
            if company.isin is None:
                results[ticker] = TickerValidationError(
                    error=f"Ticker not found",
                    ticker=ticker
                )
                continue

            info = company.info
            results[ticker] = StockInfoResponse(
                symbol=ticker,
                shortName=info.get("shortName"),
                longName=info.get("longName"),
                currentPrice=info.get("currentPrice"),
                marketCap=info.get("marketCap")
            )

        except Exception as e:
            await ctx.debug(f"Error in {ticker}: {e}")
            results[ticker] = TickerValidationError(
                error=str(e),
                ticker=ticker
            )

    await ctx.info(f"✅ Processed {total} tickers")
    return results
```

---

## PHASE 3: Dual Transport System

**Estimated duration:** 3-4 hours

**Critical Note**: Streamable HTTP is the modern transport replacing SSE. This phase implements both STDIO (for local use) and Streamable HTTP (for remote deployment). SSE transport is deprecated and should not be used for new implementations.

### 3.1 Dynamic Transport Configuration

**Create file: `config.py`**

```python
"""
Configuration system for MCP transports.
Allows choosing between STDIO and Streamable HTTP.
"""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TransportType(str, Enum):
    """Supported transport types."""
    STDIO = "stdio"
    HTTP = "http"


class HTTPConfig(BaseModel):
    """HTTP transport configuration."""
    host: str = Field(default="0.0.0.0", description="HTTP server host")
    port: int = Field(default=3000, description="HTTP server port", ge=1024, le=65535)
    stateless: bool = Field(default=False, description="Stateless mode (no SSE)")
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )

    # Optional: Authentication (OAuth 2.1 support - requires separate AS)
    enable_auth: bool = Field(default=False, description="Enable OAuth 2.1")
    issuer_url: str | None = Field(default=None, description="Authorization Server URL")
    required_scopes: list[str] = Field(default=["read"], description="Required scopes")
    
    # Note: OAuth implementation requires a separate Authorization Server.
    # See: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
    # Example: examples/servers/simple-auth/ in Python SDK repository


class ServerConfig(BaseSettings):
    """MCP server general configuration."""

    # Transport
    transport: TransportType = Field(
        default=TransportType.STDIO,
        description="Transport type to use"
    )

    # HTTP configuration
    http: HTTPConfig = Field(default_factory=HTTPConfig)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )

    # Rate limiting (future)
    enable_rate_limit: bool = Field(default=False)
    requests_per_minute: int = Field(default=60)

    model_config = SettingsConfigDict(
        env_prefix="YF_MCP_",  # Environment variables: YF_MCP_TRANSPORT, etc.
        env_nested_delimiter="__",  # YF_MCP_HTTP__PORT
        case_sensitive=False
    )


# Global configuration instance
config = ServerConfig()
```

### 3.2 Dual Startup System

**Create file: `main.py`**

```python
#!/usr/bin/env python3
"""
Main entry point for Yahoo Finance MCP Server.
Supports startup with STDIO or Streamable HTTP based on configuration.
"""
import sys
from typing import NoReturn

from config import config, TransportType
from server import mcp


def run_stdio() -> NoReturn:
    """
    Run server in STDIO mode.
    Ideal for Claude Desktop and local use.
    """
    print("🔌 Starting server in STDIO mode...", file=sys.stderr)
    print(f"📊 Log level: {config.log_level}", file=sys.stderr)

    mcp.run(transport="stdio")


def run_http() -> NoReturn:
    """
    Run server in Streamable HTTP mode.
    Ideal for remote deployment and multiple clients.
    """
    print("🌐 Starting server in Streamable HTTP mode...", file=sys.stderr)
    print(f"   Host: {config.http.host}", file=sys.stderr)
    print(f"   Port: {config.http.port}", file=sys.stderr)
    print(f"   Stateless: {config.http.stateless}", file=sys.stderr)
    print(f"   CORS origins: {config.http.cors_origins}", file=sys.stderr)

    # Configure CORS
    mcp.settings.cors.allow_origins = config.http.cors_origins
    mcp.settings.cors.allow_methods = ["GET", "POST", "DELETE"]
    mcp.settings.cors.allow_headers = ["Authorization", "Content-Type", "Mcp-Session-Id"]

    # Run server
    mcp.run(
        transport="streamable-http",
        host=config.http.host,
        port=config.http.port,
        stateless_http=config.http.stateless
    )


def main() -> NoReturn:
    """Main entry point."""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  Yahoo Finance MCP Server v2.0                             ║
║  Python SDK: 1.19.0 | Protocol: 2025-06-18                ║
║  Transport: {config.transport.value.upper():^45} ║
╚════════════════════════════════════════════════════════════╝
    """, file=sys.stderr)

    if config.transport == TransportType.STDIO:
        run_stdio()
    elif config.transport == TransportType.HTTP:
        run_http()
    else:
        print(f"❌ Unknown transport: {config.transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
```

### 3.3 Startup Scripts

**Create file: `run_stdio.sh`**

```bash
#!/bin/bash
# Run in STDIO mode for Claude Desktop

export YF_MCP_TRANSPORT=stdio
export YF_MCP_LOG_LEVEL=INFO

uv run python main.py
```

**Create file: `run_http.sh`**

```bash
#!/bin/bash
# Run in HTTP mode for remote deployment

export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__HOST=0.0.0.0
export YF_MCP_HTTP__PORT=3000
export YF_MCP_HTTP__STATELESS=false
export YF_MCP_LOG_LEVEL=INFO

uv run python main.py
```

**Update file: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  yfinance-mcp:
    build: .
    ports:
      - "3000:3000"
    environment:
      - YF_MCP_TRANSPORT=http
      - YF_MCP_HTTP__PORT=3000
      - YF_MCP_HTTP__STATELESS=false
      - YF_MCP_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## PHASE 4: Comprehensive Unit Tests

**Estimated duration:** 4-5 hours

**Testing Strategy**:
1. **Mock all yfinance calls** to avoid rate limits and API dependencies
2. **Use in-memory sessions** for fast execution
3. **Test structured outputs** with Pydantic validation
4. **Cover both transports** (STDIO and HTTP)
5. **Target 80%+ coverage** focusing on critical paths first

**Note**: Real API integration tests should be separate (marked with `@pytest.mark.integration`) and run infrequently.

### 4.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_tools.py              # Tool tests
├── test_resources.py          # Resource tests
├── test_prompts.py            # Prompt tests
├── test_transports.py         # STDIO/HTTP tests
├── test_structured_output.py  # Pydantic validation tests
└── test_integration.py        # Integration tests
```

### 4.2 Shared Fixtures

**Create file: `tests/conftest.py`**

```python
"""
Shared fixtures for MCP server tests.
Uses in-memory session creation to avoid socket/network overhead.
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock
from mcp.shared.memory import create_connected_server_and_client_session
from server import mcp


@pytest_asyncio.fixture
async def mcp_session():
    """
    Create connected server-client session in memory.
    Ideal for tests without sockets or network calls.
    
    This fixture uses the official MCP testing pattern from SDK 1.19+.
    """
    async with create_connected_server_and_client_session(
        mcp,
        raise_exceptions=True  # Errors propagate directly for easier debugging
    ) as session:
        await session.initialize()
        yield session


@pytest.fixture
def mock_yfinance(mocker):
    """
    Mock yfinance.Ticker to avoid real API calls.
    Essential for fast, reliable tests without rate limits.
    """
    mock_ticker = mocker.patch('yfinance.Ticker')
    return mock_ticker


@pytest.fixture
def mock_ticker_data():
    """Mock ticker data for tests."""
    return {
        "AAPL": {
            "shortName": "Apple Inc.",
            "currentPrice": 150.25,
            "marketCap": 2500000000000
        },
        "MSFT": {
            "shortName": "Microsoft Corporation",
            "currentPrice": 380.50,
            "marketCap": 2800000000000
        }
    }


@pytest.fixture
def invalid_tickers():
    """List of invalid tickers for error tests."""
    return ["INVALID123", "NOTREAL", ""]
```

### 4.3 Tool Tests

**Create file: `tests/test_tools.py`**

```python
"""
Unit tests for MCP server tools.
"""
import pytest
from inline_snapshot import snapshot


class TestHistoricalStockPrices:
    """Tests for get_historical_stock_prices."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_data(self, mcp_session):
        """Verify valid ticker returns historical data."""
        result = await mcp_session.call_tool(
            "get_historical_stock_prices",
            {"ticker": "AAPL", "period": "5d", "interval": "1d"}
        )

        # Verify returns list of data points
        assert result.structured_content is not None
        assert isinstance(result.structured_content, list)
        assert len(result.structured_content) > 0

        # Verify structure of each point
        first_point = result.structured_content[0]
        assert "date" in first_point
        assert "close" in first_point
        assert "volume" in first_point

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_error(self, mcp_session):
        """Verify invalid ticker returns structured error."""
        result = await mcp_session.call_tool(
            "get_historical_stock_prices",
            {"ticker": "INVALID123", "period": "1d", "interval": "1d"}
        )

        # Should return TickerValidationError
        assert result.structured_content is not None
        assert "error" in result.structured_content
        assert "ticker" in result.structured_content
        assert result.structured_content["ticker"] == "INVALID123"

    @pytest.mark.asyncio
    async def test_period_validation(self, mcp_session):
        """Verify invalid period generates validation error."""
        with pytest.raises(Exception) as exc_info:
            await mcp_session.call_tool(
                "get_historical_stock_prices",
                {"ticker": "AAPL", "period": "invalid_period"}
            )

        # Error should mention valid values
        assert "Literal" in str(exc_info.value) or "validation" in str(exc_info.value).lower()


class TestMultipleStockInfo:
    """Tests for get_multiple_stock_info with progress."""

    @pytest.mark.asyncio
    async def test_multiple_tickers_with_progress(self, mcp_session):
        """Verify processing of multiple tickers."""
        result = await mcp_session.call_tool(
            "get_multiple_stock_info",
            {"tickers": ["AAPL", "MSFT", "GOOGL"]}
        )

        assert result.structured_content is not None
        assert len(result.structured_content) == 3
        assert "AAPL" in result.structured_content
        assert "MSFT" in result.structured_content

    @pytest.mark.asyncio
    async def test_mixed_valid_invalid_tickers(self, mcp_session):
        """Verify handling of mixed valid/invalid tickers."""
        result = await mcp_session.call_tool(
            "get_multiple_stock_info",
            {"tickers": ["AAPL", "INVALID123", "MSFT"]}
        )

        data = result.structured_content

        # AAPL and MSFT should have valid data
        assert "symbol" in data["AAPL"]
        assert "symbol" in data["MSFT"]

        # INVALID123 should have error
        assert "error" in data["INVALID123"]


@pytest.mark.asyncio
async def test_all_tools_discoverable(mcp_session):
    """Verify all tools are discoverable."""
    tools = await mcp_session.list_tools()

    tool_names = {t.name for t in tools.tools}

    expected_tools = {
        "get_historical_stock_prices",
        "get_stock_info",
        "get_yahoo_finance_news",
        "get_stock_actions",
        "get_financial_statement",
        "get_holder_info",
        "get_option_expiration_dates",
        "get_option_chain",
        "get_recommendations",
        "get_multiple_stock_info",  # New tool
    }

    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"
```

### 4.4 Transport Tests

**Create file: `tests/test_transports.py`**

```python
"""
STDIO and Streamable HTTP transport tests.
"""
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx


class TestSTDIOTransport:
    """STDIO transport tests."""

    @pytest.mark.asyncio
    async def test_stdio_connection(self):
        """Verify STDIO connection with server."""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "main.py"],
            env={"YF_MCP_TRANSPORT": "stdio"}
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Verify server responds
                tools = await session.list_tools()
                assert len(tools.tools) > 0


class TestHTTPTransport:
    """Streamable HTTP transport tests."""

    @pytest.mark.asyncio
    async def test_http_health_endpoint(self):
        """Verify health check endpoint."""
        # Note: Requires HTTP server running at http://localhost:3000
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_http_mcp_endpoint(self):
        """Verify MCP endpoint over HTTP."""
        async with httpx.AsyncClient() as client:
            # Initialize handshake
            response = await client.post(
                "http://localhost:3000/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",  # Current protocol version
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "result" in data
            assert data["result"]["protocolVersion"] == "2025-06-18"  # Server must match
```

### 4.5 Structured Output Tests

**Create file: `tests/test_structured_output.py`**

```python
"""
Structured output validation tests (Pydantic).
"""
import pytest
from pydantic import ValidationError
from server import (
    HistoricalPricePoint,
    StockInfoResponse,
    TickerValidationError
)


class TestHistoricalPricePoint:
    """HistoricalPricePoint model tests."""

    def test_valid_price_point(self):
        """Verify valid price point creation."""
        point = HistoricalPricePoint(
            date="2024-01-15",
            open=150.0,
            high=155.0,
            low=149.0,
            close=154.0,
            volume=1000000,
            adj_close=154.0
        )

        assert point.date == "2024-01-15"
        assert point.close == 154.0

    def test_missing_optional_fields(self):
        """Verify optional fields can be missing."""
        point = HistoricalPricePoint(
            date="2024-01-15",
            close=150.0
        )

        assert point.open is None
        assert point.volume is None

    def test_invalid_types_raise_error(self):
        """Verify invalid types generate error."""
        with pytest.raises(ValidationError):
            HistoricalPricePoint(
                date="2024-01-15",
                close="not_a_number"  # Should be float
            )


class TestTickerValidationError:
    """Validation error model tests."""

    def test_error_with_suggestion(self):
        """Verify error with suggestion."""
        error = TickerValidationError(
            error="Ticker not found",
            ticker="APPL",  # Common typo
            suggestion="Did you mean AAPL?"
        )

        assert error.ticker == "APPL"
        assert error.suggestion is not None

    def test_error_without_suggestion(self):
        """Verify error without suggestion."""
        error = TickerValidationError(
            error="Invalid ticker",
            ticker="INVALID123"
        )

        assert error.suggestion is None
```

### 4.6 Pytest Configuration

**Update `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--asyncio-mode=auto",
    "--cov=.",
    "--cov-report=html",
    "--cov-report=term-missing:skip-covered",
]
testpaths = ["tests"]
pythonpath = ["."]

[tool.coverage.run]
source = ["."]
omit = [
    "tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

---

## PHASE 5: Documentation and Final Improvements

**Estimated duration:** 2-3 hours

### 5.1 Update README.md

Add the following sections to README:

```markdown
## 🚀 Running the Server

### STDIO Mode (Local)

For use with Claude Desktop or other local clients:

```bash
# Option 1: Using helper script
chmod +x run_stdio.sh
./run_stdio.sh

# Option 2: Using environment variables
export YF_MCP_TRANSPORT=stdio
uv run python main.py

# Option 3: With MCP Inspector (development)
uv run mcp dev main.py
```

### HTTP Mode (Remote)

For deployment as web service:

```bash
# Option 1: Using helper script
chmod +x run_http.sh
./run_http.sh

# Option 2: Using environment variables
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3000
uv run python main.py

# Option 3: With Docker Compose
docker-compose up -d
```

### Environment Variables

| Variable | Values | Default | Description |
|----------|---------|---------|-------------|
| `YF_MCP_TRANSPORT` | `stdio`, `http` | `stdio` | Transport type |
| `YF_MCP_HTTP__HOST` | IP/hostname | `0.0.0.0` | HTTP host |
| `YF_MCP_HTTP__PORT` | 1024-65535 | `3000` | HTTP port |
| `YF_MCP_HTTP__STATELESS` | `true`, `false` | `false` | Stateless mode |
| `YF_MCP_LOG_LEVEL` | `DEBUG`, `INFO`, etc. | `INFO` | Log level |

## 🧪 Testing

```bash
# Run all tests
pytest

# Tests with coverage
pytest --cov

# Specific tests
pytest tests/test_tools.py

# Verbose output
pytest -v

# Watch mode (auto-reload)
pytest-watch
```

## 📊 New Features (v2.0)

- ✅ **MCP 1.19+ compliance**: Updated to latest specification
- ✅ **Structured outputs**: Automatic Pydantic validation
- ✅ **Dual transport**: STDIO + Streamable HTTP
- ✅ **Real-time progress**: Progress reporting for long operations
- ✅ **Structured logging**: Rich context in logs
- ✅ **Test coverage**: >80% coverage
- ✅ **Type safety**: Complete type hints
- ✅ **Error handling**: Robust handling with clear messages

## 📝 Migration from v1.x

### Claude Desktop Configuration

**Before (MCP 1.6):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "server.py"]
    }
  }
}
```

**After (MCP 1.19+):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "python", "main.py"],
      "env": {
        "YF_MCP_TRANSPORT": "stdio",
        "YF_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note**: The `env` key allows passing environment variables to configure the server without modifying code.
```

### 5.2 Create CHANGELOG.md

**Create file: `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-XX

### Added
- **Python SDK 1.19+ Support**: Upgraded from SDK 1.6.0 to 1.19.0+ (Oct 24, 2025 release)
- **Protocol 2025-06-18**: Implements current stable MCP protocol specification
- **Dual Transport System**: Support for both STDIO and Streamable HTTP
- **Structured Outputs**: Pydantic models for all tool responses with automatic validation
- **Progress Reporting**: Real-time progress updates for long operations (SDK 1.10+ feature)
- **Lifespan Management**: Proper startup/shutdown handling with typed context
- **New Tool**: `get_multiple_stock_info` with progress tracking
- **Configuration System**: Environment-based config with `pydantic-settings`
- **Comprehensive Tests**: Unit tests with >80% coverage (mocked yfinance calls)
- **Type Safety**: Complete type hints throughout codebase
- **Context API**: Structured logging with `await ctx.info()`, `await ctx.error()`, etc.

### Changed
- **Breaking**: Entry point changed from `server.py` to `main.py` (backward compatibility via symlink optional)
- **Breaking**: All tools now return structured Pydantic models (also includes text content for backward compatibility)
- **Improved**: Error handling with typed `TickerValidationError` model
- **Improved**: Logging using MCP Context API (`await ctx.info()`, `await ctx.error()`)
- **Enhanced**: Docker support with health checks and proper environment config
- **Modernized**: HTTP transport uses Streamable HTTP (SSE deprecated)

### Deprecated
- Direct execution of `server.py` (use `main.py` instead)

### Fixed
- Rate limiting issues with yfinance (upgraded to 0.2.62+)
- Type validation errors in financial statement endpoints

## [1.0.0] - 2024-XX-XX

### Added
- Initial release with MCP 1.6.0 support
- Basic tools for stock data retrieval
- STDIO transport only
```

### 5.3 Create Migration Guide

**Create file: `MIGRATION_GUIDE.md`**

```markdown
# Migration Guide v1.x → v2.0

This guide will help you migrate your existing configuration to the new version.

## Main Changes

### 1. Entry Point

**Before:**
```bash
uv run server.py
```

**After:**
```bash
uv run python main.py
```

### 2. Claude Desktop Config

Update your `claude_desktop_config.json`:

**Before:**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "server.py"]
    }
  }
}
```

**After:**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": ["--directory", "/path/to/yahoo-finance-mcp", "run", "python", "main.py"],
      "env": {
        "YF_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 3. Tool Responses

Responses are now structured Pydantic models:

**Before (v1.x):**
```json
{
  "content": "[{\"Date\": \"2024-01-15\", \"Close\": 150.0, ...}]"
}
```

**After (v2.0):**
```json
{
  "structured_content": [
    {
      "date": "2024-01-15",
      "close": 150.0,
      "open": 149.0,
      "high": 151.0,
      "low": 148.5,
      "volume": 1000000
    }
  ]
}
```

### 4. Error Handling

Errors are now structured:

**Before:**
```
"Company ticker INVALID123 not found."
```

**After:**
```json
{
  "error": "Ticker 'INVALID123' not found",
  "ticker": "INVALID123",
  "suggestion": "Check the symbol or try the full ticker"
}
```

## Installing v2.0

```bash
# 1. Update dependencies
uv sync --upgrade

# 2. Verify installation
uv run python main.py --version

# 3. Run tests
pytest

# 4. Restart Claude Desktop
```

## Rollback to v1.x

If you encounter issues:

```bash
# Restore previous version
git checkout v1.x
uv sync

# Use legacy server.py
uv run server.py
```
```

---

## 📅 Implementation Timeline

| Phase | Duration | Critical Tasks | Dependencies |
|------|----------|-----------------|--------------|
| **Phase 0** | 0.5h | Baseline, backup, branch setup | - |
| **Phase 1** | 2-3h | Audit, prepare branch, update deps | Phase 0 |
| **Phase 2** | 4-6h | Modernize FastMCP, structured output, Context | Phase 1 |
| **Phase 3** | 3-4h | Config system, dual transport, Docker | Phase 2 |
| **Phase 4** | 4-5h | Unit tests with mocked yfinance (>80% coverage) | Phase 2, 3 |
| **Phase 5** | 2-3h | Docs, examples, migration guide | Phase 1-4 |
| **TOTAL** | **16-22h** | **3-4 days effective work** | - |

**Buffer**: Add 25% contingency time for unexpected issues (20-27.5h total)

### Key Milestones

- [ ] **Phase 0**: Baseline established, backups created → Safe to proceed
- [ ] **Day 1**: Complete Phase 1 and start Phase 2 → Dependencies updated, structure planned
- [ ] **Day 2**: Complete Phase 2 and start Phase 3 → Modernized server with structured outputs
- [ ] **Day 3**: Complete Phase 3 and Phase 4 → Dual transport + passing tests
- [ ] **Day 4**: Complete Phase 5 + review → Documentation complete, ready for merge

**Daily Checkpoints**:
- Each day, commit work with meaningful messages
- Test STDIO transport in Claude Desktop
- Verify no regressions in existing functionality

---

## ✅ Final Validation Checklist

### Pre-merge

- [ ] All tests pass (`pytest` with no failures)
- [ ] Coverage >80% (`pytest --cov` report verified)
- [ ] Clean linting (`ruff check .` with zero errors)
- [ ] No type errors (`mypy .` - optional but recommended)
- [ ] Updated docs (README, CHANGELOG, MIGRATION_GUIDE all current)
- [ ] Functional test in Claude Desktop (STDIO transport)
- [ ] Functional test via HTTP (`curl` or Postman to verify endpoints)
- [ ] Executable scripts have correct permissions (`chmod +x run_*.sh`)
- [ ] Successful Docker build (`docker-compose build` completes)
- [ ] Successful Docker run (`docker-compose up` and health check passes)
- [ ] Version numbers consistent across all files (pyproject.toml, main.py, README)

### Functional Tests (Manual Verification)

- [ ] Tool `get_historical_stock_prices` returns valid structured data for "AAPL"
- [ ] Invalid ticker "INVALID123" returns `TickerValidationError` with structured error
- [ ] Tool `get_multiple_stock_info` shows progress in logs/UI (if client supports)
- [ ] Lifespan context properly increments `request_count` (check server logs)
- [ ] Structured logging visible in stderr (`await ctx.info()` messages appear)
- [ ] STDIO transport connects successfully from Claude Desktop
- [ ] HTTP transport responds correctly at `http://localhost:3000/mcp`
- [ ] Health endpoint returns 200 OK at `http://localhost:3000/health` (if implemented)
- [ ] Environment variables properly configure server (test different YF_MCP_* values)

### Cross-Client Compatibility

- [ ] Works with Claude Desktop (latest version)
- [ ] `uv run mcp dev main.py` (Inspector works)
- [ ] Python client script can connect via STDIO
- [ ] HTTP client (httpx/curl) can initialize session

### Performance & Reliability

- [ ] Server starts in <5 seconds
- [ ] First tool call completes in reasonable time (<30s including yfinance API)
- [ ] No memory leaks during extended operation (run for 10+ minutes)
- [ ] Graceful shutdown on Ctrl+C
- [ ] Proper error messages for all failure scenarios

### Post-merge

- [ ] Release tag `v2.0.0` created
- [ ] Branch `feat/modernize-mcp-1.19` merged to `main`
- [ ] Update smithery.yaml with new version
- [ ] Announcement in GitHub Discussions
- [ ] Update MCP version badge in README

---

## 🎯 Expected Results

Upon completing this plan:

1. ✅ **Server 100% compatible with Python SDK 1.19.0 and Protocol 2025-06-18**
2. ✅ **Deployment flexibility**: Local (STDIO) or Remote (Streamable HTTP) with single codebase
3. ✅ **Robustness**: Test coverage >80%, comprehensive error handling with typed models
4. ✅ **Developer Experience**: Full type safety, structured logging, clear documentation
5. ✅ **Future-ready**: Modular architecture prepared for OAuth, rate limiting, caching extensions
6. ✅ **Backward compatible**: Old clients receive text content, new clients get structured outputs
7. ✅ **Production-ready**: Docker support, health checks, environment-based config

---

## 🚨 Common Pitfalls & Solutions

### Issue: "Module 'mcp' has no attribute 'X'"
**Solution**: Verify SDK version with `python -c "import mcp; print(mcp.__version__)"`. Must be 1.19.0+.

### Issue: Tests fail with "RuntimeError: no running event loop"
**Solution**: Ensure `pytest-asyncio` is installed and test functions are marked with `@pytest.mark.asyncio`.

### Issue: yfinance rate limiting during tests
**Solution**: Mock all yfinance calls with `pytest-mock`. Never make real API calls in unit tests.

### Issue: HTTP transport doesn't start
**Solution**: Check port 3000 isn't in use (`lsof -i :3000`). Verify CORS settings for browser clients.

### Issue: Context injection not working
**Solution**: Ensure parameter has type hint: `ctx: Context[ServerSession, AppContext]`.

### Issue: Progress reporting doesn't show
**Solution**: Client must support progress notifications. Claude Desktop supports this in recent versions.

---

## 🛡️ Risk Mitigation Strategy

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking changes for existing users | **High** | **High** | • Maintain `server_legacy.py` backup<br>• Document migration path<br>• Test with Claude Desktop before release |
| yfinance API rate limits in tests | **High** | **Medium** | • Mock all API calls with `pytest-mock`<br>• Separate integration tests with `@pytest.mark.integration`<br>• Use cached responses for examples |
| HTTP transport configuration complexity | **Medium** | **Medium** | • Provide working examples<br>• Include docker-compose template<br>• Document common CORS issues |
| Test coverage not reaching 80% | **Medium** | **Low** | • Focus on critical paths first<br>• Skip trivial getters/setters<br>• Use coverage reports to identify gaps |
| Migration effort underestimated | **Medium** | **High** | • Built-in 25% time buffer<br>• Daily checkpoints<br>• Can deploy incrementally (STDIO first) |
| SDK bugs or incompatibilities | **Low** | **High** | • SDK v1.19.0 is battle-tested<br>• Large community on GitHub<br>• Active maintenance team |

**Rollback Plan**: If critical issues arise, revert to `server_legacy.py` and update Claude Desktop config to use it. All changes are in version control and can be rolled back within minutes.

---

## 📚 References

- [MCP Specification (Protocol 2025-06-18)](https://spec.modelcontextprotocol.io)
- [MCP Python SDK (v1.19.0) GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [FastMCP Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)
- [Streamable HTTP Transport Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http)

---

**Created:** 2025-01-25  
**Last updated:** 2025-10-25  
**Author:** AI Assistant (Claude)  
**Version:** 2.0 (Revised with SDK/Protocol clarifications)

# Migration Guide: v1.x → v2.0

This guide will help you migrate your existing Yahoo Finance MCP Server installation from v1.x to v2.0.

## Table of Contents

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Configuration Changes](#configuration-changes)
5. [Response Format Changes](#response-format-changes)
6. [Testing Your Migration](#testing-your-migration)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Instructions](#rollback-instructions)

---

## Overview

### What's Different in v2.0?

| Aspect | v1.x | v2.0 |
|--------|------|------|
| **Entry Point** | `server.py` | `main.py` |
| **MCP SDK** | 1.6.0 | 1.19.0+ |
| **Protocol** | Legacy | 2025-06-18 |
| **Response Format** | Plain text/JSON strings | Structured Pydantic models |
| **Transport** | STDIO only | STDIO + Streamable HTTP |
| **Configuration** | Hardcoded | Environment variables |
| **Error Handling** | Text messages | Structured error models |
| **Testing** | None | 68 tests, 75% coverage |
| **Logging** | `print()` statements | MCP Context API |

### Why Upgrade?

✅ **Better type safety** with Pydantic validation  
✅ **More deployment options** with HTTP transport  
✅ **Improved error messages** with structured errors  
✅ **Production ready** with comprehensive tests  
✅ **Modern MCP features** like progress reporting  
✅ **Flexible configuration** via environment variables  

---

## Breaking Changes

### 1. Entry Point Change

**Before (v1.x):**
```bash
uv run server.py
```

**After (v2.0):**
```bash
uv run python main.py
```

### 2. Claude Desktop Configuration

**Before (v1.x):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/yahoo-finance-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**After (v2.0):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/yahoo-finance-mcp",
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

**Key Changes:**
- `server.py` → `python main.py`
- Added `env` object for configuration
- Transport type explicitly set to `stdio`

### 3. Tool Response Format

**Before (v1.x) - Plain Text:**
```python
# Historical prices returned as JSON string
"[{\"Date\": \"2024-01-15\", \"Close\": 150.0, ...}]"
```

**After (v2.0) - Structured:**
```python
# Historical prices returned as typed list
[
  HistoricalPricePoint(
    date="2024-01-15",
    close=150.0,
    open=149.0,
    high=151.0,
    low=148.5,
    volume=1000000,
    adj_close=150.2
  ),
  ...
]
```

**Backward Compatibility:**
- v2.0 includes both `content` (text) and `structured_content` (typed)
- Old clients receive text, new clients get structured data
- No client changes required for basic functionality

### 4. Error Responses

**Before (v1.x):**
```
"Company ticker INVALID123 not found."
```

**After (v2.0):**
```json
{
  "error": "Ticker 'INVALID123' not found",
  "ticker": "INVALID123",
  "suggestion": "Check the symbol or try the full ticker (e.g., AAPL.MX for Mexico)"
}
```

---

## Step-by-Step Migration

### Step 1: Backup Current Configuration

```bash
# Save your current Claude Desktop config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup

# Or on Windows:
# copy %AppData%\Claude\claude_desktop_config.json %AppData%\Claude\claude_desktop_config.json.backup
```

### Step 2: Update Repository

```bash
# Navigate to your installation
cd /path/to/yahoo-finance-mcp

# Fetch latest changes
git fetch origin

# Checkout v2.0 (replace with actual tag/branch)
git checkout main  # or v2.0.0 when tagged
git pull origin main
```

### Step 3: Update Dependencies

```bash
# Update all dependencies to latest versions
uv sync --upgrade

# Verify MCP SDK version
uv run python -c "import mcp; print(f'MCP SDK: {mcp.__version__}')"
# Expected output: MCP SDK: 1.19.0 (or higher)

# Verify yfinance version
uv run python -c "import yfinance as yf; print(f'yfinance: {yf.__version__}')"
# Expected output: yfinance: 0.2.66 (or higher)
```

### Step 4: Update Claude Desktop Configuration

Edit your `claude_desktop_config.json`:

**macOS:**
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
code $env:AppData\Claude\claude_desktop_config.json
```

**Update the configuration:**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/yahoo-finance-mcp",  // ← Update this path
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

**Important:** Replace `/ABSOLUTE/PATH/TO/yahoo-finance-mcp` with your actual path.

### Step 5: Test the Server Independently

Before restarting Claude Desktop, test the server:

```bash
# Test STDIO mode (should start without errors)
uv run python main.py

# In another terminal, test with MCP Inspector
uv run mcp dev src/server.py

# Run tests to verify everything works
uv run pytest
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════╗
║  Yahoo Finance MCP Server v2.0                             ║
║  Python SDK: 1.19.0 | Protocol: 2025-06-18                ║
║  Transport: STDIO                                          ║
╚════════════════════════════════════════════════════════════╝
```

### Step 6: Restart Claude Desktop

1. **Quit Claude Desktop completely** (ensure it's not running in background)
2. **Restart Claude Desktop**
3. **Look for the 🔌 icon** in the chat interface indicating server connection

### Step 7: Test Integration

Try a simple query in Claude Desktop:

```
Can you get the historical stock prices for AAPL over the last 5 days?
```

**Expected behavior:**
- Server receives request
- Returns structured historical price data
- Claude displays the information in a readable format

---

## Configuration Changes

### Environment Variables (New in v2.0)

All configuration is now done via environment variables prefixed with `YF_MCP_`:

| Variable | Purpose | Default | Values |
|----------|---------|---------|--------|
| `YF_MCP_TRANSPORT` | Transport type | `stdio` | `stdio`, `http` |
| `YF_MCP_HTTP__HOST` | HTTP server host | `0.0.0.0` | Any IP/hostname |
| `YF_MCP_HTTP__PORT` | HTTP server port | `3000` | 1024-65535 |
| `YF_MCP_HTTP__STATELESS` | Stateless mode | `false` | `true`, `false` |
| `YF_MCP_LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Setting Environment Variables

**In Claude Desktop config:**
```json
{
  "env": {
    "YF_MCP_TRANSPORT": "stdio",
    "YF_MCP_LOG_LEVEL": "DEBUG"
  }
}
```

**In shell (for HTTP mode):**
```bash
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3000
export YF_MCP_LOG_LEVEL=INFO
uv run python main.py
```

**In Docker (docker-compose.yml):**
```yaml
environment:
  - YF_MCP_TRANSPORT=http
  - YF_MCP_HTTP__PORT=3000
  - YF_MCP_LOG_LEVEL=INFO
```

---

## Response Format Changes

### Historical Stock Prices

**v1.x Response:**
```json
{
  "content": "[{\"Date\":\"2024-01-15\",\"Open\":149.0,\"High\":151.0,\"Low\":148.5,\"Close\":150.0,\"Volume\":1000000,\"Adj Close\":150.2}]"
}
```

**v2.0 Response:**
```json
{
  "content": "Historical prices for AAPL...",
  "structured_content": [
    {
      "date": "2024-01-15",
      "open": 149.0,
      "high": 151.0,
      "low": 148.5,
      "close": 150.0,
      "volume": 1000000,
      "adj_close": 150.2
    }
  ]
}
```

### Error Responses

**v1.x Error:**
```
"Error: Company ticker INVALID123 not found"
```

**v2.0 Error:**
```json
{
  "error": "Ticker 'INVALID123' not found",
  "ticker": "INVALID123",
  "suggestion": "Check the symbol or try the full ticker (e.g., AAPL.MX for Mexico)"
}
```

### Stock Info

**v1.x Response:**
```json
{
  "content": "Apple Inc. (AAPL)\nCurrent Price: $150.25\n..."
}
```

**v2.0 Response:**
```json
{
  "content": "Stock information for AAPL...",
  "structured_content": {
    "symbol": "AAPL",
    "shortName": "Apple Inc.",
    "longName": "Apple Inc.",
    "currentPrice": 150.25,
    "marketCap": 2500000000000,
    "volume": 50000000,
    "averageVolume": 55000000,
    "fiftyTwoWeekHigh": 180.0,
    "fiftyTwoWeekLow": 120.0
  }
}
```

---

## Testing Your Migration

### 1. Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Expected: 68 passed, coverage ~75%
```

### 2. Test STDIO Transport

```bash
# Start server
export YF_MCP_TRANSPORT=stdio
uv run python main.py

# Should show:
# ╔════════════════════════════════════════════════════════════╗
# ║  Yahoo Finance MCP Server v2.0                             ║
# ║  Transport: STDIO                                          ║
# ╚════════════════════════════════════════════════════════════╝
```

### 3. Test HTTP Transport (Optional)

```bash
# Start HTTP server
export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__PORT=3000
uv run python main.py

# In another terminal, test with curl
curl http://localhost:3000/health
# Expected: 200 OK

# Test MCP endpoint
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'
```

### 4. Test with Claude Desktop

1. Restart Claude Desktop
2. Look for 🔌 icon indicating server connection
3. Try these test queries:

```
1. Get historical stock prices for AAPL over the last 5 days
2. Get stock information for MSFT
3. Get the latest news for TSLA
4. Try an invalid ticker like "INVALID123" (should show helpful error)
```

### 5. Verify Logs

Check server logs for structured logging:

```bash
# In Claude Desktop logs or terminal output, you should see:
# 🚀 Yahoo Finance MCP Server starting...
# 📊 yfinance version: 0.2.66
# Querying historical data for AAPL (period=5d, interval=1d)
# ✅ Returning 5 data points for AAPL
```

---

## Troubleshooting

### Issue: "Module 'mcp' has no attribute 'X'"

**Cause:** Old SDK version still installed

**Solution:**
```bash
# Force upgrade
uv sync --upgrade
uv pip install --force-reinstall mcp>=1.19.0

# Verify version
uv run python -c "import mcp; print(mcp.__version__)"
```

### Issue: Server Won't Start

**Cause:** Syntax errors or missing dependencies

**Solution:**
```bash
# Check Python version (must be 3.11+)
python --version

# Reinstall dependencies
uv sync --upgrade

# Check for errors
uv run python main.py
```

### Issue: Claude Desktop Shows No Connection (No 🔌 Icon)

**Cause:** Configuration error or server not starting

**Solution:**
1. Check Claude Desktop logs:
   - **macOS:** `~/Library/Logs/Claude/mcp*.log`
   - **Windows:** `%AppData%\Claude\logs\mcp*.log`

2. Verify configuration path is absolute:
   ```json
   {
     "args": [
       "--directory",
       "/Users/yourname/path/to/yahoo-finance-mcp",  // ← Must be absolute
       "run",
       "python",
       "main.py"
     ]
   }
   ```

3. Test server independently:
   ```bash
   uv run python main.py
   ```

### Issue: "RuntimeError: no running event loop"

**Cause:** Missing `pytest-asyncio` or incorrect test setup

**Solution:**
```bash
# Install test dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

### Issue: HTTP Mode Port Already in Use

**Cause:** Port 3000 is occupied

**Solution:**
```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process or use different port
export YF_MCP_HTTP__PORT=3001
uv run python main.py
```

### Issue: Deprecation Warnings

**Cause:** Pydantic v2 Config class warnings (non-blocking)

**Solution:**
These warnings are non-blocking but will be fixed in a future release. If they bother you:

```bash
# Run with warnings suppressed
PYTHONWARNINGS=ignore uv run python main.py
```

---

## Rollback Instructions

If you need to revert to v1.x:

### Step 1: Restore Git State

```bash
# Find previous working commit
git log --oneline

# Revert to v1.x commit (replace COMMIT_HASH)
git checkout <COMMIT_HASH>

# Or checkout v1.x branch if it exists
git checkout v1.x
```

### Step 2: Reinstall Old Dependencies

```bash
# Sync to old dependencies
uv sync

# Verify old SDK version
uv run python -c "import mcp; print(mcp.__version__)"
# Expected: 1.6.0
```

### Step 3: Restore Claude Desktop Config

```bash
# Restore backup
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or manually edit to use old format:
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/yahoo-finance-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop
2. Restart
3. Verify connection with old server

---

## Additional Resources

- [CHANGELOG.md](CHANGELOG.md) - Detailed version changes
- [README.md](README.md) - Updated usage documentation
- [MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md) - Technical implementation details
- [MCP Specification](https://spec.modelcontextprotocol.io) - Official protocol docs
- [GitHub Issues](https://github.com/Alex2Yang97/yahoo-finance-mcp/issues) - Report problems

---

## Need Help?

If you encounter issues not covered in this guide:

1. **Check Logs:** Claude Desktop logs contain detailed error information
2. **Run Tests:** `uv run pytest -v` to identify specific failures
3. **Open Issue:** Create a GitHub issue with:
   - Your OS and Python version
   - MCP SDK version (`uv run python -c "import mcp; print(mcp.__version__)"`)
   - Error messages from logs
   - Steps to reproduce

---

**Last Updated:** 2025-10-25  
**Applies To:** v2.0.0 and later

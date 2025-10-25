# HTTP Transport Configuration Fix

## Issue
HTTP mode was failing with error: `FastMCP.run() got an unexpected keyword argument 'host'`

## Root Cause
The FastMCP SDK (v1.19.0) has a simplified API:
- **Actual signature**: `FastMCP.run(transport, mount_path=None)`
- **Incorrect usage**: Passing `host`, `port`, `stateless_http` as run() parameters

## Solution
Configure HTTP server settings via `mcp.settings` **before** calling `run()`:

```python
# CORRECT ✅
def run_http():
    # Configure settings first
    mcp.settings.host = config.http.host
    mcp.settings.port = config.http.port
    mcp.settings.stateless_http = config.http.stateless
    
    # Then run with transport only
    mcp.run(transport="streamable-http")

# INCORRECT ❌
def run_http():
    # This fails - run() doesn't accept these parameters
    mcp.run(
        transport="streamable-http",
        host=config.http.host,              # ← Not supported
        port=config.http.port,              # ← Not supported
        stateless_http=config.http.stateless # ← Not supported
    )
```

## FastMCP API Documentation

According to the official [Python MCP SDK README](https://github.com/modelcontextprotocol/python-sdk):

### FastMCP.run() signature:
```python
def run(
    self, 
    transport: Literal['stdio', 'sse', 'streamable-http'] = 'stdio',
    mount_path: str | None = None
) -> None
```

### Parameters:
- **transport**: The transport mode to use
- **mount_path**: Optional path for SSE transport mounting (not used for streamable-http)

### Configuration via settings:
```python
# FastMCP settings control the HTTP server behavior
mcp.settings.host           # Server host (default: 0.0.0.0)
mcp.settings.port           # Server port (default: 8000)
mcp.settings.stateless_http # Stateless mode flag
```

## Examples from Official Documentation

### Streamable HTTP Transport Example:
```python
from mcp.server.fastmcp import FastMCP

# Stateful server (maintains session state)
mcp = FastMCP("StatefulServer")

# Stateless server (no session persistence)
# mcp = FastMCP("StatelessServer", stateless_http=True)

@mcp.tool()
def greet(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### Multiple Servers with Path Configuration:
```python
# Configure servers to mount at the root of each path
api_mcp.settings.streamable_http_path = "/"
chat_mcp.settings.streamable_http_path = "/"

# Mount the servers
app = Starlette(
    routes=[
        Mount("/api", app=api_mcp.streamable_http_app()),
        Mount("/chat", app=chat_mcp.streamable_http_app()),
    ]
)
```

## Testing

### Test 1: STDIO mode (control test)
```bash
$ bash run_stdio.sh
✅ Started successfully - used for Phase 5 validation
```

### Test 2: HTTP mode (before fix)
```bash
$ bash run_http.sh
❌ Error: FastMCP.run() got an unexpected keyword argument 'host'
```

### Test 3: HTTP mode (after fix)
```bash
$ timeout 5 bash run_http.sh
✅ Server started successfully on 0.0.0.0:3000
```

## Configuration Flow

```
Config File (config.yaml)
    ↓
YFinanceSettings class
    ↓ (http.host, http.port, http.stateless)
main.py run_http()
    ↓ (set mcp.settings.host/port/stateless_http)
FastMCP.settings
    ↓ (configure internal HTTP server)
mcp.run(transport="streamable-http")
    ↓ (start server with configured settings)
HTTP Server Running
```

## Files Modified

### main.py
```diff
- def run_http() -> NoReturn:
+ def run_http() -> NoReturn:
      """
      Run server in Streamable HTTP mode.
      ...
+     FastMCP.run() only accepts transport and mount_path parameters.
+     Host, port, and stateless_http must be configured via settings.
      """
+     # Configure FastMCP settings - these control the HTTP server
+     mcp.settings.host = config.http.host
+     mcp.settings.port = config.http.port
+     mcp.settings.stateless_http = config.http.stateless
+ 
-     # Run server - CORS is handled automatically by FastMCP
-     mcp.run(
-         transport="streamable-http",
-         host=config.http.host,
-         port=config.http.port,
-         stateless_http=config.http.stateless
-     )
+     # Run server with streamable-http transport
+     mcp.run(transport="streamable-http")
```

## CORS Handling

FastMCP automatically handles CORS for HTTP transport:
- Default: All origins allowed (`*`)
- Headers automatically exposed: `Mcp-Session-Id`
- Methods: `GET`, `POST`, `DELETE`

For custom CORS configuration:
```python
from starlette.middleware.cors import CORSMiddleware

starlette_app = CORSMiddleware(
    starlette_app,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST", "DELETE"],
    expose_headers=["Mcp-Session-Id"],
)
```

## Commit

**Commit**: 99907fe  
**Message**: `fix(http): correct FastMCP HTTP transport configuration`  
**Branch**: feat/phase5-documentation-final

## References

1. **FastMCP Documentation**: https://github.com/modelcontextprotocol/python-sdk#streamable-http-transport
2. **FastMCP API Signature** (inspected via Python):
   ```python
   >>> import inspect
   >>> from mcp.server.fastmcp import FastMCP
   >>> print(inspect.signature(FastMCP.run))
   (self, transport: "Literal['stdio', 'sse', 'streamable-http']" = 'stdio', 
    mount_path: 'str | None' = None) -> 'None'
   ```
3. **Example Servers**: 
   - examples/snippets/servers/streamable_config.py
   - examples/snippets/servers/streamable_starlette_mount.py

## Conclusion

✅ **HTTP transport now working correctly**  
✅ **Configuration follows FastMCP 1.19.0 API design**  
✅ **Both STDIO and HTTP modes functional**  
✅ **Phase 5 modernization complete with working dual transport**

---
**Date**: 2025-10-25  
**Author**: Pablo Toledo (via GitHub Copilot)  
**SDK Version**: FastMCP 1.19.0 (MCP Python SDK)

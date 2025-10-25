#!/usr/bin/env python3
"""
Main entry point for Yahoo Finance MCP Server.
Supports startup with STDIO or Streamable HTTP based on configuration.
"""
import sys
from typing import NoReturn

from src.config import config, TransportType
from src.server import mcp


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
    
    Note: Streamable HTTP is the modern transport replacing SSE.
    CORS is handled automatically by FastMCP for HTTP transport.
    
    FastMCP.run() only accepts transport and mount_path parameters.
    Host, port, and stateless_http must be configured via settings.
    """
    print("🌐 Starting server in Streamable HTTP mode...", file=sys.stderr)
    print(f"   Host: {config.http.host}", file=sys.stderr)
    print(f"   Port: {config.http.port}", file=sys.stderr)
    print(f"   Stateless: {config.http.stateless}", file=sys.stderr)
    print(f"   CORS: Enabled (all origins allowed by default)", file=sys.stderr)
    print(f"   Connect to: http://{config.http.host}:{config.http.port}/mcp", file=sys.stderr)

    # Configure FastMCP settings - these control the HTTP server
    # FastMCP.run() signature: run(transport, mount_path) 
    # Host/port/stateless are configured via settings, not run() parameters
    mcp.settings.host = config.http.host
    mcp.settings.port = config.http.port
    mcp.settings.stateless_http = config.http.stateless

    # Run server with streamable-http transport
    mcp.run(transport="streamable-http")


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

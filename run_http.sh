#!/bin/bash
# Run in HTTP mode for remote deployment

export YF_MCP_TRANSPORT=http
export YF_MCP_HTTP__HOST=0.0.0.0
export YF_MCP_HTTP__PORT=3000
export YF_MCP_HTTP__STATELESS=false
export YF_MCP_LOG_LEVEL=INFO

uv run python main.py

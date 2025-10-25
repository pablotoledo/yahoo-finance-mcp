#!/bin/bash
# Run in STDIO mode for Claude Desktop

export YF_MCP_TRANSPORT=stdio
export YF_MCP_LOG_LEVEL=INFO

uv run python main.py

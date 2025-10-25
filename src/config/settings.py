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
    stateless: bool = Field(default=False, description="Stateless mode (no session persistence)")
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
    enable_rate_limit: bool = Field(default=False, description="Enable rate limiting")
    requests_per_minute: int = Field(default=60, description="Max requests per minute")

    model_config = SettingsConfigDict(
        env_prefix="YF_MCP_",  # Environment variables: YF_MCP_TRANSPORT, etc.
        env_nested_delimiter="__",  # YF_MCP_HTTP__PORT
        case_sensitive=False
    )


# Global configuration instance
config = ServerConfig()

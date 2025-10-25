"""
Base models for Yahoo Finance MCP Server.
These models enable structured outputs with automatic validation.
"""
from pydantic import BaseModel, Field, ConfigDict


class TickerValidationError(BaseModel):
    """Error model for ticker validation failures."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Ticker 'INVALID' not found",
                "ticker": "INVALID",
                "suggestion": "Check the symbol or try the full ticker (e.g., AAPL.MX for Mexico)"
            }
        }
    )

    error: str = Field(..., description="Error message")
    ticker: str = Field(..., description="Ticker symbol that failed validation")
    suggestion: str | None = Field(None, description="Suggestion for fixing the error")


class AppContext(BaseModel):
    """Application context shared during server lifecycle."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cache: dict = Field(default_factory=dict, description="Cache for storing data")
    request_count: int = Field(default=0, description="Total number of requests processed")

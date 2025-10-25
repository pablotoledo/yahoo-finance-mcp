"""
Models for stock actions (dividends and splits).
"""
from pydantic import BaseModel, Field, ConfigDict


class StockActionPoint(BaseModel):
    """Single stock action data point."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-10-25",
                "dividends": 0.25,
                "stock_splits": None
            }
        }
    )

    date: str = Field(..., description="Date of the action")
    dividends: float | None = Field(None, description="Dividend amount")
    stock_splits: float | None = Field(None, description="Stock split ratio")


class StockActionsResponse(BaseModel):
    """Response containing stock actions data."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticker": "AAPL",
                "actions": [],
                "count": 5
            }
        }
    )

    ticker: str = Field(..., description="Ticker symbol")
    actions: list[StockActionPoint] = Field(..., description="List of stock actions")
    count: int = Field(..., description="Number of actions returned")


"""
Models for historical stock price data.
"""
from pydantic import BaseModel, Field


class HistoricalPricePoint(BaseModel):
    """Single historical price data point."""
    date: str = Field(..., description="Date of the price point")
    open: float | None = Field(None, description="Opening price")
    high: float | None = Field(None, description="Highest price")
    low: float | None = Field(None, description="Lowest price")
    close: float | None = Field(None, description="Closing price")
    volume: int | None = Field(None, description="Trading volume")
    adj_close: float | None = Field(None, alias="Adj Close", description="Adjusted closing price")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "date": "2025-10-25",
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 154.0,
                "volume": 1000000,
                "adj_close": 154.0
            }
        }


class HistoricalPriceResponse(BaseModel):
    """Response containing historical price data."""
    ticker: str = Field(..., description="Ticker symbol")
    period: str = Field(..., description="Time period queried")
    interval: str = Field(..., description="Data interval")
    data_points: list[HistoricalPricePoint] = Field(..., description="Historical price data points")
    count: int = Field(..., description="Number of data points returned")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "period": "1mo",
                "interval": "1d",
                "data_points": [],
                "count": 30
            }
        }

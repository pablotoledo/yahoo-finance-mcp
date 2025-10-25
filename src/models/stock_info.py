"""
Models for stock information data.
"""
from pydantic import BaseModel, Field


class StockInfoResponse(BaseModel):
    """Comprehensive stock information response."""
    # Basic identification
    symbol: str = Field(..., description="Stock ticker symbol")
    short_name: str | None = Field(None, description="Short company name")
    long_name: str | None = Field(None, description="Full company name")
    
    # Price & Trading Info
    current_price: float | None = Field(None, description="Current stock price")
    previous_close: float | None = Field(None, description="Previous closing price")
    open_price: float | None = Field(None, description="Today's opening price")
    day_low: float | None = Field(None, description="Today's low price")
    day_high: float | None = Field(None, description="Today's high price")
    volume: int | None = Field(None, description="Trading volume")
    average_volume: int | None = Field(None, description="Average trading volume")
    
    # Market Data
    market_cap: int | None = Field(None, description="Market capitalization")
    beta: float | None = Field(None, description="Beta (volatility measure)")
    pe_ratio: float | None = Field(None, description="Price-to-earnings ratio")
    eps: float | None = Field(None, description="Earnings per share")
    
    # Dividends
    dividend_rate: float | None = Field(None, description="Annual dividend rate")
    dividend_yield: float | None = Field(None, description="Dividend yield percentage")
    
    # Trading Range
    fifty_two_week_low: float | None = Field(None, description="52-week low price")
    fifty_two_week_high: float | None = Field(None, description="52-week high price")
    
    # Company Info
    sector: str | None = Field(None, description="Company sector")
    industry: str | None = Field(None, description="Company industry")
    website: str | None = Field(None, description="Company website")
    description: str | None = Field(None, description="Company description")
    
    # Additional metrics
    book_value: float | None = Field(None, description="Book value per share")
    price_to_book: float | None = Field(None, description="Price-to-book ratio")
    enterprise_value: int | None = Field(None, description="Enterprise value")
    profit_margins: float | None = Field(None, description="Profit margins")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "short_name": "Apple Inc.",
                "long_name": "Apple Inc.",
                "current_price": 150.25,
                "market_cap": 2500000000000,
                "pe_ratio": 25.5,
                "sector": "Technology"
            }
        }

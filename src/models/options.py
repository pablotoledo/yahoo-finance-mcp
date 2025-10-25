"""
Models for options data.
"""
from pydantic import BaseModel, Field


class OptionExpirationDatesResponse(BaseModel):
    """Response containing option expiration dates."""
    ticker: str = Field(..., description="Ticker symbol")
    expiration_dates: list[str] = Field(..., description="List of expiration dates")
    count: int = Field(..., description="Number of expiration dates")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "expiration_dates": ["2025-11-15", "2025-12-20"],
                "count": 2
            }
        }


class OptionContract(BaseModel):
    """Single option contract."""
    contract_symbol: str | None = Field(None, description="Contract symbol")
    strike: float | None = Field(None, description="Strike price")
    last_price: float | None = Field(None, description="Last traded price")
    bid: float | None = Field(None, description="Bid price")
    ask: float | None = Field(None, description="Ask price")
    volume: int | None = Field(None, description="Trading volume")
    open_interest: int | None = Field(None, description="Open interest")
    implied_volatility: float | None = Field(None, description="Implied volatility")
    in_the_money: bool | None = Field(None, description="Whether option is in the money")

    class Config:
        json_schema_extra = {
            "example": {
                "contract_symbol": "AAPL251115C00150000",
                "strike": 150.0,
                "last_price": 5.25,
                "volume": 1000,
                "in_the_money": True
            }
        }


class OptionChainResponse(BaseModel):
    """Response containing option chain data."""
    ticker: str = Field(..., description="Ticker symbol")
    expiration_date: str = Field(..., description="Expiration date")
    option_type: str = Field(..., description="Option type (calls or puts)")
    contracts: list[OptionContract] = Field(..., description="List of option contracts")
    count: int = Field(..., description="Number of contracts")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "expiration_date": "2025-11-15",
                "option_type": "calls",
                "contracts": [],
                "count": 50
            }
        }

"""
Models for financial statements.
"""
from pydantic import BaseModel, Field


class FinancialStatementResponse(BaseModel):
    """Response containing financial statement data."""
    ticker: str = Field(..., description="Ticker symbol")
    statement_type: str = Field(..., description="Type of financial statement")
    data: dict = Field(..., description="Financial statement data as key-value pairs")
    periods: list[str] = Field(..., description="List of periods covered")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "statement_type": "income_stmt",
                "data": {},
                "periods": ["2024", "2023", "2022"]
            }
        }

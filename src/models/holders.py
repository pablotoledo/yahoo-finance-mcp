"""
Models for holder information.
"""
from pydantic import BaseModel, Field


class HolderInfoResponse(BaseModel):
    """Response containing holder information."""
    ticker: str = Field(..., description="Ticker symbol")
    holder_type: str = Field(..., description="Type of holder information")
    data: dict = Field(..., description="Holder data as key-value pairs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "holder_type": "institutional_holders",
                "data": {}
            }
        }

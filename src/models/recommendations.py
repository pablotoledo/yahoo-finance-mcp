"""
Models for analyst recommendations.
"""
from pydantic import BaseModel, Field, ConfigDict


class RecommendationPoint(BaseModel):
    """Single recommendation data point."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-10-25",
                "firm": "Goldman Sachs",
                "to_grade": "Buy",
                "from_grade": "Hold",
                "action": "upgrade"
            }
        }
    )

    date: str = Field(..., description="Date of recommendation")
    firm: str | None = Field(None, description="Analyst firm")
    to_grade: str | None = Field(None, description="New grade/rating")
    from_grade: str | None = Field(None, description="Previous grade/rating")
    action: str | None = Field(None, description="Action (upgrade/downgrade/init)")


class RecommendationsResponse(BaseModel):
    """Response containing analyst recommendations."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticker": "AAPL",
                "recommendation_type": "upgrades_downgrades",
                "recommendations": [],
                "count": 10
            }
        }
    )

    ticker: str = Field(..., description="Ticker symbol")
    recommendation_type: str = Field(..., description="Type of recommendations")
    recommendations: list[RecommendationPoint] = Field(..., description="List of recommendations")
    count: int = Field(..., description="Number of recommendations")


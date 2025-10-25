"""
Models for news data.
"""
from pydantic import BaseModel, Field, ConfigDict


class NewsArticle(BaseModel):
    """Single news article."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Apple announces new product",
                "publisher": "Reuters",
                "link": "https://example.com/article",
                "publish_time": "2025-10-25T10:00:00Z",
                "type": "STORY"
            }
        }
    )

    title: str = Field(..., description="Article title")
    publisher: str | None = Field(None, description="Publisher name")
    link: str | None = Field(None, description="Article URL")
    publish_time: str | None = Field(None, description="Publication timestamp")
    type: str | None = Field(None, description="Article type")
    thumbnail: str | None = Field(None, description="Thumbnail image URL")
    related_tickers: list[str] | None = Field(None, description="Related ticker symbols")


class NewsListResponse(BaseModel):
    """Response containing list of news articles."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticker": "AAPL",
                "articles": [],
                "count": 10
            }
        }
    )

    ticker: str = Field(..., description="Ticker symbol")
    articles: list[NewsArticle] = Field(..., description="List of news articles")
    count: int = Field(..., description="Number of articles returned")

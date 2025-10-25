"""
Pydantic models for structured Yahoo Finance MCP Server responses.
"""
from .base import TickerValidationError, AppContext
from .historical import HistoricalPricePoint, HistoricalPriceResponse
from .stock_info import StockInfoResponse
from .news import NewsArticle, NewsListResponse
from .actions import StockActionPoint, StockActionsResponse
from .financials import FinancialStatementResponse
from .holders import HolderInfoResponse
from .options import (
    OptionExpirationDatesResponse,
    OptionContract,
    OptionChainResponse
)
from .recommendations import RecommendationPoint, RecommendationsResponse

__all__ = [
    # Base
    "TickerValidationError",
    "AppContext",
    # Historical
    "HistoricalPricePoint",
    "HistoricalPriceResponse",
    # Stock Info
    "StockInfoResponse",
    # News
    "NewsArticle",
    "NewsListResponse",
    # Actions
    "StockActionPoint",
    "StockActionsResponse",
    # Financials
    "FinancialStatementResponse",
    # Holders
    "HolderInfoResponse",
    # Options
    "OptionExpirationDatesResponse",
    "OptionContract",
    "OptionChainResponse",
    # Recommendations
    "RecommendationPoint",
    "RecommendationsResponse",
]

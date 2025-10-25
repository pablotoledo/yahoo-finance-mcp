"""
Unit tests for MCP server tools.
Tests all 9 core tools with mocked yfinance data.
"""
import pytest
from src.models import (
    HistoricalPriceResponse,
    StockInfoResponse,
    NewsListResponse,
    StockActionsResponse,
    FinancialStatementResponse,
    HolderInfoResponse,
    OptionExpirationDatesResponse,
    OptionChainResponse,
    RecommendationsResponse,
    TickerValidationError
)
from src.models.enums import FinancialType, HolderType, RecommendationType


class TestGetHistoricalStockPrices:
    """Tests for get_historical_stock_prices tool."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_structured_data(self, mock_yfinance_ticker):
        """Verify valid ticker returns HistoricalPriceResponse."""
        from src.server import get_historical_stock_prices
        
        result = await get_historical_stock_prices(ticker="AAPL", period="5d", interval="1d")
        
        assert isinstance(result, HistoricalPriceResponse)
        assert result.ticker == "AAPL"
        assert result.period == "5d"
        assert result.interval == "1d"
        assert result.count > 0
        assert len(result.data_points) > 0
        
        # Check first data point structure
        point = result.data_points[0]
        assert point.date is not None
        assert point.close is not None
        assert point.volume is not None

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_error(self, mock_yfinance_ticker):
        """Verify invalid ticker returns TickerValidationError."""
        from src.server import get_historical_stock_prices
        
        result = await get_historical_stock_prices(ticker="INVALID123", period="1d", interval="1d")
        
        assert isinstance(result, TickerValidationError)
        assert result.ticker == "INVALID123"
        assert "not found" in result.error.lower()
        assert result.suggestion is not None

    @pytest.mark.asyncio
    async def test_different_periods(self, mock_yfinance_ticker):
        """Test different time periods."""
        from src.server import get_historical_stock_prices
        
        for period in ["1d", "5d", "1mo", "1y"]:
            result = await get_historical_stock_prices(ticker="AAPL", period=period, interval="1d")
            assert isinstance(result, HistoricalPriceResponse)
            assert result.period == period


class TestGetStockInfo:
    """Tests for get_stock_info tool."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_info(self, mock_yfinance_ticker):
        """Verify valid ticker returns StockInfoResponse."""
        from src.server import get_stock_info
        
        result = await get_stock_info(ticker="AAPL")
        
        assert isinstance(result, StockInfoResponse)
        assert result.symbol == "AAPL"
        assert result.short_name == "Apple Inc."
        assert result.current_price == 150.25
        assert result.market_cap == 2500000000000
        assert result.sector == "Technology"

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_error(self, mock_yfinance_ticker):
        """Verify invalid ticker returns error."""
        from src.server import get_stock_info
        
        result = await get_stock_info(ticker="NOTREAL")
        
        assert isinstance(result, TickerValidationError)
        assert result.ticker == "NOTREAL"

    @pytest.mark.asyncio
    async def test_multiple_tickers(self, mock_yfinance_ticker):
        """Test fetching info for multiple tickers."""
        from src.server import get_stock_info
        
        for ticker in ["AAPL", "MSFT"]:
            result = await get_stock_info(ticker=ticker)
            assert isinstance(result, StockInfoResponse)
            assert result.symbol == ticker


class TestGetYahooFinanceNews:
    """Tests for get_yahoo_finance_news tool."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_news(self, mock_yfinance_ticker):
        """Verify valid ticker returns NewsListResponse."""
        from src.server import get_yahoo_finance_news
        
        result = await get_yahoo_finance_news(ticker="AAPL")
        
        assert isinstance(result, NewsListResponse)
        assert result.ticker == "AAPL"
        assert result.count >= 0
        if result.count > 0:
            assert len(result.articles) > 0
            article = result.articles[0]
            assert article.title is not None
            assert article.publisher is not None

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_error(self, mock_yfinance_ticker):
        """Verify invalid ticker returns error."""
        from src.server import get_yahoo_finance_news
        
        result = await get_yahoo_finance_news(ticker="INVALID123")
        
        assert isinstance(result, TickerValidationError)


class TestGetStockActions:
    """Tests for get_stock_actions tool."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_actions(self, mock_yfinance_ticker):
        """Verify valid ticker returns StockActionsResponse."""
        from src.server import get_stock_actions
        
        result = await get_stock_actions(ticker="AAPL")
        
        assert isinstance(result, StockActionsResponse)
        assert result.ticker == "AAPL"
        assert result.count >= 0
        if result.count > 0:
            action = result.actions[0]
            assert action.date is not None
            assert action.dividends is not None or action.stock_splits is not None


class TestGetFinancialStatement:
    """Tests for get_financial_statement tool."""

    @pytest.mark.asyncio
    async def test_income_statement(self, mock_yfinance_ticker):
        """Test income statement retrieval."""
        from src.server import get_financial_statement
        
        result = await get_financial_statement(
            ticker="AAPL",
            financial_type=FinancialType.income_stmt
        )
        
        assert isinstance(result, FinancialStatementResponse)
        assert result.ticker == "AAPL"
        assert result.statement_type == "income_stmt"
        assert len(result.periods) > 0
        assert len(result.data) > 0

    @pytest.mark.asyncio
    async def test_balance_sheet(self, mock_yfinance_ticker):
        """Test balance sheet retrieval."""
        from src.server import get_financial_statement
        
        result = await get_financial_statement(
            ticker="AAPL",
            financial_type=FinancialType.balance_sheet
        )
        
        assert isinstance(result, FinancialStatementResponse)
        assert result.statement_type == "balance_sheet"

    @pytest.mark.asyncio
    async def test_cashflow(self, mock_yfinance_ticker):
        """Test cash flow statement retrieval."""
        from src.server import get_financial_statement
        
        result = await get_financial_statement(
            ticker="AAPL",
            financial_type=FinancialType.cashflow
        )
        
        assert isinstance(result, FinancialStatementResponse)
        assert result.statement_type == "cashflow"


class TestGetHolderInfo:
    """Tests for get_holder_info tool."""

    @pytest.mark.asyncio
    async def test_major_holders(self, mock_yfinance_ticker):
        """Test major holders retrieval."""
        from src.server import get_holder_info
        
        result = await get_holder_info(
            ticker="AAPL",
            holder_type=HolderType.major_holders
        )
        
        assert isinstance(result, HolderInfoResponse)
        assert result.ticker == "AAPL"
        assert result.holder_type == "major_holders"
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_institutional_holders(self, mock_yfinance_ticker):
        """Test institutional holders retrieval."""
        from src.server import get_holder_info
        
        result = await get_holder_info(
            ticker="AAPL",
            holder_type=HolderType.institutional_holders
        )
        
        assert isinstance(result, HolderInfoResponse)
        assert result.holder_type == "institutional_holders"


class TestGetOptionExpirationDates:
    """Tests for get_option_expiration_dates tool."""

    @pytest.mark.asyncio
    async def test_valid_ticker_returns_dates(self, mock_yfinance_ticker):
        """Verify valid ticker returns expiration dates."""
        from src.server import get_option_expiration_dates
        
        result = await get_option_expiration_dates(ticker="AAPL")
        
        assert isinstance(result, OptionExpirationDatesResponse)
        assert result.ticker == "AAPL"
        assert result.count > 0
        assert len(result.expiration_dates) > 0

    @pytest.mark.asyncio
    async def test_invalid_ticker_returns_error(self, mock_yfinance_ticker):
        """Verify invalid ticker returns error."""
        from src.server import get_option_expiration_dates
        
        result = await get_option_expiration_dates(ticker="INVALID123")
        
        assert isinstance(result, TickerValidationError)


class TestGetOptionChain:
    """Tests for get_option_chain tool."""

    @pytest.mark.asyncio
    async def test_calls_option_chain(self, mock_yfinance_ticker, mock_options_dates):
        """Test calls option chain retrieval."""
        from src.server import get_option_chain
        
        result = await get_option_chain(
            ticker="AAPL",
            expiration_date=mock_options_dates[0],
            option_type="calls"
        )
        
        assert isinstance(result, OptionChainResponse)
        assert result.ticker == "AAPL"
        assert result.option_type == "calls"
        assert result.count >= 0
        if result.count > 0:
            contract = result.contracts[0]
            assert contract.strike is not None
            assert contract.last_price is not None

    @pytest.mark.asyncio
    async def test_puts_option_chain(self, mock_yfinance_ticker, mock_options_dates):
        """Test puts option chain retrieval."""
        from src.server import get_option_chain
        
        result = await get_option_chain(
            ticker="AAPL",
            expiration_date=mock_options_dates[0],
            option_type="puts"
        )
        
        assert isinstance(result, OptionChainResponse)
        assert result.option_type == "puts"


class TestGetRecommendations:
    """Tests for get_recommendations tool."""

    @pytest.mark.asyncio
    async def test_recommendations(self, mock_yfinance_ticker):
        """Test analyst recommendations retrieval."""
        from src.server import get_recommendations
        
        result = await get_recommendations(
            ticker="AAPL",
            recommendation_type=RecommendationType.recommendations
        )
        
        assert isinstance(result, RecommendationsResponse)
        assert result.ticker == "AAPL"
        assert result.recommendation_type == "recommendations"
        assert result.count >= 0

    @pytest.mark.asyncio
    async def test_upgrades_downgrades(self, mock_yfinance_ticker):
        """Test upgrades/downgrades retrieval."""
        from src.server import get_recommendations
        
        result = await get_recommendations(
            ticker="AAPL",
            recommendation_type=RecommendationType.upgrades_downgrades,
            months_back=12
        )
        
        assert isinstance(result, RecommendationsResponse)
        assert result.recommendation_type == "upgrades_downgrades"


class TestErrorHandling:
    """Tests for error handling across all tools."""

    @pytest.mark.asyncio
    async def test_empty_ticker_string(self, mock_yfinance_ticker):
        """Test handling of empty ticker string."""
        from src.server import get_stock_info
        
        result = await get_stock_info(ticker="")
        
        assert isinstance(result, TickerValidationError)

    @pytest.mark.asyncio
    async def test_special_characters_in_ticker(self, mock_yfinance_ticker):
        """Test handling of special characters."""
        from src.server import get_stock_info
        
        # Valid special characters (forex, crypto)
        for ticker in ["BTC-USD", "EURUSD=X", "^GSPC"]:
            result = await get_stock_info(ticker=ticker)
            # Should either return data or validation error, not crash
            assert isinstance(result, (StockInfoResponse, TickerValidationError))


@pytest.mark.asyncio
async def test_all_tools_have_structured_outputs(mock_yfinance_ticker):
    """Verify all tools return Pydantic models."""
    from src.server import (
        get_historical_stock_prices,
        get_stock_info,
        get_yahoo_finance_news,
        get_stock_actions,
        get_financial_statement,
        get_holder_info,
        get_option_expiration_dates,
        get_option_chain,
        get_recommendations
    )
    from pydantic import BaseModel
    
    # Test each tool returns Pydantic model
    tools_to_test = [
        (get_historical_stock_prices, {"ticker": "AAPL", "period": "1d", "interval": "1d"}),
        (get_stock_info, {"ticker": "AAPL"}),
        (get_yahoo_finance_news, {"ticker": "AAPL"}),
        (get_stock_actions, {"ticker": "AAPL"}),
        (get_financial_statement, {"ticker": "AAPL", "financial_type": FinancialType.income_stmt}),
        (get_holder_info, {"ticker": "AAPL", "holder_type": HolderType.major_holders}),
        (get_option_expiration_dates, {"ticker": "AAPL"}),
    ]
    
    for tool_func, params in tools_to_test:
        result = await tool_func(**params)
        assert isinstance(result, BaseModel), f"{tool_func.__name__} should return Pydantic model"

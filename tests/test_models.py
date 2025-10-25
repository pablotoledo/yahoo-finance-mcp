"""
Tests for Pydantic model validation and serialization.
"""
import pytest
from pydantic import ValidationError
from src.models import (
    TickerValidationError,
    HistoricalPricePoint,
    HistoricalPriceResponse,
    StockInfoResponse,
    NewsArticle,
    NewsListResponse,
    StockActionPoint,
    StockActionsResponse,
    OptionContract,
    OptionChainResponse
)


class TestTickerValidationError:
    """Tests for TickerValidationError model."""

    def test_valid_creation(self):
        """Test creating valid error model."""
        error = TickerValidationError(
            error="Ticker not found",
            ticker="INVALID",
            suggestion="Check the symbol"
        )
        
        assert error.error == "Ticker not found"
        assert error.ticker == "INVALID"
        assert error.suggestion == "Check the symbol"

    def test_without_suggestion(self):
        """Test creating error without suggestion."""
        error = TickerValidationError(
            error="API error",
            ticker="AAPL"
        )
        
        assert error.suggestion is None

    def test_json_serialization(self):
        """Test JSON serialization."""
        error = TickerValidationError(
            error="Test error",
            ticker="TEST"
        )
        
        json_data = error.model_dump()
        assert "error" in json_data
        assert "ticker" in json_data


class TestHistoricalPricePoint:
    """Tests for HistoricalPricePoint model."""

    def test_valid_creation(self):
        """Test creating valid price point."""
        point = HistoricalPricePoint(
            date="2025-10-25",
            open=150.0,
            high=155.0,
            low=149.0,
            close=154.0,
            volume=1000000,
            adj_close=154.0
        )
        
        assert point.date == "2025-10-25"
        assert point.open == 150.0
        assert point.volume == 1000000

    def test_optional_fields(self):
        """Test with optional fields as None."""
        point = HistoricalPricePoint(
            date="2025-10-25"
        )
        
        assert point.open is None
        assert point.volume is None

    def test_alias_support(self):
        """Test Adj Close alias."""
        point = HistoricalPricePoint(
            date="2025-10-25",
            **{"Adj Close": 150.0}
        )
        
        assert point.adj_close == 150.0


class TestHistoricalPriceResponse:
    """Tests for HistoricalPriceResponse model."""

    def test_valid_creation(self):
        """Test creating valid response."""
        points = [
            HistoricalPricePoint(date="2025-10-25", close=150.0),
            HistoricalPricePoint(date="2025-10-24", close=149.0)
        ]
        
        response = HistoricalPriceResponse(
            ticker="AAPL",
            period="1mo",
            interval="1d",
            data_points=points,
            count=2
        )
        
        assert response.ticker == "AAPL"
        assert response.count == 2
        assert len(response.data_points) == 2

    def test_empty_data_points(self):
        """Test with empty data points."""
        response = HistoricalPriceResponse(
            ticker="AAPL",
            period="1d",
            interval="1d",
            data_points=[],
            count=0
        )
        
        assert response.count == 0
        assert len(response.data_points) == 0


class TestStockInfoResponse:
    """Tests for StockInfoResponse model."""

    def test_valid_creation_full(self):
        """Test creating with all fields."""
        info = StockInfoResponse(
            symbol="AAPL",
            short_name="Apple Inc.",
            long_name="Apple Inc.",
            current_price=150.25,
            market_cap=2500000000000,
            sector="Technology",
            industry="Consumer Electronics",
            beta=1.2,
            pe_ratio=25.5
        )
        
        assert info.symbol == "AAPL"
        assert info.current_price == 150.25
        assert info.market_cap == 2500000000000

    def test_minimal_creation(self):
        """Test creating with only required field."""
        info = StockInfoResponse(symbol="AAPL")
        
        assert info.symbol == "AAPL"
        assert info.short_name is None
        assert info.current_price is None

    def test_json_schema_generation(self):
        """Test that JSON schema is generated correctly."""
        schema = StockInfoResponse.model_json_schema()
        
        assert "properties" in schema
        assert "symbol" in schema["properties"]
        assert "required" in schema
        assert "symbol" in schema["required"]


class TestNewsArticle:
    """Tests for NewsArticle model."""

    def test_valid_creation(self):
        """Test creating valid news article."""
        article = NewsArticle(
            title="Apple announces new product",
            publisher="Reuters",
            link="https://example.com/article",
            publish_time="2025-10-25T10:00:00Z",
            type="STORY"
        )
        
        assert article.title == "Apple announces new product"
        assert article.publisher == "Reuters"

    def test_optional_fields(self):
        """Test with only required fields."""
        article = NewsArticle(
            title="Breaking News"
        )
        
        assert article.title == "Breaking News"
        assert article.publisher is None
        assert article.link is None


class TestNewsListResponse:
    """Tests for NewsListResponse model."""

    def test_valid_creation(self):
        """Test creating news list response."""
        articles = [
            NewsArticle(title="Article 1"),
            NewsArticle(title="Article 2")
        ]
        
        response = NewsListResponse(
            ticker="AAPL",
            articles=articles,
            count=2
        )
        
        assert response.ticker == "AAPL"
        assert response.count == 2
        assert len(response.articles) == 2

    def test_empty_articles(self):
        """Test with no articles."""
        response = NewsListResponse(
            ticker="AAPL",
            articles=[],
            count=0
        )
        
        assert response.count == 0


class TestStockActionPoint:
    """Tests for StockActionPoint model."""

    def test_dividend_only(self):
        """Test action with dividend only."""
        action = StockActionPoint(
            date="2025-10-25",
            dividends=0.25,
            stock_splits=None
        )
        
        assert action.dividends == 0.25
        assert action.stock_splits is None

    def test_split_only(self):
        """Test action with split only."""
        action = StockActionPoint(
            date="2025-10-25",
            dividends=None,
            stock_splits=2.0
        )
        
        assert action.stock_splits == 2.0
        assert action.dividends is None


class TestOptionContract:
    """Tests for OptionContract model."""

    def test_valid_creation(self):
        """Test creating valid option contract."""
        contract = OptionContract(
            contract_symbol="AAPL251115C00150000",
            strike=150.0,
            last_price=5.25,
            bid=5.20,
            ask=5.30,
            volume=1000,
            open_interest=5000,
            implied_volatility=0.25,
            in_the_money=True
        )
        
        assert contract.strike == 150.0
        assert contract.in_the_money is True

    def test_all_optional(self):
        """Test with all fields as None."""
        contract = OptionContract()
        
        assert contract.strike is None
        assert contract.volume is None


class TestModelSerialization:
    """Tests for model serialization and deserialization."""

    def test_round_trip_serialization(self):
        """Test serialize and deserialize."""
        original = TickerValidationError(
            error="Test",
            ticker="AAPL"
        )
        
        # Serialize
        json_data = original.model_dump_json()
        
        # Deserialize
        restored = TickerValidationError.model_validate_json(json_data)
        
        assert restored.error == original.error
        assert restored.ticker == original.ticker

    def test_dict_conversion(self):
        """Test conversion to dict."""
        article = NewsArticle(
            title="Test Article",
            publisher="Test Publisher"
        )
        
        data = article.model_dump()
        
        assert isinstance(data, dict)
        assert data["title"] == "Test Article"
        assert data["publisher"] == "Test Publisher"

    def test_exclude_none_in_serialization(self):
        """Test excluding None values."""
        article = NewsArticle(title="Test")
        
        data = article.model_dump(exclude_none=True)
        
        assert "title" in data
        assert "publisher" not in data
        assert "link" not in data


class TestModelValidation:
    """Tests for Pydantic validation."""

    def test_required_field_missing(self):
        """Test validation error for missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            NewsListResponse(articles=[], count=0)  # Missing ticker
        
        error = exc_info.value
        assert "ticker" in str(error)

    def test_type_validation(self):
        """Test type validation."""
        with pytest.raises(ValidationError):
            HistoricalPricePoint(
                date="2025-10-25",
                open="not_a_number"  # Should be float
            )

    def test_port_range_validation(self):
        """Test custom validation (if any)."""
        from src.config.settings import HTTPConfig
        
        # Valid port
        config = HTTPConfig(port=3000)
        assert config.port == 3000
        
        # Invalid port (too low)
        with pytest.raises(ValidationError):
            HTTPConfig(port=100)
        
        # Invalid port (too high)
        with pytest.raises(ValidationError):
            HTTPConfig(port=70000)

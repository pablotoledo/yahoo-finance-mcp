"""
Shared fixtures for MCP server tests.
Uses in-memory session creation to avoid socket/network overhead.
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, MagicMock
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def mock_ticker_data():
    """Mock ticker data for tests."""
    return {
        "AAPL": {
            "shortName": "Apple Inc.",
            "longName": "Apple Inc.",
            "currentPrice": 150.25,
            "marketCap": 2500000000000,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "beta": 1.2,
            "trailingPE": 25.5,
            "dividendYield": 0.005,
            "fiftyTwoWeekHigh": 180.0,
            "fiftyTwoWeekLow": 120.0
        },
        "MSFT": {
            "shortName": "Microsoft Corporation",
            "longName": "Microsoft Corporation",
            "currentPrice": 380.50,
            "marketCap": 2800000000000,
            "sector": "Technology",
            "industry": "Software",
            "beta": 0.9,
            "trailingPE": 35.2,
            "dividendYield": 0.008,
            "fiftyTwoWeekHigh": 400.0,
            "fiftyTwoWeekLow": 300.0
        }
    }


@pytest.fixture
def mock_historical_data():
    """Mock historical price data."""
    dates = pd.date_range(end=datetime.now(), periods=5, freq='D')
    df = pd.DataFrame({
        'Open': [148.0, 149.0, 150.0, 151.0, 150.5],
        'High': [150.0, 151.0, 152.0, 153.0, 152.0],
        'Low': [147.0, 148.0, 149.0, 150.0, 149.5],
        'Close': [149.0, 150.0, 151.0, 152.0, 151.5],
        'Volume': [100000000, 110000000, 105000000, 95000000, 98000000],
        'Adj Close': [149.0, 150.0, 151.0, 152.0, 151.5]
    }, index=dates)
    df.index.name = 'Date'
    return df


@pytest.fixture
def mock_news_data():
    """Mock news data."""
    return [
        {
            "content": {
                "contentType": "STORY",
                "title": "Apple announces new product",
                "provider": {"displayName": "Reuters"},
                "canonicalUrl": {"url": "https://example.com/article1"},
                "thumbnail": {"resolutions": [{"url": "https://example.com/thumb1.jpg"}]}
            },
            "pubDate": datetime.now().isoformat(),
            "relatedTickers": ["AAPL"]
        },
        {
            "content": {
                "contentType": "STORY",
                "title": "Apple Q4 earnings beat expectations",
                "provider": {"displayName": "Bloomberg"},
                "canonicalUrl": {"url": "https://example.com/article2"}
            },
            "pubDate": (datetime.now() - timedelta(days=1)).isoformat(),
            "relatedTickers": ["AAPL"]
        }
    ]


@pytest.fixture
def mock_actions_data():
    """Mock stock actions (dividends and splits)."""
    dates = pd.date_range(end=datetime.now(), periods=3, freq='90D')
    df = pd.DataFrame({
        'Dividends': [0.23, 0.24, 0.25],
        'Stock Splits': [0.0, 0.0, 0.0]
    }, index=dates)
    df.index.name = 'Date'
    return df


@pytest.fixture
def mock_options_dates():
    """Mock option expiration dates."""
    today = datetime.now()
    return [
        (today + timedelta(days=30)).strftime('%Y-%m-%d'),
        (today + timedelta(days=60)).strftime('%Y-%m-%d'),
        (today + timedelta(days=90)).strftime('%Y-%m-%d')
    ]


@pytest.fixture
def mock_option_chain_data():
    """Mock option chain data."""
    return pd.DataFrame({
        'contractSymbol': ['AAPL251115C00150000', 'AAPL251115C00155000'],
        'strike': [150.0, 155.0],
        'lastPrice': [5.25, 3.50],
        'bid': [5.20, 3.45],
        'ask': [5.30, 3.55],
        'volume': [1000, 800],
        'openInterest': [5000, 3000],
        'impliedVolatility': [0.25, 0.28],
        'inTheMoney': [True, False]
    })


@pytest.fixture
def invalid_tickers():
    """List of invalid tickers for error tests."""
    return ["INVALID123", "NOTREAL", "BADTICKER", ""]


@pytest.fixture
def mock_yfinance_ticker(mocker, mock_ticker_data, mock_historical_data, 
                         mock_news_data, mock_actions_data, mock_options_dates,
                         mock_option_chain_data):
    """
    Mock yfinance.Ticker to avoid real API calls.
    Essential for fast, reliable tests without rate limits.
    """
    def create_mock_ticker(ticker):
        mock = MagicMock()
        
        # Valid ticker check
        if ticker in mock_ticker_data:
            mock.isin = "US0378331005"  # Valid ISIN
            mock.info = mock_ticker_data[ticker]
            mock.history.return_value = mock_historical_data
            mock.news = mock_news_data
            mock.actions = mock_actions_data
            mock.options = mock_options_dates
            
            # Mock option chain
            mock_chain = MagicMock()
            mock_chain.calls = mock_option_chain_data
            mock_chain.puts = mock_option_chain_data.copy()
            mock.option_chain.return_value = mock_chain
            
            # Mock financial statements
            dates = pd.date_range(end=datetime.now(), periods=3, freq='Y')
            mock.income_stmt = pd.DataFrame({
                dates[0]: {'Revenue': 100000000, 'Net Income': 20000000},
                dates[1]: {'Revenue': 110000000, 'Net Income': 22000000},
                dates[2]: {'Revenue': 120000000, 'Net Income': 24000000}
            })
            mock.balance_sheet = pd.DataFrame({
                dates[0]: {'Total Assets': 500000000, 'Total Debt': 100000000},
                dates[1]: {'Total Assets': 550000000, 'Total Debt': 110000000},
                dates[2]: {'Total Assets': 600000000, 'Total Debt': 120000000}
            })
            mock.cashflow = pd.DataFrame({
                dates[0]: {'Operating Cash Flow': 30000000},
                dates[1]: {'Operating Cash Flow': 33000000},
                dates[2]: {'Operating Cash Flow': 36000000}
            })
            
            # Mock holders
            mock.major_holders = pd.DataFrame({
                0: ['10%', '70%'],
                1: ['Insider', 'Institution']
            })
            mock.institutional_holders = pd.DataFrame({
                'Holder': ['Vanguard', 'BlackRock'],
                'Shares': [100000000, 90000000]
            })
            
            # Mock recommendations
            rec_dates = pd.date_range(end=datetime.now(), periods=5, freq='30D')
            mock.recommendations = pd.DataFrame({
                'Date': rec_dates,
                'Firm': ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Citi', 'BofA'],
                'To Grade': ['Buy', 'Buy', 'Hold', 'Buy', 'Buy'],
                'From Grade': ['Hold', 'Hold', 'Buy', 'Hold', 'Hold'],
                'Action': ['upgrade', 'upgrade', 'downgrade', 'upgrade', 'upgrade']
            })
            mock.upgrades_downgrades = mock.recommendations.copy()
            mock.upgrades_downgrades['GradeDate'] = rec_dates
            mock.upgrades_downgrades['ToGrade'] = mock.upgrades_downgrades['To Grade']
            mock.upgrades_downgrades['FromGrade'] = mock.upgrades_downgrades['From Grade']
            
        else:
            # Invalid ticker
            mock.isin = None
            mock.info = {}
            mock.history.return_value = pd.DataFrame()
            mock.news = []
            mock.actions = pd.DataFrame()
            mock.options = []
        
        return mock
    
    # Patch yfinance.Ticker
    mock_ticker_class = mocker.patch('yfinance.Ticker', side_effect=create_mock_ticker)
    return mock_ticker_class

"""
Yahoo Finance MCP Server - Modernized for MCP 1.19+
Supports structured outputs with Pydantic validation.
Protocol: 2025-06-18
"""
from contextlib import asynccontextmanager
from typing import Literal

import pandas as pd
import yfinance as yf
from mcp.server.fastmcp import FastMCP, Context

from src.models import (
    AppContext,
    TickerValidationError,
    HistoricalPricePoint,
    HistoricalPriceResponse,
    StockInfoResponse,
    NewsArticle,
    NewsListResponse,
    StockActionPoint,
    StockActionsResponse,
    FinancialStatementResponse,
    HolderInfoResponse,
    OptionExpirationDatesResponse,
    OptionContract,
    OptionChainResponse,
    RecommendationPoint,
    RecommendationsResponse,
)
from src.models.enums import FinancialType, HolderType, RecommendationType


# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Handles server initialization and cleanup."""
    context = AppContext()

    # Startup: initialize resources
    print("🚀 Yahoo Finance MCP Server v2.0 starting...")
    print(f"📊 yfinance version: {yf.__version__}")
    print(f"📡 MCP Protocol: 2025-06-18")
    print(f"🔧 Python SDK: 1.19+")

    try:
        yield context
    finally:
        # Cleanup: close connections, save cache, etc.
        print(f"📈 Total requests processed: {context.request_count}")
        print("👋 Server shutting down...")


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

mcp = FastMCP(
    "Yahoo Finance",
    lifespan=app_lifespan,
    instructions="""
# Yahoo Finance MCP Server (v2.0)

**Python SDK**: 1.19.0 | **Protocol**: 2025-06-18

Modernized MCP server for Yahoo Finance financial data with structured outputs.

## Key Features:
- ✅ Structured outputs with Pydantic validation
- ✅ Robust error handling with typed error models
- ✅ Structured logging via Context API
- ✅ Progress reporting for long operations
- ✅ Comprehensive data models for all tools

## Available Tools:
1. **get_historical_stock_prices** - Historical OHLCV prices
2. **get_stock_info** - Comprehensive stock information
3. **get_yahoo_finance_news** - Latest news articles
4. **get_stock_actions** - Dividends and stock splits
5. **get_financial_statement** - Financial statements (income, balance, cashflow)
6. **get_holder_info** - Ownership information
7. **get_option_expiration_dates** - Available option expiration dates
8. **get_option_chain** - Option chain data
9. **get_recommendations** - Analyst recommendations

## Supported Tickers:
- US Stocks: AAPL, MSFT, GOOGL, TSLA, etc.
- Indices: ^GSPC (S&P 500), ^DJI (Dow Jones)
- Crypto: BTC-USD, ETH-USD
- Forex: EURUSD=X
- International: Add suffix (e.g., AAPL.MX for Mexico)
""",
)


# ============================================================================
# TOOL 1: GET HISTORICAL STOCK PRICES
# ============================================================================

@mcp.tool(
    name="get_historical_stock_prices",
    description="Get historical OHLCV stock prices for a ticker symbol with structured output"
)
async def get_historical_stock_prices(
    ticker: str,
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1mo",
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"] = "1d",
    ctx: Context | None = None
) -> HistoricalPriceResponse | TickerValidationError:
    """
    Get historical price data for a stock.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        ctx: MCP context (auto-injected)

    Returns:
        HistoricalPriceResponse with data points or TickerValidationError
    """
    if ctx:
        await ctx.info(f"📊 Querying historical data for {ticker} (period={period}, interval={interval})")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker,
                suggestion="Check the symbol or try with exchange suffix (e.g., AAPL.MX for Mexico)"
            )

        # Get historical data
        hist_data = company.history(period=period, interval=interval)

        if hist_data.empty:
            return TickerValidationError(
                error=f"No data available for {ticker} in period {period}",
                ticker=ticker,
                suggestion="Try a different period or check if trading is active"
            )

        # Convert to structured format
        hist_data = hist_data.reset_index(names="Date")
        records = hist_data.to_dict(orient="records")

        data_points = [
            HistoricalPricePoint(
                date=str(rec["Date"]),
                open=float(rec["Open"]) if rec.get("Open") and not pd.isna(rec["Open"]) else None,
                high=float(rec["High"]) if rec.get("High") and not pd.isna(rec["High"]) else None,
                low=float(rec["Low"]) if rec.get("Low") and not pd.isna(rec["Low"]) else None,
                close=float(rec["Close"]) if rec.get("Close") and not pd.isna(rec["Close"]) else None,
                volume=int(rec["Volume"]) if rec.get("Volume") and not pd.isna(rec["Volume"]) else None,
                adj_close=float(rec.get("Adj Close")) if rec.get("Adj Close") and not pd.isna(rec.get("Adj Close")) else None
            )
            for rec in records
        ]

        if ctx:
            await ctx.info(f"✅ Returning {len(data_points)} data points for {ticker}")

        return HistoricalPriceResponse(
            ticker=ticker,
            period=period,
            interval=interval,
            data_points=data_points,
            count=len(data_points)
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting historical data for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 2: GET STOCK INFO
# ============================================================================

@mcp.tool(
    name="get_stock_info",
    description="Get comprehensive stock information including price, market cap, financials, and company details"
)
async def get_stock_info(
    ticker: str,
    ctx: Context | None = None
) -> StockInfoResponse | TickerValidationError:
    """
    Get comprehensive stock information.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        ctx: MCP context (auto-injected)

    Returns:
        StockInfoResponse with detailed information or TickerValidationError
    """
    if ctx:
        await ctx.info(f"📈 Querying stock info for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker,
                suggestion="Verify the ticker symbol is correct"
            )

        info = company.info

        if ctx:
            await ctx.info(f"✅ Retrieved info for {ticker}")

        return StockInfoResponse(
            symbol=ticker,
            short_name=info.get("shortName"),
            long_name=info.get("longName"),
            current_price=info.get("currentPrice"),
            previous_close=info.get("previousClose"),
            open_price=info.get("open"),
            day_low=info.get("dayLow"),
            day_high=info.get("dayHigh"),
            volume=info.get("volume"),
            average_volume=info.get("averageVolume"),
            market_cap=info.get("marketCap"),
            beta=info.get("beta"),
            pe_ratio=info.get("trailingPE"),
            eps=info.get("trailingEps"),
            dividend_rate=info.get("dividendRate"),
            dividend_yield=info.get("dividendYield"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            website=info.get("website"),
            description=info.get("longBusinessSummary"),
            book_value=info.get("bookValue"),
            price_to_book=info.get("priceToBook"),
            enterprise_value=info.get("enterpriseValue"),
            profit_margins=info.get("profitMargins")
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting stock info for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# Import remaining tools
import json

# ============================================================================
# TOOL 3: GET NEWS
# ============================================================================

@mcp.tool(
    name="get_yahoo_finance_news",
    description="Get latest news articles for a ticker symbol with structured output"
)
async def get_yahoo_finance_news(
    ticker: str,
    ctx: Context | None = None
) -> NewsListResponse | TickerValidationError:
    """
    Get news articles for a stock.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        ctx: MCP context (auto-injected)

    Returns:
        NewsListResponse with articles or TickerValidationError
    """
    if ctx:
        await ctx.info(f"📰 Querying news for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        news = company.news
        
        if not news:
            return NewsListResponse(ticker=ticker, articles=[], count=0)

        articles = []
        for item in news:
            if item.get("content", {}).get("contentType") == "STORY":
                content = item.get("content", {})
                articles.append(NewsArticle(
                    title=content.get("title"),
                    publisher=content.get("provider", {}).get("displayName"),
                    link=content.get("canonicalUrl", {}).get("url"),
                    publish_time=str(item.get("pubDate")) if item.get("pubDate") else None,
                    type=content.get("contentType"),
                    thumbnail=content.get("thumbnail", {}).get("resolutions", [{}])[0].get("url") if content.get("thumbnail") else None,
                    related_tickers=item.get("relatedTickers")
                ))

        if ctx:
            await ctx.info(f"✅ Found {len(articles)} news articles for {ticker}")

        return NewsListResponse(ticker=ticker, articles=articles, count=len(articles))

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting news for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 4: GET STOCK ACTIONS
# ============================================================================

@mcp.tool(
    name="get_stock_actions",
    description="Get stock dividends and splits with structured output"
)
async def get_stock_actions(
    ticker: str,
    ctx: Context | None = None
) -> StockActionsResponse | TickerValidationError:
    """
    Get stock actions (dividends and splits).

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        ctx: MCP context (auto-injected)

    Returns:
        StockActionsResponse with actions or TickerValidationError
    """
    if ctx:
        await ctx.info(f"💰 Querying stock actions for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)
        actions_df = company.actions

        if actions_df.empty:
            return StockActionsResponse(ticker=ticker, actions=[], count=0)

        actions_df = actions_df.reset_index(names="Date")
        records = actions_df.to_dict(orient="records")

        actions = [
            StockActionPoint(
                date=str(rec["Date"]),
                dividends=float(rec["Dividends"]) if rec.get("Dividends") and not pd.isna(rec["Dividends"]) else None,
                stock_splits=float(rec["Stock Splits"]) if rec.get("Stock Splits") and not pd.isna(rec["Stock Splits"]) else None
            )
            for rec in records
        ]

        if ctx:
            await ctx.info(f"✅ Found {len(actions)} stock actions for {ticker}")

        return StockActionsResponse(ticker=ticker, actions=actions, count=len(actions))

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting stock actions for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 5: GET FINANCIAL STATEMENT
# ============================================================================

@mcp.tool(
    name="get_financial_statement",
    description="Get financial statements (income statement, balance sheet, cash flow) with structured output"
)
async def get_financial_statement(
    ticker: str,
    financial_type: FinancialType,
    ctx: Context | None = None
) -> FinancialStatementResponse | TickerValidationError:
    """
    Get financial statement data.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        financial_type: Type of statement (income_stmt, balance_sheet, cashflow, etc.)
        ctx: MCP context (auto-injected)

    Returns:
        FinancialStatementResponse with data or TickerValidationError
    """
    if ctx:
        await ctx.info(f"📊 Querying {financial_type} for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        # Get appropriate statement
        if financial_type == FinancialType.income_stmt:
            statement = company.income_stmt
        elif financial_type == FinancialType.quarterly_income_stmt:
            statement = company.quarterly_income_stmt
        elif financial_type == FinancialType.balance_sheet:
            statement = company.balance_sheet
        elif financial_type == FinancialType.quarterly_balance_sheet:
            statement = company.quarterly_balance_sheet
        elif financial_type == FinancialType.cashflow:
            statement = company.cashflow
        elif financial_type == FinancialType.quarterly_cashflow:
            statement = company.quarterly_cashflow
        else:
            return TickerValidationError(
                error=f"Invalid financial type: {financial_type}",
                ticker=ticker
            )

        if statement.empty:
            return FinancialStatementResponse(
                ticker=ticker,
                statement_type=financial_type.value,
                data={},
                periods=[]
            )

        # Convert to dict structure
        data_dict = {}
        periods = []
        
        for column in statement.columns:
            if isinstance(column, pd.Timestamp):
                date_str = column.strftime("%Y-%m-%d")
            else:
                date_str = str(column)
            
            periods.append(date_str)
            data_dict[date_str] = {}
            
            for index, value in statement[column].items():
                data_dict[date_str][index] = None if pd.isna(value) else float(value) if isinstance(value, (int, float)) else str(value)

        if ctx:
            await ctx.info(f"✅ Retrieved {financial_type} for {ticker}")

        return FinancialStatementResponse(
            ticker=ticker,
            statement_type=financial_type.value,
            data=data_dict,
            periods=periods
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting financial statement for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 6: GET HOLDER INFO
# ============================================================================

@mcp.tool(
    name="get_holder_info",
    description="Get ownership information (institutional, mutual fund, insider) with structured output"
)
async def get_holder_info(
    ticker: str,
    holder_type: HolderType,
    ctx: Context | None = None
) -> HolderInfoResponse | TickerValidationError:
    """
    Get holder information.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        holder_type: Type of holder info (major_holders, institutional_holders, etc.)
        ctx: MCP context (auto-injected)

    Returns:
        HolderInfoResponse with data or TickerValidationError
    """
    if ctx:
        await ctx.info(f"👥 Querying {holder_type} for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        # Get appropriate holder data
        if holder_type == HolderType.major_holders:
            holders = company.major_holders
            data = holders.to_dict() if not holders.empty else {}
        elif holder_type == HolderType.institutional_holders:
            holders = company.institutional_holders
            data = holders.to_dict(orient="records") if not holders.empty else {}
        elif holder_type == HolderType.mutualfund_holders:
            holders = company.mutualfund_holders
            data = holders.to_dict(orient="records") if not holders.empty else {}
        elif holder_type == HolderType.insider_transactions:
            holders = company.insider_transactions
            data = holders.to_dict(orient="records") if not holders.empty else {}
        elif holder_type == HolderType.insider_purchases:
            holders = company.insider_purchases
            data = holders.to_dict(orient="records") if not holders.empty else {}
        elif holder_type == HolderType.insider_roster_holders:
            holders = company.insider_roster_holders
            data = holders.to_dict(orient="records") if not holders.empty else {}
        else:
            return TickerValidationError(
                error=f"Invalid holder type: {holder_type}",
                ticker=ticker
            )

        if ctx:
            await ctx.info(f"✅ Retrieved {holder_type} for {ticker}")

        return HolderInfoResponse(
            ticker=ticker,
            holder_type=holder_type.value,
            data=data
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting holder info for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 7: GET OPTION EXPIRATION DATES
# ============================================================================

@mcp.tool(
    name="get_option_expiration_dates",
    description="Get available option expiration dates with structured output"
)
async def get_option_expiration_dates(
    ticker: str,
    ctx: Context | None = None
) -> OptionExpirationDatesResponse | TickerValidationError:
    """
    Get option expiration dates.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        ctx: MCP context (auto-injected)

    Returns:
        OptionExpirationDatesResponse with dates or TickerValidationError
    """
    if ctx:
        await ctx.info(f"📅 Querying option expiration dates for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        dates = list(company.options)

        if ctx:
            await ctx.info(f"✅ Found {len(dates)} expiration dates for {ticker}")

        return OptionExpirationDatesResponse(
            ticker=ticker,
            expiration_dates=dates,
            count=len(dates)
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting option dates for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 8: GET OPTION CHAIN
# ============================================================================

@mcp.tool(
    name="get_option_chain",
    description="Get option chain (calls/puts) for a specific expiration date with structured output"
)
async def get_option_chain(
    ticker: str,
    expiration_date: str,
    option_type: Literal["calls", "puts"],
    ctx: Context | None = None
) -> OptionChainResponse | TickerValidationError:
    """
    Get option chain data.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        expiration_date: Expiration date (YYYY-MM-DD format)
        option_type: Type of options (calls or puts)
        ctx: MCP context (auto-injected)

    Returns:
        OptionChainResponse with contracts or TickerValidationError
    """
    if ctx:
        await ctx.info(f"⚡ Querying {option_type} option chain for {ticker} ({expiration_date})")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        # Check if expiration date is valid
        if expiration_date not in company.options:
            return TickerValidationError(
                error=f"No options available for date {expiration_date}",
                ticker=ticker,
                suggestion="Use get_option_expiration_dates to see available dates"
            )

        # Get option chain
        option_chain = company.option_chain(expiration_date)
        
        if option_type == "calls":
            chain_df = option_chain.calls
        else:
            chain_df = option_chain.puts

        if chain_df.empty:
            return OptionChainResponse(
                ticker=ticker,
                expiration_date=expiration_date,
                option_type=option_type,
                contracts=[],
                count=0
            )

        records = chain_df.to_dict(orient="records")
        
        contracts = [
            OptionContract(
                contract_symbol=rec.get("contractSymbol"),
                strike=float(rec["strike"]) if rec.get("strike") and not pd.isna(rec["strike"]) else None,
                last_price=float(rec["lastPrice"]) if rec.get("lastPrice") and not pd.isna(rec["lastPrice"]) else None,
                bid=float(rec["bid"]) if rec.get("bid") and not pd.isna(rec["bid"]) else None,
                ask=float(rec["ask"]) if rec.get("ask") and not pd.isna(rec["ask"]) else None,
                volume=int(rec["volume"]) if rec.get("volume") and not pd.isna(rec["volume"]) else None,
                open_interest=int(rec["openInterest"]) if rec.get("openInterest") and not pd.isna(rec["openInterest"]) else None,
                implied_volatility=float(rec["impliedVolatility"]) if rec.get("impliedVolatility") and not pd.isna(rec["impliedVolatility"]) else None,
                in_the_money=bool(rec.get("inTheMoney"))
            )
            for rec in records
        ]

        if ctx:
            await ctx.info(f"✅ Found {len(contracts)} {option_type} contracts for {ticker}")

        return OptionChainResponse(
            ticker=ticker,
            expiration_date=expiration_date,
            option_type=option_type,
            contracts=contracts,
            count=len(contracts)
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting option chain for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# TOOL 9: GET RECOMMENDATIONS
# ============================================================================

@mcp.tool(
    name="get_recommendations",
    description="Get analyst recommendations and upgrades/downgrades with structured output"
)
async def get_recommendations(
    ticker: str,
    recommendation_type: RecommendationType,
    months_back: int = 12,
    ctx: Context | None = None
) -> RecommendationsResponse | TickerValidationError:
    """
    Get analyst recommendations.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "MSFT")
        recommendation_type: Type (recommendations or upgrades_downgrades)
        months_back: Months of history for upgrades/downgrades (default: 12)
        ctx: MCP context (auto-injected)

    Returns:
        RecommendationsResponse with recommendations or TickerValidationError
    """
    if ctx:
        await ctx.info(f"⭐ Querying {recommendation_type} for {ticker}")
        ctx.request_context.lifespan_context.request_count += 1

    try:
        company = yf.Ticker(ticker)

        # Validate ticker
        if company.isin is None:
            if ctx:
                await ctx.warning(f"⚠️  Ticker {ticker} not found")
            return TickerValidationError(
                error=f"Ticker '{ticker}' not found",
                ticker=ticker
            )

        if recommendation_type == RecommendationType.recommendations:
            recs_df = company.recommendations
            if recs_df is None or recs_df.empty:
                return RecommendationsResponse(
                    ticker=ticker,
                    recommendation_type=recommendation_type.value,
                    recommendations=[],
                    count=0
                )
            
            records = recs_df.to_dict(orient="records")
            recommendations = [
                RecommendationPoint(
                    date=str(rec.get("Date")) if rec.get("Date") else None,
                    firm=rec.get("Firm"),
                    to_grade=rec.get("To Grade"),
                    from_grade=rec.get("From Grade"),
                    action=rec.get("Action")
                )
                for rec in records
            ]

        elif recommendation_type == RecommendationType.upgrades_downgrades:
            upgrades_df = company.upgrades_downgrades
            if upgrades_df is None or upgrades_df.empty:
                return RecommendationsResponse(
                    ticker=ticker,
                    recommendation_type=recommendation_type.value,
                    recommendations=[],
                    count=0
                )
            
            upgrades_df = upgrades_df.reset_index()
            cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months_back)
            upgrades_df = upgrades_df[upgrades_df["GradeDate"] >= cutoff_date]
            upgrades_df = upgrades_df.sort_values("GradeDate", ascending=False)
            latest_by_firm = upgrades_df.drop_duplicates(subset=["Firm"])
            
            records = latest_by_firm.to_dict(orient="records")
            recommendations = [
                RecommendationPoint(
                    date=str(rec.get("GradeDate")) if rec.get("GradeDate") else None,
                    firm=rec.get("Firm"),
                    to_grade=rec.get("ToGrade"),
                    from_grade=rec.get("FromGrade"),
                    action=rec.get("Action")
                )
                for rec in records
            ]
        else:
            return TickerValidationError(
                error=f"Invalid recommendation type: {recommendation_type}",
                ticker=ticker
            )

        if ctx:
            await ctx.info(f"✅ Found {len(recommendations)} recommendations for {ticker}")

        return RecommendationsResponse(
            ticker=ticker,
            recommendation_type=recommendation_type.value,
            recommendations=recommendations,
            count=len(recommendations)
        )

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Error getting recommendations for {ticker}: {str(e)}")
        return TickerValidationError(
            error=f"Internal error: {str(e)}",
            ticker=ticker
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import asyncio
    mcp.run()

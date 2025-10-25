#!/usr/bin/env python3
"""
Comprehensive test suite for Yahoo Finance MCP Server via STDIO
Tests all 9 tools with real data
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Test cases for each tool
TEST_CASES = [
    {
        "name": "get_historical_stock_prices",
        "description": "Test historical OHLCV data",
        "arguments": {"ticker": "AAPL", "period": "5d", "interval": "1d"}
    },
    {
        "name": "get_stock_info",
        "description": "Test comprehensive stock information",
        "arguments": {"ticker": "MSFT"}
    },
    {
        "name": "get_yahoo_finance_news",
        "description": "Test news retrieval",
        "arguments": {"ticker": "TSLA"}
    },
    {
        "name": "get_stock_actions",
        "description": "Test dividends and splits",
        "arguments": {"ticker": "AAPL"}
    },
    {
        "name": "get_financial_statement",
        "description": "Test financial statements",
        "arguments": {"ticker": "AAPL", "financial_type": "income_stmt"}
    },
    {
        "name": "get_holder_info",
        "description": "Test ownership information",
        "arguments": {"ticker": "AAPL", "holder_type": "major_holders"}
    },
    {
        "name": "get_option_expiration_dates",
        "description": "Test option dates",
        "arguments": {"ticker": "AAPL"}
    },
    {
        "name": "get_option_chain",
        "description": "Test option chain data",
        "arguments": {
            "ticker": "AAPL",
            "expiration_date": "2024-12-20",  # Will be set dynamically
            "option_type": "calls"
        },
        "requires_expiration": True
    },
    {
        "name": "get_recommendations",
        "description": "Test analyst recommendations",
        "arguments": {
            "ticker": "AAPL",
            "recommendation_type": "recommendations",
            "months_back": 3
        }
    }
]


async def test_all_tools_stdio():
    """Test all MCP tools via STDIO transport"""
    
    print("\n" + "="*80)
    print("🧪 Yahoo Finance MCP Server - Comprehensive STDIO Test Suite")
    print("="*80)
    print(f"🔧 Testing {len(TEST_CASES)} tools")
    print(f"📊 Transport: STDIO (stdin/stdout)\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "details": []
    }
    
    # Server parameters for STDIO
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "main.py"],
        env={"YF_MCP_TRANSPORT": "stdio", "YF_MCP_LOG_LEVEL": "WARNING"}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("🔌 Initializing MCP session...")
                init_result = await session.initialize()
                server_name = init_result.serverInfo.name
                server_version = init_result.serverInfo.version
                protocol_version = init_result.protocolVersion
                
                print(f"✅ Connected to: {server_name} v{server_version}")
                print(f"   Protocol: {protocol_version}\n")
                
                # List tools
                print("📋 Listing available tools...")
                tools_result = await session.list_tools()
                available_tools = {t.name: t for t in tools_result.tools}
                print(f"✅ Found {len(available_tools)} tools\n")
                
                # Store first expiration date for option chain test
                first_expiration = None
                
                # Test each tool
                for idx, test_case in enumerate(TEST_CASES, 1):
                    tool_name = test_case["name"]
                    description = test_case["description"]
                    arguments = test_case["arguments"].copy()
                    requires_expiration = test_case.get("requires_expiration", False)
                    
                    print(f"[{idx}/{len(TEST_CASES)}] 🔍 {tool_name}")
                    print(f"    📝 {description}")
                    
                    # Check if tool exists
                    if tool_name not in available_tools:
                        print(f"    ⚠️  Tool not found in server")
                        results["failed"] += 1
                        results["errors"].append({
                            "tool": tool_name,
                            "error": "Tool not available on server"
                        })
                        print()
                        continue
                    
                    # Handle dynamic arguments
                    if requires_expiration:
                        if first_expiration:
                            arguments["expiration_date"] = first_expiration
                            print(f"    📅 Using expiration: {first_expiration}")
                        else:
                            print(f"    ⚠️  Skipped: No expiration date available")
                            results["skipped"] += 1
                            print()
                            continue
                    
                    # Show arguments
                    args_str = json.dumps(arguments, indent=10)
                    print(f"    📦 Arguments:")
                    for line in args_str.split('\n')[:5]:
                        print(f"       {line}")
                    
                    try:
                        # Call the tool
                        result = await session.call_tool(tool_name, arguments)
                        
                        # Check for error
                        if result.isError:
                            error_content = result.content[0].text if result.content else "Unknown error"
                            print(f"    ❌ Tool Error: {error_content[:150]}")
                            results["failed"] += 1
                            results["errors"].append({
                                "tool": tool_name,
                                "error": error_content[:150]
                            })
                        else:
                            # Success!
                            print(f"    ✅ Success!")
                            
                            # Analyze result
                            detail = {
                                "tool": tool_name,
                                "status": "passed"
                            }
                            
                            # Content info
                            if result.content:
                                content_type = type(result.content[0]).__name__
                                print(f"       📄 Content type: {content_type}")
                                detail["content_type"] = content_type
                            
                            # Structured content analysis
                            if hasattr(result, 'structuredContent') and result.structuredContent:
                                structured = result.structuredContent
                                if isinstance(structured, dict):
                                    keys = list(structured.keys())
                                    print(f"       🔑 Structure keys ({len(keys)}): {', '.join(keys[:6])}")
                                    detail["keys"] = keys
                                    
                                    # Extract sample data
                                    if "ticker" in structured:
                                        print(f"       📊 Ticker: {structured['ticker']}")
                                    
                                    if "count" in structured:
                                        count = structured['count']
                                        print(f"       🔢 Count: {count}")
                                        detail["count"] = count
                                    
                                    if "data_points" in structured and structured.get("data_points"):
                                        points = structured["data_points"]
                                        print(f"       📈 Data points: {len(points)}")
                                        if points:
                                            first_point = points[0]
                                            if isinstance(first_point, dict):
                                                sample_keys = list(first_point.keys())[:4]
                                                print(f"          Sample keys: {sample_keys}")
                                    
                                    if "expiration_dates" in structured and structured.get("expiration_dates"):
                                        dates = structured["expiration_dates"]
                                        print(f"       📅 Expiration dates: {len(dates)}")
                                        if dates and not first_expiration:
                                            first_expiration = dates[0]
                                            print(f"       💾 Saved first date: {first_expiration}")
                                    
                                    if "news" in structured and structured.get("news"):
                                        news_items = structured["news"]
                                        print(f"       📰 News articles: {len(news_items)}")
                                        if news_items and isinstance(news_items[0], dict):
                                            first_news = news_items[0]
                                            if "title" in first_news:
                                                title = first_news["title"][:60]
                                                print(f"          First: {title}...")
                            
                            results["passed"] += 1
                            results["details"].append(detail)
                            
                    except Exception as e:
                        error_msg = str(e)[:150]
                        print(f"    ❌ Exception: {error_msg}")
                        results["failed"] += 1
                        results["errors"].append({
                            "tool": tool_name,
                            "error": error_msg
                        })
                    
                    print()  # Blank line
                    await asyncio.sleep(0.3)  # Small delay
                    
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return results
    
    # Print summary
    total = len(TEST_CASES)
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed:  {results['passed']}/{total}")
    print(f"❌ Failed:  {results['failed']}/{total}")
    print(f"⏭️  Skipped: {results['skipped']}/{total}")
    
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if results["errors"]:
        print(f"\n❌ Failed Tests ({len(results['errors'])}):")
        for idx, error in enumerate(results["errors"], 1):
            print(f"   {idx}. {error['tool']}")
            print(f"      {error['error']}")
    
    if results["passed"] > 0:
        print(f"\n✅ Passed Tests ({results['passed']}):")
        for detail in results["details"]:
            tool = detail["tool"]
            content_type = detail.get("content_type", "N/A")
            count = detail.get("count", "N/A")
            print(f"   • {tool} (content: {content_type}, count: {count})")
    
    print("="*80 + "\n")
    
    return results


async def main():
    """Main entry point"""
    try:
        results = await test_all_tools_stdio()
        
        # Exit with appropriate code
        if results["failed"] == 0:
            print("🎉 All tests passed successfully!")
            exit(0)
        elif results["passed"] > 0:
            print(f"⚠️  Partial success: {results['passed']} passed, {results['failed']} failed")
            exit(1)
        else:
            print(f"❌ All tests failed")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())

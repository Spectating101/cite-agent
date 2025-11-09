#!/usr/bin/env python3
"""
Example 2: Financial Data Retrieval

This example demonstrates how to:
- Get financial metrics for companies
- Retrieve SEC filings data
- Access historical financial information
"""

import asyncio
from cite_agent import EnhancedNocturnalAgent

async def main():
    """Financial data retrieval example"""

    # Initialize agent
    print("🚀 Initializing Cite-Agent...")
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Example 1: Get single financial metric
    ticker = "AAPL"
    metric = "revenue"

    print(f"\n📊 Getting {metric} data for {ticker}...")
    revenue_data = await agent.get_financial_data(ticker, metric, limit=4)

    if not revenue_data.get("error"):
        print(f"\n✅ {ticker} Revenue (Last 4 Quarters):\n")
        if "data" in revenue_data:
            for entry in revenue_data["data"]:
                period = entry.get("period", "N/A")
                value = entry.get("value", 0)
                print(f"   {period}: ${value:,.0f}M")
    else:
        print(f"❌ Error: {revenue_data['error']}")

    # Example 2: Get multiple financial metrics
    print(f"\n📈 Getting comprehensive financial metrics for {ticker}...")
    metrics = await agent.get_financial_metrics(
        ticker,
        metrics=["revenue", "grossProfit", "netIncome", "operatingIncome"]
    )

    if metrics:
        print(f"\n✅ {ticker} Financial Metrics:\n")
        for metric_name, metric_data in metrics.items():
            if "error" not in metric_data:
                print(f"   {metric_name}:")
                if "data" in metric_data and metric_data["data"]:
                    latest = metric_data["data"][0]
                    value = latest.get("value", 0)
                    period = latest.get("period", "N/A")
                    print(f"     Latest ({period}): ${value:,.0f}M")
            else:
                print(f"   {metric_name}: Error - {metric_data['error']}")
            print()

    # Example 3: Compare multiple companies
    print("\n📊 Comparing Tech Companies:")
    companies = ["AAPL", "MSFT", "GOOGL"]

    for company_ticker in companies:
        data = await agent.get_financial_data(company_ticker, "revenue", limit=1)
        if not data.get("error") and data.get("data"):
            latest = data["data"][0]
            value = latest.get("value", 0)
            period = latest.get("period", "N/A")
            print(f"   {company_ticker}: ${value:,.0f}M ({period})")

    # Clean up
    await agent.close()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())

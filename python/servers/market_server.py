from mcp.server.fastmcp import FastMCP
import random

mcp = FastMCP("market_server")

def mock_get_share_price(symbol: str) -> float:
    """Mock implementation of share price lookup."""
    # Simulate realistic stock prices
    base_prices = {
        "AAPL": 150.0,
        "MSFT": 300.0,
        "GOOGL": 2500.0,
        "AMZN": 3000.0,
        "TSLA": 200.0,
        "NVDA": 400.0,
        "META": 250.0,
        "SPY": 400.0,
        "QQQ": 350.0,
        "VTI": 200.0
    }
    
    base_price = base_prices.get(symbol.upper(), 100.0)
    # Add some randomness (+/- 5%)
    variation = random.uniform(0.95, 1.05)
    return round(base_price * variation, 2)

@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    """This tool provides the current price of the given stock symbol.

    Args:
        symbol: the symbol of the stock
    """
    return mock_get_share_price(symbol)

if __name__ == "__main__":
    mcp.run(transport='stdio')
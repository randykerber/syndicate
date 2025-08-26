from mcp.server.fastmcp import FastMCP
# from accounts import Account  # Note: accounts.py module would need to be ported separately

mcp = FastMCP("accounts_server")

# Mock Account class for now - would be replaced with actual implementation
class MockAccount:
    def __init__(self, name):
        self.name = name
        self.balance = 10000.0
        self.holdings = {"AAPL": 10, "MSFT": 5}
        self.strategy = "Conservative growth"
    
    @classmethod
    def get(cls, name):
        return cls(name)
    
    def buy_shares(self, symbol, quantity, rationale):
        # Mock implementation
        return f"Bought {quantity} shares of {symbol}. Rationale: {rationale}"
    
    def sell_shares(self, symbol, quantity, rationale):
        # Mock implementation
        return f"Sold {quantity} shares of {symbol}. Rationale: {rationale}"
    
    def change_strategy(self, strategy):
        self.strategy = strategy
        return f"Strategy changed to: {strategy}"
    
    def report(self):
        return f"Account: {self.name}, Balance: ${self.balance}, Holdings: {self.holdings}"
    
    def get_strategy(self):
        return self.strategy

@mcp.tool()
async def get_balance(name: str) -> float:
    """Get the cash balance of the given account name.

    Args:
        name: The name of the account holder
    """
    return MockAccount.get(name).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    """Get the holdings of the given account name.

    Args:
        name: The name of the account holder
    """
    return MockAccount.get(name).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Buy shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to buy
        rationale: The rationale for the purchase and fit with the account's strategy
    """
    return MockAccount.get(name).buy_shares(symbol, quantity, rationale)


@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Sell shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to sell
        rationale: The rationale for the sale and fit with the account's strategy
    """
    return MockAccount.get(name).sell_shares(symbol, quantity, rationale)

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> str:
    """At your discretion, if you choose to, call this to change your investment strategy for the future.

    Args:
        name: The name of the account holder
        strategy: The new strategy for the account
    """
    return MockAccount.get(name).change_strategy(strategy)

@mcp.resource("accounts://accounts_server/{name}")
async def read_account_resource(name: str) -> str:
    account = MockAccount.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    account = MockAccount.get(name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')
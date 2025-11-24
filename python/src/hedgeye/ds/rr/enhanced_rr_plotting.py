#!/usr/bin/env python3
"""
Enhanced plotting functions that include latest FMP price data.
Extends risk range plots with current market prices.
"""

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Optional

from hedgeye.config_loader import load_config
from hedgeye.ds.rr.use_rr import load_all_risk_range_data
from hedgeye.ds.rr.symbol_canonicalization import get_canonical_symbol_for_plotting, canonicalize_symbol
from hedgeye.ds.fmp.price_fetcher import get_prices_for_symbols

def load_symbol_mappings() -> pd.DataFrame:
    """Load the Hedgeye to FMP symbol mappings."""
    from hedgeye.config_loader import load_config
    
    config = load_config()
    fmp_path = Path(config["paths"]["fmp_mapping_file"])
    
    if not fmp_path.exists():
        raise FileNotFoundError(f"FMP mapping file not found: {fmp_path}")
        
    return pd.read_csv(fmp_path)

def get_latest_fmp_prices() -> pd.DataFrame:
    """Get latest prices for all mapped symbols."""
    mappings = load_symbol_mappings()
    
    try:
        latest_prices = get_prices_for_symbols(mappings, latest=True)
        print(f"Successfully fetched {len(latest_prices)} latest prices")
        return latest_prices
    except Exception as e:
        print(f"Error fetching latest prices: {e}")
        return pd.DataFrame()

def display_rr_with_latest_price(df: pd.DataFrame, index_symbol: str, 
                                latest_prices: Optional[pd.DataFrame] = None) -> plt.Figure:
    """
    Enhanced risk range plot that includes latest FMP price as additional data point.
    
    Args:
        df: Hedgeye risk range data
        index_symbol: Symbol to plot (e.g., 'AAPL', 'SPX')
        latest_prices: DataFrame with latest FMP prices (optional)
        
    Returns:
        matplotlib Figure object
    """
    # Get symbol data - handle case variations
    actual_symbol = get_canonical_symbol_for_plotting(df, index_symbol, 'index')
    
    if actual_symbol is None:
        print(f"No Hedgeye data found for symbol: {index_symbol}")
        return plt.figure()
    
    symbol_df = df[df["index"] == actual_symbol].copy()
    display_symbol = canonicalize_symbol(actual_symbol)  # Use canonical form for display
    
    # Prepare data
    symbol_df["date"] = pd.to_datetime(symbol_df["date"])
    symbol_df.sort_values("date", inplace=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot original risk range data
    ax.plot(symbol_df["date"], symbol_df["prev_close"], 
            label="Prev Close", color="black", linewidth=2)
    ax.plot(symbol_df["date"], symbol_df["buy_trade"], 
            label="Buy Trade", color="green", linewidth=1.5, linestyle="--")
    ax.plot(symbol_df["date"], symbol_df["sell_trade"], 
            label="Sell Trade", color="red", linewidth=1.5, linestyle="--")
    
    # Add latest FMP price if available - handle symbol variations
    if latest_prices is not None and not latest_prices.empty:
        # Try exact match first, then canonical form
        latest_price_row = latest_prices[latest_prices["he_symbol"] == index_symbol]
        if latest_price_row.empty:
            # Try with canonical form of the symbol
            canonical_symbol = canonicalize_symbol(index_symbol)
            latest_price_row = latest_prices[latest_prices["he_symbol"] == canonical_symbol]
        
        if not latest_price_row.empty:
            latest_price = latest_price_row.iloc[0]
            
            # Use current date/time for latest price
            latest_date = datetime.now()
            
            # Add latest price point
            ax.scatter(latest_date, latest_price["price"], 
                      color="blue", s=100, zorder=5, 
                      label=f"Latest Price: ${latest_price['price']:.2f}")
            
            # Connect latest price to most recent prev_close
            if len(symbol_df) > 0:
                last_date = symbol_df["date"].iloc[-1]
                last_close = symbol_df["prev_close"].iloc[-1]
                
                ax.plot([last_date, latest_date], [last_close, latest_price["price"]], 
                       color="blue", linewidth=2, alpha=0.7)
            
            # Add price annotation
            ax.annotate(f"${latest_price['price']:.2f}", 
                       xy=(latest_date, latest_price["price"]),
                       xytext=(10, 10), textcoords="offset points",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                       fontsize=10, fontweight="bold")
            
            # Show if price is in risk range
            if len(symbol_df) > 0:
                latest_buy = symbol_df["buy_trade"].iloc[-1]
                latest_sell = symbol_df["sell_trade"].iloc[-1]
                current_price = latest_price["price"]
                
                if current_price <= latest_buy:
                    status = "🟢 AT/BELOW BUY RANGE"
                    status_color = "green"
                elif current_price >= latest_sell:
                    status = "🔴 AT/ABOVE SELL RANGE"
                    status_color = "red"
                else:
                    status = "🟡 IN RANGE"
                    status_color = "orange"
                
                ax.text(0.02, 0.98, status, transform=ax.transAxes, 
                       fontsize=12, fontweight="bold", color=status_color,
                       verticalalignment="top",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Format the plot
    ax.set_title(f"Risk Range Time Series: {display_symbol}", fontsize=16, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    
    # Format dates on x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def generate_enhanced_plots(df: Optional[pd.DataFrame] = None, 
                          include_latest_prices: bool = True,
                          symbols_to_plot: Optional[list] = None):
    """
    Generate enhanced plots for all symbols with latest FMP prices.
    
    Args:
        df: Hedgeye risk range data (loads if None)
        include_latest_prices: Whether to fetch and include latest FMP prices
        symbols_to_plot: List of specific symbols to plot (plots all if None)
    """
    config = load_config()
    
    # Load data if not provided
    if df is None:
        df = load_all_risk_range_data()
    
    # Get latest prices if requested
    latest_prices = None
    if include_latest_prices:
        print("Fetching latest FMP prices...")
        latest_prices = get_latest_fmp_prices()
        
        if latest_prices.empty:
            print("⚠️  Could not fetch latest prices. Plots will show Hedgeye data only.")
            include_latest_prices = False
    
    # Determine symbols to plot
    if symbols_to_plot is None:
        # Filter to symbols with recent data
        max_days = config.get("plotting", {}).get("max_days_since_update", 7)
        cutoff_date = datetime.now() - timedelta(days=max_days)

        # Get most recent date for each symbol
        df["date"] = pd.to_datetime(df["date"])
        recent_symbols = df.groupby("index")["date"].max()
        recent_symbols = recent_symbols[recent_symbols >= cutoff_date].index.tolist()

        symbols = sorted(recent_symbols)
        print(f"Filtering to {len(symbols)} symbols with data in last {max_days} days")
    else:
        symbols = symbols_to_plot
    
    # Create output directory
    output_dir = Path(config["paths"]["plots_output_dir"])
    if include_latest_prices:
        output_dir = output_dir.parent / f"plots_with_fmp_{datetime.now().strftime('%Y%m%d')}"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean up old plots (remove any .png files not in our current symbol list)
    if output_dir.exists():
        existing_plots = list(output_dir.glob("*.png"))
        if existing_plots and symbols_to_plot is None:  # Only clean when auto-generating all
            safe_symbols = {sym.replace("/", "-").replace("^", "") for sym in symbols}
            for plot_path in existing_plots:
                plot_symbol = plot_path.stem
                if plot_symbol not in safe_symbols:
                    plot_path.unlink()
                    print(f"🗑️  Removed stale plot: {plot_symbol}.png")
    
    print(f"Generating {len(symbols)} enhanced plots...")
    
    successful_plots = 0
    failed_plots = 0
    
    for sym in symbols:
        try:
            fig = display_rr_with_latest_price(df, sym, latest_prices)
            
            # Save plot
            safe_symbol = sym.replace("/", "-").replace("^", "")
            out_path = output_dir / f"{safe_symbol}.png"
            
            fig.savefig(out_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Saved: {out_path}")
            successful_plots += 1
            
        except Exception as e:
            print(f"❌ Failed to create plot for {sym}: {e}")
            failed_plots += 1
    
    print(f"\n📊 Plot generation complete:")
    print(f"   ✅ Successful: {successful_plots}")
    print(f"   ❌ Failed: {failed_plots}")
    print(f"   📁 Output directory: {output_dir}")

def create_summary_dashboard(df: Optional[pd.DataFrame] = None, 
                           latest_prices: Optional[pd.DataFrame] = None):
    """
    Create a summary dashboard showing multiple symbols and their risk range status.
    """
    if df is None:
        df = load_all_risk_range_data()
    
    if latest_prices is None:
        latest_prices = get_latest_fmp_prices()
    
    # Get most recent risk range data for each symbol
    latest_rr = df.loc[df.groupby("index")["date"].idxmax()].copy()
    
    # Merge with FMP prices
    summary = latest_rr.merge(
        latest_prices, 
        left_on="index", 
        right_on="he_symbol", 
        how="left"
    )
    
    # Calculate risk range status
    def get_status(row):
        if pd.isna(row["price"]):
            return "No Price Data"
        
        current_price = row["price"]
        buy_level = row["buy_trade"]
        sell_level = row["sell_trade"]
        
        if current_price <= buy_level:
            return "BUY RANGE"
        elif current_price >= sell_level:
            return "SELL RANGE"
        else:
            return "IN RANGE"
    
    summary["status"] = summary.apply(get_status, axis=1)
    
    # Create dashboard plot
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Status distribution
    status_counts = summary["status"].value_counts()
    ax1.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
    ax1.set_title("Risk Range Status Distribution")
    
    # 2. Price vs Buy/Sell levels scatter
    valid_data = summary.dropna(subset=["price"])
    ax2.scatter(valid_data["buy_trade"], valid_data["price"], 
               color="green", alpha=0.6, label="Buy Level")
    ax2.scatter(valid_data["sell_trade"], valid_data["price"], 
               color="red", alpha=0.6, label="Sell Level")
    ax2.plot([valid_data["buy_trade"].min(), valid_data["buy_trade"].max()],
             [valid_data["buy_trade"].min(), valid_data["buy_trade"].max()],
             'k--', alpha=0.5)
    ax2.set_xlabel("Risk Range Level")
    ax2.set_ylabel("Current Price")
    ax2.set_title("Current Price vs Risk Range Levels")
    ax2.legend()
    
    # 3. Symbols by entity type
    if not latest_prices.empty:
        etype_counts = latest_prices["fmp_etype"].value_counts()
        ax3.bar(etype_counts.index, etype_counts.values)
        ax3.set_title("Symbols by Entity Type")
        ax3.tick_params(axis='x', rotation=45)
    
    # 4. Recent activity (symbols with data in last 7 days)
    recent_data = df[pd.to_datetime(df["date"]) >= (datetime.now() - timedelta(days=7))]
    recent_symbols = recent_data["index"].value_counts().head(10)
    ax4.barh(recent_symbols.index, recent_symbols.values)
    ax4.set_title("Most Active Symbols (Last 7 Days)")
    ax4.set_xlabel("Number of Updates")
    
    plt.tight_layout()
    
    # Save dashboard
    config = load_config()
    output_dir = Path(config["paths"]["plots_output_dir"]).parent
    dashboard_path = output_dir / f"risk_range_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    
    fig.savefig(dashboard_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"📊 Dashboard saved: {dashboard_path}")
    
    return summary

if __name__ == "__main__":
    # Test the enhanced plotting
    print("Testing enhanced plotting with FMP prices...")
    
    # Generate a few test plots
    test_symbols = ['AAPL', 'SPX', 'EURUSD']  # Mix of entity types
    generate_enhanced_plots(symbols_to_plot=test_symbols)
    
    # Create summary dashboard
    create_summary_dashboard()
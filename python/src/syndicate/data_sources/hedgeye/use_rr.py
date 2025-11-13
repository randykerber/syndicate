import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

from syndicate.data_sources.hedgeye.config_loader import load_config

def load_all_risk_range_data() -> pd.DataFrame:
    config = load_config()
    csv_dir = Path(config["paths"]["csv_output_dir"])
    all_files = list(csv_dir.glob("*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")
    df_list = [pd.read_csv(file) for file in all_files]
    return pd.concat(df_list, ignore_index=True)

def save_combined_risk_range_df(df: pd.DataFrame) -> None:
    config = load_config()
    output_path = Path(config["paths"]["combined_csv_output_dir"]) / "combined_risk_range.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

def display_rr_1(df: pd.DataFrame, sym: str) -> None:
    df_sym = df[df["index"] == sym].copy()
    if df_sym.empty:
        print(f"No data found for index: {sym}")
        return

    # Ensure date is datetime type and sort
    df_sym["date"] = pd.to_datetime(df_sym["date"])
    df_sym.sort_values("date", inplace=True)

    plt.figure(figsize=(12, 6))
    plt.plot(df_sym["date"], df_sym["prev_close"], label="Prev Close", color="black")
    plt.plot(df_sym["date"], df_sym["buy_trade"], label="Buy Trade", color="green")
    plt.plot(df_sym["date"], df_sym["sell_trade"], label="Sell Trade", color="red")

    plt.title(f"Risk Range Time Series: {sym}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def display_rr(df: pd.DataFrame, index_symbol: str) -> plt.Figure:
    symbol_df = df[df["index"] == index_symbol].copy()
    symbol_df["date"] = pd.to_datetime(symbol_df["date"])
    symbol_df.sort_values("date", inplace=True)

    fig, ax = plt.subplots()
    ax.plot(symbol_df["date"], symbol_df["prev_close"], label="Prev Close", color="black")
    ax.plot(symbol_df["date"], symbol_df["buy_trade"], label="Buy Trade", color="green")
    ax.plot(symbol_df["date"], symbol_df["sell_trade"], label="Sell Trade", color="red")

    ax.set_title(f"Risk Range Time Series: {index_symbol}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    return fig

def generate_all_plots(df: pd.DataFrame = None):
    """Generate plots for all symbols. If df not provided, loads data internally."""
    config = load_config()

    if df is None:
        df = load_all_risk_range_data()
    
    symbols = sorted(df["index"].unique())

    output_dir = Path(config["paths"]["plots_output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    for sym in symbols:
        fig = display_rr(df, sym)  # returns a matplotlib Figure

        safe_symbol = sym.replace("/", "-")
        out_path = output_dir / f"{safe_symbol}.png"

        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"Saved plot: {out_path}")


# Using:
#
# df = load_all_risk_range_data()
# save_combined_risk_range_df(df)


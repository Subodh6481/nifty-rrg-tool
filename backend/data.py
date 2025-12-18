import yfinance as yf
import pandas as pd


# Central place for all sector tickers
SECTOR_TICKERS = {
    "Bank": "^NSEBANK",
    "PSU Bank": "^NSEBANK",   # fallback if no dedicated PSU index
    "IT": "^CNXIT",
    "FMCG": "^CNXFMCG",
    "Pharma": "^CNXPHARMA",
    "Auto": "^CNXAUTO",
    "Metal": "^CNXMETAL",
    "Realty": "^CNXREALTY",
    "Energy": "^CNXENERGY",
    "Media": "^CNXMEDIA",
}


def load_price_data(
    sectors: dict,
    benchmark: str,
    period: str = "6mo"
) -> dict:
    """
    Fetch adjusted close price data for sectors + benchmark.

    Args:
        sectors: Dictionary mapping sector names to tickers, e.g., {"IT": "^CNXIT", "Bank": "^NSEBANK"}
        benchmark: Benchmark ticker symbol, e.g., "^NSEI"
        period: Time period for data, e.g., "6mo"

    Returns:
        Dictionary with benchmark and sector DataFrames:
        {
            "^NSEI": pd.DataFrame,
            "IT": pd.DataFrame,
            "Bank": pd.DataFrame,
            ...
        }
    """

    data = {}

    # --- Benchmark ---
    try:
        benchmark_df = yf.download(
            benchmark,
            period=period,
            progress=False,
            auto_adjust=True
        )

        # Handle MultiIndex columns if present
        if isinstance(benchmark_df.columns, pd.MultiIndex):
            benchmark_df.columns = benchmark_df.columns.droplevel(1)

        if benchmark_df.empty:
            raise ValueError(f"No data returned for benchmark {benchmark}")

        if "Close" not in benchmark_df.columns:
            raise ValueError(f"Benchmark data missing Close column. Available columns: {benchmark_df.columns.tolist()}")

        data[benchmark] = benchmark_df

    except Exception as e:
        raise ValueError(f"Failed to load benchmark data for {benchmark}: {str(e)}")

    # --- Sector data ---
    for sector, ticker in sectors.items():
        try:
            df = yf.download(
                ticker,
                period=period,
                progress=False,
                auto_adjust=True
            )

            # Handle MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            if df.empty:
                print(f"Warning: No data returned for sector {sector} ({ticker})")
                continue

            if "Close" not in df.columns:
                print(f"Warning: Sector {sector} data missing Close column. Available columns: {df.columns.tolist()}")
                continue

            data[sector] = df

        except Exception as e:
            print(f"Warning: Failed to load data for sector {sector} ({ticker}): {str(e)}")
            continue

    if len(data) <= 1:  # Only benchmark, no sectors
        raise ValueError("No sector data could be loaded. Please check your internet connection and try again.")

    return data

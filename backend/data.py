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
    benchmark_df = yf.download(
        benchmark,
        period=period,
        progress=False
    )

    if benchmark_df.empty or "Close" not in benchmark_df:
        raise ValueError("Benchmark data missing Close column")

    data[benchmark] = benchmark_df

    # --- Sector data ---
    for sector, ticker in sectors.items():
        df = yf.download(
            ticker,
            period=period,
            progress=False
        )

        if df.empty or "Close" not in df:
            continue

        data[sector] = df

    return data

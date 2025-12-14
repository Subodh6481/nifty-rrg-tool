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
    sectors: list[str],
    benchmark: str,
    period: str = "6mo"
) -> dict:
    """
    Fetch adjusted close price data for sectors + benchmark.

    Returns:
        {
            "benchmark": pd.Series,
            "sectors": {
                "IT": pd.Series,
                "Bank": pd.Series,
                ...
            }
        }
    """

    data = {
        "benchmark": None,
        "sectors": {}
    }

    # --- Benchmark ---
    benchmark_df = yf.download(
        benchmark,
        period=period,
        progress=False
    )

    if "Close" not in benchmark_df:
        raise ValueError("Benchmark data missing Close column")

    data["benchmark"] = benchmark_df["Close"]

    # --- Sector data ---
    for sector in sectors:
        ticker = SECTOR_TICKERS.get(sector)

        if not ticker:
            continue

        df = yf.download(
            ticker,
            period=period,
            progress=False
        )

        if "Close" not in df:
            continue

        data["sectors"][sector] = df["Close"]

    return data

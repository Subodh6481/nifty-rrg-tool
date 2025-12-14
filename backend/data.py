# backend/data.py

import yfinance as yf
import pandas as pd


def fetch_price_series(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d"
) -> pd.Series:
    """
    Fetch Close price series for a given ticker.
    """

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")

    if "Close" not in df.columns:
        raise ValueError(f"'Close' column missing for ticker: {ticker}")

    series = df["Close"].dropna()

    if len(series) < 50:
        raise ValueError(f"Not enough data for ticker: {ticker}")

    return series

import pandas as pd
import numpy as np


def calculate_rrg(
    data: dict,
    benchmark: str,
    rs_period: int,
    roc_period: int,
    tail_length: int
) -> dict:
    """
    Calculate RRG metrics with multi-point history.

    data = {
        "benchmark": pd.Series,
        "sectors": {
            "IT": pd.Series,
            "Bank": pd.Series,
            ...
        }
    }

    Returns:
        {
            "IT": DataFrame(rs_ratio, rs_momentum),
            "Bank": DataFrame(...),
            ...
        }
    """

    benchmark_prices = data["benchmark"]
    sector_prices = data["sectors"]

    results = {}

    # --- Benchmark returns ---
    benchmark_ret = benchmark_prices.pct_change()

    for sector, prices in sector_prices.items():

        # Align dates
        df = pd.concat(
            [prices, benchmark_prices],
            axis=1,
            join="inner"
        )
        df.columns = ["sector", "benchmark"]

        # Relative strength
        rs = (df["sector"] / df["benchmark"]) * 100
        rs_ema = rs.ewm(span=rs_period, adjust=False).mean()

        # RS Momentum
        rs_roc = rs_ema.pct_change(periods=roc_period) * 100 + 100

        rrg_df = pd.DataFrame({
            "rs_ratio": rs_ema,
            "rs_momentum": rs_roc
        }).dropna()

        # Keep tail
        if len(rrg_df) >= tail_length:
            rrg_df = rrg_df.iloc[-tail_length:]

        results[sector] = rrg_df

    return results

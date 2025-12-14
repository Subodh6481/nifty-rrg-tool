import pandas as pd
import numpy as np


def calculate_rrg(data, rs_period, roc_period, tail_length):
    """
    Returns multi-point RRG history per sector.
    Output columns: sector, rs_ratio, rs_momentum
    """

    records = []

    benchmark_df = data["^NSEI"]
    benchmark_close = benchmark_df["Close"]

    for sector, df in data.items():
        if sector == "^NSEI":
            continue

        rel = df["Close"] / benchmark_close
        rel = rel.dropna()

        # RS-Ratio (EMA normalized to 100)
        rs_ratio = (
            rel / rel.ewm(span=rs_period, adjust=False).mean()
        ) * 100

        # RS-Momentum (ROC normalized to 100)
        rs_momentum = (
            rs_ratio / rs_ratio.shift(roc_period)
        ) * 100

        rrg_df = pd.DataFrame({
            "sector": sector,
            "rs_ratio": rs_ratio,
            "rs_momentum": rs_momentum
        }).dropna()

        # keep only tail
        rrg_df = rrg_df.tail(tail_length)

        records.append(rrg_df)

    df = pd.concat(records, ignore_index=True)

    # ✅ validate AFTER creation
    required_cols = {"sector", "rs_ratio", "rs_momentum"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in RRG data: {missing}")

    return df


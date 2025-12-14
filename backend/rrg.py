# backend/rrg.py

import pandas as pd


def calculate_rrg(
    data: dict,
    benchmark: str,
    ma_period: int,
    roc_period: int,
    tail_length: int,
):
    """
    Calculate JdK RS-Ratio and RS-Momentum safely with index alignment.
    """

    benchmark_price = data[benchmark]
    results = []

    for name, series in data.items():
        if name == benchmark:
            continue

        # -----------------------------
        # CRITICAL: align dates
        # -----------------------------
        aligned = pd.concat(
            [series, benchmark_price],
            axis=1,
            join="inner"
        ).dropna()

        if aligned.shape[0] < max(ma_period, roc_period) + 5:
            # Not enough data to calculate indicators safely
            continue

        asset_price = aligned.iloc[:, 0]
        bench_price = aligned.iloc[:, 1]

        # -----------------------------
        # RRG calculations
        # -----------------------------
        rs = asset_price / bench_price

        rs_ratio = rs.ewm(
            span=ma_period,
            adjust=False
        ).mean() * 100

        rs_momentum = (
            rs_ratio.pct_change(roc_period) * 100 + 100
        )

        df = pd.DataFrame(
            {
                "rs_ratio": rs_ratio,
                "rs_momentum": rs_momentum,
            }
        ).dropna()

        if df.empty:
            continue

        tail_df = df.tail(tail_length)

        results.append(
            {
                "name": name,
                "history": tail_df.values.tolist(),
                "latest": {
                    "rs_ratio": float(tail_df.iloc[-1]["rs_ratio"]),
                    "rs_momentum": float(tail_df.iloc[-1]["rs_momentum"]),
                },
            }
        )

    if not results:
        raise ValueError("No valid RRG data could be computed.")

    return results

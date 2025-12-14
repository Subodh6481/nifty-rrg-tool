# backend/rrg.py

import pandas as pd


def calculate_rrg(
    data: dict,
    benchmark: str,
    ma_period: int,
    roc_period: int,
    tail_length: int
):
    """
    Calculate JdK RS-Ratio and RS-Momentum for RRG.
    """

    benchmark_price = data[benchmark]
    results = []

    for name, series in data.items():
        if name == benchmark:
            continue

        rs = series / benchmark_price
        rs_ratio = rs.ewm(span=ma_period, adjust=False).mean() * 100
        rs_momentum = rs_ratio.pct_change(roc_period) * 100 + 100

        df = pd.DataFrame(
            {
                "rs_ratio": rs_ratio,
                "rs_momentum": rs_momentum,
            }
        ).dropna()

        tail_df = df.tail(tail_length)

        results.append(
            {
                "name": name,
                "history": tail_df.values.tolist(),
                "latest": tail_df.iloc[-1].to_dict(),
            }
        )

    return results

# backend/rrg.py

import pandas as pd


def calculate_rrg(data, benchmark, ma_period, roc_period, tail_length):
    results = []

    benchmark_prices = data[benchmark]

    for sector, prices in data.items():
        if sector == benchmark:
            continue

        # --------------------------------------------------
        # 1. Relative Strength
        # --------------------------------------------------
        rs = prices / benchmark_prices

        # --------------------------------------------------
        # 2. JdK RS-Ratio (EMA normalized)
        # --------------------------------------------------
        rs_ema = rs.ewm(span=ma_period, adjust=False).mean()
        rs_ratio = 100 * (rs_ema / rs_ema.mean())

        # --------------------------------------------------
        # 3. JdK RS-Momentum (ROC of RS-Ratio)
        # --------------------------------------------------
        rs_momentum = 100 + rs_ratio.pct_change(roc_period) * 100

        # --------------------------------------------------
        # 4. CLEAN + ALIGN
        # --------------------------------------------------
        df = (
            pd.DataFrame({
                "rs_ratio": rs_ratio,
                "rs_momentum": rs_momentum
            })
            .dropna()
        )

        # ❗ Critical safety check
        if len(df) < tail_length:
            continue

        # --------------------------------------------------
        # 5. BUILD HISTORY (THIS IS THE FIX)
        # --------------------------------------------------
        tail = df.iloc[-tail_length:]

        history = list(
            zip(
                tail["rs_ratio"].values,
                tail["rs_momentum"].values
            )
        )

        results.append({
            "name": sector,
            "history": history
        })

    return results


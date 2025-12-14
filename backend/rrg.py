import pandas as pd

def calculate_rrg(data, benchmark, ma_period, roc_period, tail_length):
    results = []

    # -----------------------------
    # Extract benchmark CLOSE series
    # -----------------------------
    benchmark_df = data[benchmark]

    if isinstance(benchmark_df, pd.DataFrame):
        benchmark_prices = benchmark_df["Close"]
    else:
        benchmark_prices = benchmark_df

    for sector, sector_df in data.items():
        if sector == benchmark:
            continue

        # -----------------------------
        # Extract sector CLOSE series
        # -----------------------------
        if isinstance(sector_df, pd.DataFrame):
            prices = sector_df["Close"]
        else:
            prices = sector_df

        # -----------------------------
        # Align dates (CRITICAL)
        # -----------------------------
        prices, benchmark_aligned = prices.align(benchmark_prices, join="inner")

        if len(prices) < max(ma_period, roc_period) + tail_length:
            continue

        # -----------------------------
        # Relative Strength
        # -----------------------------
        rs = prices / benchmark_aligned

        # -----------------------------
        # JdK RS-Ratio
        # -----------------------------
        rs_ema = rs.ewm(span=ma_period, adjust=False).mean()
        rs_ratio = 100 * (rs_ema / rs_ema.mean())

        # -----------------------------
        # JdK RS-Momentum
        # -----------------------------
        rs_momentum = 100 + rs_ratio.pct_change(roc_period) * 100

        # -----------------------------
        # Combine + clean
        # -----------------------------
        df = pd.DataFrame({
            "rs_ratio": rs_ratio,
            "rs_momentum": rs_momentum
        }).dropna()

        if len(df) < tail_length:
            continue

        # -----------------------------
        # Build tail history (FIX)
        # -----------------------------
        tail = df.iloc[-tail_length:]

        history = list(zip(
            tail["rs_ratio"].values,
            tail["rs_momentum"].values
        ))

        results.append({
            "name": sector,
            "history": history
        })

    return results

import pandas as pd

def calculate_rrg(data, benchmark, ma_period, roc_period, tail_length):
    results = []

    benchmark_prices = data[benchmark]

    # 🔒 SAFETY: ensure benchmark is a Series
    if not isinstance(benchmark_prices, pd.Series):
        benchmark_prices = pd.Series(benchmark_prices)

    for sector, prices in data.items():
        if sector == benchmark:
            continue

        # 🔒 SAFETY: ensure prices is a Series
        if not isinstance(prices, pd.Series):
            prices = pd.Series(prices)

        # 🔒 ALIGN indices (CRITICAL)
        prices, benchmark_aligned = prices.align(benchmark_prices, join="inner")

        if len(prices) < max(ma_period, roc_period) + tail_length:
            continue

        # 1. Relative Strength
        rs = prices / benchmark_aligned

        # 2. RS-Ratio
        rs_ema = rs.ewm(span=ma_period, adjust=False).mean()
        rs_ratio = 100 * (rs_ema / rs_ema.mean())

        # 3. RS-Momentum
        rs_momentum = 100 + rs_ratio.pct_change(roc_period) * 100

        # 4. Combine
        df = pd.DataFrame({
            "rs_ratio": rs_ratio,
            "rs_momentum": rs_momentum
        }).dropna()

        if len(df) < tail_length:
            continue

        # 5. Tail history
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

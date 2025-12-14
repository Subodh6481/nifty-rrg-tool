import pandas as pd

def _extract_close(series_or_df):
    """
    Safely extract a 1D price series from various inputs
    """
    if isinstance(series_or_df, pd.Series):
        return series_or_df

    if not isinstance(series_or_df, pd.DataFrame):
        raise ValueError("Expected Series or DataFrame for price data")

    # Preferred order
    for col in ["Close", "Adj Close", "close"]:
        if col in series_or_df.columns:
            return series_or_df[col]

    # Fallback: single-column DataFrame
    if series_or_df.shape[1] == 1:
        return series_or_df.iloc[:, 0]

    raise KeyError(f"No price column found in DataFrame columns={series_or_df.columns}")

def calculate_rrg(data, benchmark, ma_period, roc_period, tail_length):
    results = []

    # -----------------------------
    # Benchmark prices (SAFE)
    # -----------------------------
    benchmark_prices = _extract_close(data[benchmark])

    for sector, sector_data in data.items():
        if sector == benchmark:
            continue

        prices = _extract_close(sector_data)

        # -----------------------------
        # Align dates
        # -----------------------------
        prices, benchmark_aligned = prices.align(benchmark_prices, join="inner")

        if len(prices) < max(ma_period, roc_period) + tail_length:
            continue

        # -----------------------------
        # Relative Strength
        # -----------------------------
        rs = prices / benchmark_aligned

        # -----------------------------
        # RS-Ratio (JdK)
        # -----------------------------
        rs_ema = rs.ewm(span=ma_period, adjust=False).mean()
        rs_ratio = 100 * (rs_ema / rs_ema.mean())

        # -----------------------------
        # RS-Momentum (JdK)
        # -----------------------------
        rs_momentum = 100 + rs_ratio.pct_change(roc_period) * 100

        df = pd.DataFrame({
            "rs_ratio": rs_ratio,
            "rs_momentum": rs_momentum
        }).dropna()

        if len(df) < tail_length:
            continue

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

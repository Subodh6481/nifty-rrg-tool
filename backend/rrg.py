import pandas as pd

def calculate_rrg(data, benchmark, ma_period, roc_period, tail_length):
    benchmark_price = data[benchmark]
    result = []

    for name, series in data.items():
        if name == benchmark:
            continue

        rs = series / benchmark_price
        rs_ratio = rs.ewm(span=ma_period).mean() * 100
        rs_momentum = rs_ratio.pct_change(roc_period) * 100 + 100

        df = pd.DataFrame({
            "rs_ratio": rs_ratio,
            "rs_momentum": rs_momentum
        }).dropna().tail(tail_length)

        result.append({
            "name": name,
            "history": df.values.tolist(),
            "latest": df.iloc[-1].to_dict()
        })

    return result

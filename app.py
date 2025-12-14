# app.py
import streamlit as st
import plotly.graph_objects as go
from backend.rrg import calculate_rrg
from backend.data import load_price_data

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(
    page_title="Nifty Sector RRG Dashboard",
    layout="wide"
)

# ----------------------------
# Sidebar Controls
# ----------------------------
st.sidebar.title("⚙️ Controls")

ema_period = st.sidebar.slider(
    "RS-Ratio EMA Period",
    min_value=5,
    max_value=30,
    value=10,
    step=1
)

roc_period = st.sidebar.slider(
    "RS-Momentum ROC Period",
    min_value=5,
    max_value=30,
    value=12,
    step=1
)

tail_length = st.sidebar.slider(
    "Tail Length (Periods)",
    min_value=2,
    max_value=20,
    value=5,
    step=1
)

SECTOR_TICKERS = {
    "Bank": "^NSEBANK",
    "PSU Bank": "^NSEPSUBANK",
    "IT": "^CNXIT",
    "FMCG": "^CNXFMCG",
    "Pharma": "^CNXPHARMA",
    "Auto": "^CNXAUTO",
    "Metal": "^CNXMETAL",
    "Realty": "^CNXREALTY",
    "Energy": "^CNXENERGY",
    "Media": "^CNXMEDIA",
}

selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=list(SECTOR_TICKERS.keys()),
    default=["Bank", "IT", "FMCG"]
)

# ----------------------------
# Validation
# ----------------------------
if len(selected_sectors) < 2:
    st.warning("Select at least 2 sectors to view RRG.")
    st.stop()

# ----------------------------
# Data Load
# ----------------------------
price_data = load_price_data(
    {k: SECTOR_TICKERS[k] for k in selected_sectors},
    benchmark="^NSEI"
)

# ----------------------------
# RRG Calculation
# ----------------------------
rrg_metrics = calculate_rrg(
    data=price_data,
    rs_period=ema_period,
    roc_period=roc_period,
    tail_length=tail_length
)

# ----------------------------
# Plot Function
# ----------------------------
def plot_rrg(rrg_metrics):
    fig = go.Figure()

    # Axis lock (reference style)
    fig.update_xaxes(range=[90, 110], title="JdK RS-Ratio", zeroline=False)
    fig.update_yaxes(range=[88, 112], title="JdK RS-Momentum", zeroline=False)

    # Quadrant backgrounds
    quadrants = [
        dict(x0=90, x1=100, y0=100, y1=112, fillcolor="#e8ecff"),  # Improving
        dict(x0=100, x1=110, y0=100, y1=112, fillcolor="#e9f7e6"), # Leading
        dict(x0=90, x1=100, y0=88, y1=100, fillcolor="#fde8e8"),  # Lagging
        dict(x0=100, x1=110, y0=88, y1=100, fillcolor="#fff4db"), # Weakening
    ]

    for q in quadrants:
        fig.add_shape(type="rect", line=dict(width=0), layer="below", **q)

    # Center lines
    fig.add_shape(type="line", x0=100, x1=100, y0=88, y1=112, line=dict(color="black", width=1))
    fig.add_shape(type="line", x0=90, x1=110, y0=100, y1=100, line=dict(color="black", width=1))

    # Plot each sector
    for sector in rrg_metrics["sector"].unique():
        df = rrg_metrics[rrg_metrics["sector"] == sector]

        x_vals = df["rs_ratio"].values
        y_vals = df["rs_momentum"].values

        if len(x_vals) < 2:
            continue  # not enough points for tail

        # Tail (history)
        fig.add_trace(go.Scatter(
            x=x_vals[:-1],
            y=y_vals[:-1],
            mode="lines+markers",
            line=dict(width=1),
            marker=dict(size=5),
            opacity=0.4,
            name=sector,
            showlegend=False,
            hoverinfo="skip"
        ))

        # Arrow (latest point)
        dx = x_vals[-1] - x_vals[-2]
        dy = y_vals[-1] - y_vals[-2]
        angle = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers",
            marker=dict(
                symbol="triangle-up",
                size=12,
                angle=angle,
                line=dict(width=1)
            ),
            name=sector,
            hovertemplate=(
                f"<b>{sector}</b><br>"
                "RS-Ratio: %{x:.2f}<br>"
                "RS-Momentum: %{y:.2f}<extra></extra>"
            )
        ))


    fig.update_layout(
        height=700,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="white"
    )

    return fig

# ----------------------------
# Main Layout
# ----------------------------
st.title("Nifty Sector RRG Dashboard")
st.caption("Hover over markers to see sector details. Triangle shows latest position; faded points show recent history.")

fig = plot_rrg(rrg_metrics)
st.plotly_chart(fig, use_container_width=True)

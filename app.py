# ======================================================
# app.py  (COMPLETE, UPDATED WITH STEP 3)
# ======================================================

import math
import streamlit as st
import plotly.graph_objects as go

from backend.config import SECTOR_TICKERS, BENCHMARK_TICKER
from backend.data import fetch_price_series
from backend.rrg import calculate_rrg

# ======================================================
# Streamlit configuration
# ======================================================
st.set_page_config(
    page_title="Nifty Sector RRG",
    layout="wide"
)

st.title("Nifty Sector RRG Dashboard")

# ======================================================
# Sidebar controls
# ======================================================
st.sidebar.header("⚙️ Controls")

ma_period = st.sidebar.slider("RS-Ratio EMA Period", 5, 30, 10, 1)
roc_period = st.sidebar.slider("RS-Momentum ROC Periods", 5, 30, 12, 1)
tail_length = st.sidebar.slider("Tail Length (Periods)", 3, 15, 5, 1)

selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=list(SECTOR_TICKERS.keys()),
    default=list(SECTOR_TICKERS.keys())
)

# ======================================================
# Validation
# ======================================================
if not selected_sectors:
    st.warning("👈 Please select at least one sector.")
    st.stop()

if len(selected_sectors) < 3:
    st.warning("ℹ️ RRG works best with 3 or more sectors selected.")

# ======================================================
# Fetch data
# ======================================================
price_data = {}
price_data[BENCHMARK_TICKER] = fetch_price_series(BENCHMARK_TICKER)

for sector in selected_sectors:
    price_data[sector] = fetch_price_series(SECTOR_TICKERS[sector])

# ======================================================
# Calculate RRG metrics
# ======================================================
rrg_metrics = calculate_rrg(
    data=price_data,
    benchmark=BENCHMARK_TICKER,
    ma_period=ma_period,
    roc_period=roc_period,
    tail_length=tail_length
)

# ======================================================
# PLOT FUNCTION (STEP 1 + STEP 2 + STEP 3)
# ======================================================
def plot_rrg(metrics, chart_title):
    fig = go.Figure()

    # -------------------------
    # STEP 1: LOCKED AXES
    # -------------------------
    fig.update_xaxes(range=[90, 110], title="JdK RS-Ratio", fixedrange=True)
    fig.update_yaxes(range=[87, 113], title="JdK RS-Momentum", fixedrange=True)

    # -------------------------
    # STEP 2: QUADRANTS
    # -------------------------
    fig.update_layout(
        shapes=[
            dict(type="rect", x0=90, x1=100, y0=100, y1=113,
                 fillcolor="rgba(120,140,255,0.15)", line_width=0, layer="below"),
            dict(type="rect", x0=100, x1=110, y0=100, y1=113,
                 fillcolor="rgba(140,220,140,0.18)", line_width=0, layer="below"),
            dict(type="rect", x0=90, x1=100, y0=87, y1=100,
                 fillcolor="rgba(255,140,140,0.20)", line_width=0, layer="below"),
            dict(type="rect", x0=100, x1=110, y0=87, y1=100,
                 fillcolor="rgba(255,215,140,0.22)", line_width=0, layer="below")
        ]
    )

    fig.add_hline(y=100, line_width=1, line_color="black")
    fig.add_vline(x=100, line_width=1, line_color="black")

    fig.add_annotation(x=93, y=111, text="Improving", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=107, y=111, text="Leading", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=93, y=89, text="Lagging", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=107, y=89, text="Weakening", showarrow=False, font=dict(size=14))

    # -------------------------
    # STEP 3: TAILS + ROTATED ARROWS
    # -------------------------
    for item in metrics:
        name = item["name"]
        history = item["history"]

        x_vals = [p[0] for p in history]
        y_vals = [p[1] for p in history]

        # Tail line
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line=dict(width=1.5),
            opacity=0.6,
            hoverinfo="skip",
            showlegend=False
        ))

        # Tail points
        fig.add_trace(go.Scatter(
            x=x_vals[:-1],
            y=y_vals[:-1],
            mode="markers",
            marker=dict(size=6, opacity=0.5),
            hoverinfo="skip",
            showlegend=False
        ))

        # Arrow rotation
        if len(x_vals) >= 2:
            dx = x_vals[-1] - x_vals[-2]
            dy = y_vals[-1] - y_vals[-2]
            angle = math.degrees(math.atan2(dy, dx))
        else:
            angle = 0

        # Latest point (rotated triangle)
        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers",
            marker=dict(
                size=12,
                symbol="triangle-right",
                angle=angle,
                line=dict(width=1.2)
            ),
            hovertemplate=(
                f"<b>{name}</b><br>"
                f"RS-Ratio: {x_vals[-1]:.2f}<br>"
                f"RS-Momentum: {y_vals[-1]:.2f}"
                "<extra></extra>"
            ),
            showlegend=False
        ))

    fig.update_layout(
        title=chart_title,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

# ======================================================
# RENDER
# ======================================================
fig = plot_rrg(rrg_metrics, f"Sector RRG vs {BENCHMARK_TICKER}")
st.plotly_chart(fig, use_container_width=True)

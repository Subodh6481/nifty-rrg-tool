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

ma_period = st.sidebar.slider(
    "RS-Ratio EMA Period",
    min_value=5,
    max_value=30,
    value=10,
    step=1
)

roc_period = st.sidebar.slider(
    "RS-Momentum ROC Periods",
    min_value=5,
    max_value=30,
    value=12,
    step=1
)

tail_length = st.sidebar.slider(
    "Tail Length (Periods)",
    min_value=3,
    max_value=15,
    value=5,
    step=1
)

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

# Benchmark
price_data[BENCHMARK_TICKER] = fetch_price_series(BENCHMARK_TICKER)

# Selected sectors
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
# Plot function (STEP 1 + STEP 2 applied)
# ======================================================
def plot_rrg(metrics, chart_title):
    fig = go.Figure()

    # -------------------------
    # STEP 1: LOCKED AXES
    # -------------------------
    fig.update_xaxes(
        range=[90, 110],
        title="JdK RS-Ratio",
        fixedrange=True,
        zeroline=False
    )

    fig.update_yaxes(
        range=[87, 113],
        title="JdK RS-Momentum",
        fixedrange=True,
        zeroline=False
    )

    # -------------------------
    # STEP 2: QUADRANT BACKGROUNDS
    # -------------------------
    fig.update_layout(
        shapes=[
            # Improving (Top-Left)
            dict(type="rect", x0=90, x1=100, y0=100, y1=113,
                 fillcolor="rgba(120,140,255,0.15)", line_width=0, layer="below"),
            # Leading (Top-Right)
            dict(type="rect", x0=100, x1=110, y0=100, y1=113,
                 fillcolor="rgba(140,220,140,0.18)", line_width=0, layer="below"),
            # Lagging (Bottom-Left)
            dict(type="rect", x0=90, x1=100, y0=87, y1=100,
                 fillcolor="rgba(255,140,140,0.20)", line_width=0, layer="below"),
            # Weakening (Bottom-Right)
            dict(type="rect", x0=100, x1=110, y0=87, y1=100,
                 fillcolor="rgba(255,215,140,0.22)", line_width=0, layer="below")
        ]
    )

    # Center cross
    fig.add_hline(y=100, line_width=1, line_color="black")
    fig.add_vline(x=100, line_width=1, line_color="black")

    # Quadrant labels
    fig.add_annotation(x=93, y=111, text="Improving", showarrow=False,
                       font=dict(size=14, color="blue"))
    fig.add_annotation(x=107, y=111, text="Leading", showarrow=False,
                       font=dict(size=14, color="green"))
    fig.add_annotation(x=93, y=89, text="Lagging", showarrow=False,
                       font=dict(size=14, color="darkred"))
    fig.add_annotation(x=107, y=89, text="Weakening", showarrow=False,
                       font=dict(size=14, color="orange"))

    fig.update_layout(
        title=chart_title,
        template="plotly_white",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

# ======================================================
# Render chart
# ======================================================
st.caption(
    "💡 Axis and quadrants are now locked. "
    "Next steps will add tails and directional markers."
)

fig = plot_rrg(rrg_metrics, f"Sector RRG vs {BENCHMARK_TICKER}")
st.plotly_chart(fig, use_container_width=True)

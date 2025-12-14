# app.py

import json
import pathlib
import streamlit as st

from backend.config import SECTOR_TICKERS, BENCHMARK_TICKER
from backend.data import fetch_price_series
from backend.rrg import calculate_rrg

# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(
    page_title="Nifty Sector RRG",
    layout="wide"
)

st.title("Nifty Sector RRG Dashboard")

# -----------------------------
# Sidebar controls
# -----------------------------
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
    "Tail Length (periods)",
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

# -----------------------------
# Main logic
# -----------------------------
if not selected_sectors:
    st.warning("👈 Please select at least one sector.")
    st.stop()

if len(selected_sectors) < 3:
    st.warning("ℹ️ RRG works best with 3 or more sectors selected.")

# -----------------------------
# Fetch data
# -----------------------------
price_data = {}

# Benchmark
price_data[BENCHMARK_TICKER] = fetch_price_series(BENCHMARK_TICKER)

# Selected sectors
for sector in selected_sectors:
    ticker = SECTOR_TICKERS[sector]
    price_data[sector] = fetch_price_series(ticker)

# -----------------------------
# Calculate RRG
# -----------------------------
rrg_data = calculate_rrg(
    data=price_data,
    benchmark=BENCHMARK_TICKER,
    ma_period=ma_period,
    roc_period=roc_period,
    tail_length=tail_length
)

# -----------------------------
# Render UI (JS)
# -----------------------------
BASE_DIR = pathlib.Path(__file__).parent
html_template = (BASE_DIR / "frontend" / "rrg_chart.html").read_text()

html = html_template.replace("{{DATA}}", json.dumps(rrg_data))

st.caption(
    "💡 Hover over markers to see sector details. "
    "Triangle marker shows the latest position; faded points show recent history."
)

st.components.v1.html(
    html,
    height=720,
    scrolling=False
)

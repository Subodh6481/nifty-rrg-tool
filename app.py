import streamlit as st
import json
from backend.rrg import calculate_rrg
from backend.data import fetch_data  # your existing yfinance logic

st.set_page_config(layout="wide")

st.title("Sector RRG vs. ^NSEI")

# --- Controls ---
ma_period = st.sidebar.slider("MA", 5, 20, 10)
roc_period = st.sidebar.slider("ROC", 5, 30, 12)
tail_length = st.sidebar.slider("Tail Length", 3, 15, 5)

# --- Fetch data ---
data = fetch_data()
rrg_data = calculate_rrg(data, "^NSEI", ma_period, roc_period, tail_length)

# --- Pass data to JS ---
rrg_json = json.dumps(rrg_data)

with open("frontend/rrg_chart.html") as f:
    html = f.read()

html = html.replace("{{DATA}}", rrg_json)

st.components.v1.html(html, height=700, scrolling=False)

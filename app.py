# app.py
import streamlit as st
import plotly.graph_objects as go
import numpy as np
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

    # Color palette for sectors (distinct colors)
    color_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
    ]

    sectors = rrg_metrics["sector"].unique()
    sector_colors = {sector: color_palette[i % len(color_palette)] for i, sector in enumerate(sectors)}

    # Axis lock (reference style) with gridlines
    fig.update_xaxes(
        range=[90, 110],
        title="JdK RS-Ratio",
        zeroline=False,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        griddash='dot'
    )
    fig.update_yaxes(
        range=[88, 112],
        title="JdK RS-Momentum",
        zeroline=False,
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        griddash='dot'
    )

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

    # Quadrant labels
    quadrant_labels = [
        dict(x=92, y=110, text="Improving", showarrow=False, font=dict(size=14, color="gray")),
        dict(x=108, y=110, text="Leading", showarrow=False, font=dict(size=14, color="gray")),
        dict(x=92, y=90, text="Lagging", showarrow=False, font=dict(size=14, color="gray")),
        dict(x=108, y=90, text="Weakening", showarrow=False, font=dict(size=14, color="gray")),
    ]

    for label in quadrant_labels:
        fig.add_annotation(**label)

    # Plot each sector
    for sector in rrg_metrics["sector"].unique():
        df = rrg_metrics[rrg_metrics["sector"] == sector]

        x_vals = df["rs_ratio"].values
        y_vals = df["rs_momentum"].values

        sector_color = sector_colors[sector]

        if len(x_vals) < 2:
            continue  # not enough points for tail

        # Create gradient effect for tail - older points are more transparent
        # Tail (history) - with gradient opacity
        for i in range(len(x_vals) - 1):
            # Calculate opacity based on position in tail (older = more transparent)
            opacity = 0.2 + (i / (len(x_vals) - 1)) * 0.5  # Range from 0.2 to 0.7

            # Draw line segment
            fig.add_trace(go.Scatter(
                x=[x_vals[i], x_vals[i+1]],
                y=[y_vals[i], y_vals[i+1]],
                mode="lines+markers",
                line=dict(width=2, color=sector_color),
                marker=dict(size=5, color=sector_color),
                opacity=opacity,
                name=sector,
                legendgroup=sector,
                showlegend=False,
                hoverinfo="skip"
            ))

        # Calculate arrow direction from last few points for smoother direction
        if len(x_vals) >= 3:
            # Use last 3 points for better direction calculation
            dx = x_vals[-1] - x_vals[-3]
            dy = y_vals[-1] - y_vals[-3]
        else:
            dx = x_vals[-1] - x_vals[-2]
            dy = y_vals[-1] - y_vals[-2]

        angle = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

        # Arrow head (latest point) - larger and more visible
        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers",
            marker=dict(
                symbol="triangle-up",
                size=16,
                angle=angle,
                color=sector_color,
                line=dict(width=2, color="white")
            ),
            name=sector,
            legendgroup=sector,
            hovertemplate=(
                f"<b>{sector}</b><br>"
                "RS-Ratio: %{x:.2f}<br>"
                "RS-Momentum: %{y:.2f}<br>"
                "<extra></extra>"
            )
        ))

        # Add sector label next to latest position with better positioning
        label_offset_x = 2.0 if dx >= 0 else -2.0
        label_offset_y = 1.0 if dy >= 0 else -1.0

        fig.add_annotation(
            x=x_vals[-1] + label_offset_x,
            y=y_vals[-1] + label_offset_y,
            text=f"<b>{sector}</b>",
            showarrow=False,
            font=dict(size=11, color=sector_color, family="Arial Black"),
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor=sector_color,
            borderwidth=1,
            borderpad=3
        )


    fig.update_layout(
        height=700,
        margin=dict(l=40, r=200, t=40, b=40),
        plot_bgcolor="white",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=11)
        ),
        hovermode='closest',
        # Enable hover highlighting - when hovering over a trace, others become dimmed
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Update traces to support hover highlighting
    # When you hover over one sector, others will be dimmed
    for trace in fig.data:
        trace.update(
            hoverlabel=dict(namelength=-1)
        )

    return fig

# ----------------------------
# Main Layout
# ----------------------------
st.markdown("# Nifty Sector RRG Dashboard")
st.markdown("*Hover over markers to see sector details. Triangle shows latest position; faded points show recent history.*")
st.markdown("---")

# Add custom CSS for better hover effects
st.markdown("""
<style>
    .js-plotly-plot .plotly .modebar {
        background-color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Improve legend styling */
    .legend {
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

fig = plot_rrg(rrg_metrics)

# Custom configuration for better interactivity
config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'nifty_rrg_chart',
        'height': 700,
        'width': 1200,
        'scale': 2
    }
}

st.plotly_chart(fig, use_container_width=True, config=config)

# Add footer info
st.markdown("---")
st.markdown("""
**Quadrant Guide:**
- **Leading** (Top Right): Strong momentum, strong relative strength
- **Weakening** (Bottom Right): Weakening momentum, still strong relative strength
- **Lagging** (Bottom Left): Weak momentum, weak relative strength
- **Improving** (Top Left): Improving momentum, still weak relative strength
""")

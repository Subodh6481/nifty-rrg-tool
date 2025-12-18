#!/usr/bin/env python3
"""
Visual test for the RRG plotting function
This creates a standalone HTML file to verify the plot looks correct
"""

import plotly.graph_objects as go
import numpy as np
from backend.data import load_price_data, SECTOR_TICKERS
from backend.rrg import calculate_rrg

# Load data
print("Loading data...")
test_sectors = {
    "IT": SECTOR_TICKERS["IT"],
    "Bank": SECTOR_TICKERS["Bank"],
    "FMCG": SECTOR_TICKERS["FMCG"],
}

price_data = load_price_data(
    sectors=test_sectors,
    benchmark="^NSEI",
    period="3mo"
)

# Calculate RRG
print("Calculating RRG...")
rrg_metrics = calculate_rrg(
    data=price_data,
    rs_period=10,
    roc_period=12,
    tail_length=5
)

# Create the plot (copy of plot_rrg function)
fig = go.Figure()

# Color palette for sectors (distinct colors)
color_palette = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
]

sectors = rrg_metrics["sector"].unique()
sector_colors = {sector: color_palette[i % len(color_palette)] for i, sector in enumerate(sectors)}

# Axis lock with gridlines
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
    dict(x0=90, x1=100, y0=100, y1=112, fillcolor="#e8ecff"),
    dict(x0=100, x1=110, y0=100, y1=112, fillcolor="#e9f7e6"),
    dict(x0=90, x1=100, y0=88, y1=100, fillcolor="#fde8e8"),
    dict(x0=100, x1=110, y0=88, y1=100, fillcolor="#fff4db"),
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

# Plot each sector with improved visualization
for sector in rrg_metrics["sector"].unique():
    df = rrg_metrics[rrg_metrics["sector"] == sector]
    x_vals = df["rs_ratio"].values
    y_vals = df["rs_momentum"].values
    sector_color = sector_colors[sector]

    if len(x_vals) < 2:
        continue

    # Tail line - solid line
    fig.add_trace(go.Scatter(
        x=x_vals[:-1], y=y_vals[:-1],
        mode="lines",
        line=dict(width=3, color=sector_color),
        opacity=0.6, name=sector, legendgroup=sector,
        showlegend=False, hoverinfo="skip"
    ))

    # Markers with gradient size
    for i in range(len(x_vals) - 1):
        marker_size = 4 + (i / (len(x_vals) - 1)) * 4
        opacity = 0.4 + (i / (len(x_vals) - 1)) * 0.4
        fig.add_trace(go.Scatter(
            x=[x_vals[i]], y=[y_vals[i]],
            mode="markers",
            marker=dict(size=marker_size, color=sector_color, line=dict(width=1, color="white")),
            opacity=opacity, name=sector, legendgroup=sector,
            showlegend=False, hoverinfo="skip"
        ))

    # Calculate arrow direction
    dx = x_vals[-1] - x_vals[-2]
    dy = y_vals[-1] - y_vals[-2]

    movement_magnitude = np.sqrt(dx**2 + dy**2)
    if movement_magnitude < 0.5 and len(x_vals) >= 3:
        dx = x_vals[-1] - x_vals[-3]
        dy = y_vals[-1] - y_vals[-3]

    angle = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

    # Arrow head
    fig.add_trace(go.Scatter(
        x=[x_vals[-1]], y=[y_vals[-1]],
        mode="markers",
        marker=dict(symbol="triangle-up", size=18, angle=angle, color=sector_color, line=dict(width=2, color="white")),
        name=sector, legendgroup=sector,
        hovertemplate=f"<b>{sector}</b><br>RS-Ratio: %{{x:.2f}}<br>RS-Momentum: %{{y:.2f}}<extra></extra>"
    ))

    # Position label close to arrow tip
    offset_distance = 1.2
    angle_rad = np.radians(angle)
    perpendicular_angle = angle_rad + np.pi/4
    label_offset_x = offset_distance * np.cos(perpendicular_angle)
    label_offset_y = offset_distance * np.sin(perpendicular_angle)

    fig.add_annotation(
        x=x_vals[-1] + label_offset_x, y=y_vals[-1] + label_offset_y,
        text=f"<b>{sector}</b>", showarrow=False,
        font=dict(size=9, color=sector_color, family="Arial", weight="bold"),
        bgcolor="rgba(255, 255, 255, 0.95)", bordercolor=sector_color,
        borderwidth=1, borderpad=2,
        xanchor="center", yanchor="middle"
    )

fig.update_layout(
    height=700, margin=dict(l=40, r=200, t=40, b=40),
    plot_bgcolor="white",
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
                bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="lightgray", borderwidth=1, font=dict(size=11)),
    hovermode='closest', title="Nifty Sector RRG - Visual Test (Enhanced)",
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
)

# Update traces for hover highlighting
for trace in fig.data:
    trace.update(hoverlabel=dict(namelength=-1))

# Save to HTML
fig.write_html("rrg_test_output.html")
print("✓ Visual test complete! Open 'rrg_test_output.html' in your browser to view the chart.")


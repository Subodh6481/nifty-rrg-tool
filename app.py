import plotly.graph_objects as go
import math


def plot_rrg(rrg_metrics, benchmark_name, tail_length):
    fig = go.Figure()

    # -------------------------
    # Axis ranges (locked)
    # -------------------------
    fig.update_xaxes(range=[90, 110], fixedrange=True, title="JdK RS-Ratio")
    fig.update_yaxes(range=[88, 112], fixedrange=True, title="JdK RS-Momentum")

    # -------------------------
    # Quadrant backgrounds
    # -------------------------
    fig.add_shape(type="rect", x0=90, x1=100, y0=100, y1=112,
                  fillcolor="#e8edff", opacity=0.8, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=100, x1=110, y0=100, y1=112,
                  fillcolor="#e9f6e6", opacity=0.8, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=90, x1=100, y0=88, y1=100,
                  fillcolor="#fdeaea", opacity=0.8, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=100, x1=110, y0=88, y1=100,
                  fillcolor="#fff4dd", opacity=0.8, layer="below", line_width=0)

    # Center lines
    fig.add_shape(type="line", x0=100, x1=100, y0=88, y1=112,
                  line=dict(color="black", width=1))
    fig.add_shape(type="line", x0=90, x1=110, y0=100, y1=100,
                  line=dict(color="black", width=1))

    # -------------------------
    # Quadrant titles
    # -------------------------
    fig.add_annotation(x=95, y=110, text="Improving", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=105, y=110, text="Leading", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=95, y=90, text="Lagging", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=105, y=90, text="Weakening", showarrow=False, font=dict(size=14))

    # -------------------------
    # Helper: arrow rotation
    # -------------------------
    def arrow_angle(x, y):
        if len(x) < 2:
            return 0
        dx = x[-1] - x[-2]
        dy = y[-1] - y[-2]
        return math.degrees(math.atan2(dy, dx))

    # -------------------------
    # Plot sectors
    # -------------------------
    for sector, df in rrg_metrics.items():
        x_vals = df["rs_ratio"].values[-tail_length:]
        y_vals = df["rs_momentum"].values[-tail_length:]

        # Tail (history)
        fig.add_trace(go.Scatter(
            x=x_vals[:-1],
            y=y_vals[:-1],
            mode="lines+markers",
            line=dict(width=1),
            marker=dict(size=5, opacity=0.35),
            hoverinfo="skip",
            showlegend=False
        ))

        # Arrow head (latest point)
        fig.add_trace(go.Scatter(
            x=[x_vals[-1]],
            y=[y_vals[-1]],
            mode="markers",
            marker=dict(
                symbol="triangle-right",
                size=13,                       # FIX 2: controlled size
                angle=arrow_angle(x_vals, y_vals),  # FIX 1: correct rotation
                line=dict(width=1, color="black")
            ),
            hovertemplate=(
                f"<b>{sector}</b><br>"
                "RS-Ratio: %{x:.2f}<br>"
                "RS-Momentum: %{y:.2f}<extra></extra>"
            ),
            showlegend=False
        ))

    # -------------------------
    # Layout
    # -------------------------
    fig.update_layout(
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    return fig

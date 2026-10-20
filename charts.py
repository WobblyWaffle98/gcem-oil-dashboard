"""Shared Plotly styling and small layout helpers for the dashboard pages."""
import plotly.graph_objects as go
import streamlit as st

from theme import COLORS, COLORWAY

FONT = "Geist, Inter, system-ui, sans-serif"


def layout(fig, height=400, legend=True, hover="x unified"):
    fig.update_layout(
        height=height, margin=dict(l=22, r=22, t=46 if legend else 14, b=14),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=COLORS["surface"],
        font=dict(family=FONT, color=COLORS["muted"], size=12), colorway=COLORWAY,
        hovermode=hover, showlegend=legend,
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=COLORS["rule"], font=dict(color=COLORS["ink"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, showline=True, linecolor=COLORS["rule"], automargin=True),
        yaxis=dict(gridcolor=COLORS["rule"], zeroline=False, automargin=True),
    )
    return fig


def show(fig, key):
    st.plotly_chart(fig, use_container_width=True, theme=None, key=key, config={"displayModeBar": False})


def unavailable(title, detail):
    st.markdown(f'<div class="gc-state"><b>{title}</b>{detail}</div>', unsafe_allow_html=True)


def panel(key):
    return st.container(key=f"panel_{key}")


def legend_swatch(fig, name, color):
    """Legend-only entry, used to explain shaded regions."""
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=name,
                             marker=dict(size=10, symbol="square", color=color)))

import html
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

from theme import COLORS, SECTIONS

MYT = ZoneInfo("Asia/Kuala_Lumpur")

# (label, Yahoo symbol, decimals)
QUOTES = [
    ("Brent", "BZ=F", 2),
    ("WTI", "CL=F", 2),
    ("Henry Hub", "NG=F", 3),
    ("Brent\u2013WTI spread", None, 2),
    ("Dollar index", "DX-Y.NYB", 2),
    ("USD/MYR", "MYR=X", 4),
]

# Yahoo Finance symbols for the main chart
CHARTS = {"Brent": "BZ=F", "WTI": "CL=F", "Henry Hub": "NG=F"}
RANGES = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y"}

CHART_HEIGHT = 640   # calendar iframe height
PLOT_HEIGHT = 540    # price chart height (leaves room for the controls)
# The Investing.com widget only ships a light theme; this inverts it to sit on the dark page.
DARKEN_CALENDAR = True


# ---------------------------------------------------------------- data
@st.cache_data(ttl=300, show_spinner=False)
def load_quotes():
    """One month of daily closes per symbol, plus the fetch time. Failures give None."""
    series = {}
    for _, sym, _ in QUOTES:
        if sym is None:
            continue
        try:
            s = yf.Ticker(sym).history(period="1mo", interval="1d")["Close"].dropna()
            series[sym] = s if len(s) >= 2 else None
        except Exception:
            series[sym] = None

    brent, wti = series.get("BZ=F"), series.get("CL=F")
    if brent is not None and wti is not None:
        spread = (brent - wti).dropna()
        series["SPREAD"] = spread if len(spread) >= 2 else None
    else:
        series["SPREAD"] = None
    return series, datetime.now(MYT)


@st.cache_data(ttl=300, show_spinner=False)
def load_history(symbol, period):
    """Daily OHLC from Yahoo Finance. Returns None on failure."""
    try:
        df = yf.Ticker(symbol).history(period=period, interval="1d")[["Open", "High", "Low", "Close"]].dropna()
        return df if len(df) >= 2 else None
    except Exception:
        return None


def _price_figure(df, name, dp, candles):
    up, down, accent = COLORS["up"], COLORS["down"], COLORS["accent"]
    font = dict(family="Geist, Inter, system-ui, sans-serif", color=COLORS["muted"], size=12)
    fig = go.Figure()
    if candles:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            increasing=dict(line=dict(color=up), fillcolor=up),
            decreasing=dict(line=dict(color=down), fillcolor=down),
            name=name, showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name=name, showlegend=False,
            line=dict(color=accent, width=2.2),
            hovertemplate=f"%{{y:,.{dp}f}}<extra></extra>",
        ))
    last = float(df["Close"].iloc[-1])
    fig.add_hline(y=last, line=dict(color=COLORS["muted"], width=1, dash="dot"),
                  annotation_text=f"{last:,.{dp}f}", annotation_position="right",
                  annotation_font=dict(color=COLORS["bg"], size=12),
                  annotation_bgcolor=accent if not candles else COLORS["text"])
    fig.update_layout(
        height=PLOT_HEIGHT, margin=dict(l=4, r=4, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=COLORS["panel"], font=font,
        hovermode="x unified", dragmode="pan",
        hoverlabel=dict(bgcolor=COLORS["raise"], bordercolor=COLORS["rule"], font=dict(color=COLORS["text"])),
        xaxis=dict(showgrid=False, showline=False, rangeslider=dict(visible=False),
                   rangebreaks=[dict(bounds=["sat", "mon"])],
                   showspikes=True, spikecolor=COLORS["muted"], spikethickness=1, spikedash="dot", spikemode="across"),
        yaxis=dict(side="right", gridcolor="rgba(255,255,255,0.05)", zeroline=False, tickformat=f",.{min(dp, 2)}f",
                   showspikes=True, spikecolor=COLORS["muted"], spikethickness=1, spikedash="dot"),
    )
    return fig


# ---------------------------------------------------------------- html builders
def _sparkline(values, color, w=92, h=30):
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1.0
    n = len(values) - 1
    pts = " ".join(
        f"{i * w / n:.1f},{h - 3 - (v - lo) / rng * (h - 6):.1f}" for i, v in enumerate(values)
    )
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.6" '
        f'stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def _quote_cell(label, s, dp):
    if s is None:
        return (
            f'<div class="gc-q"><div class="gc-q-top"><span class="gc-q-name">{html.escape(label)}</span></div>'
            f'<div class="gc-q-price">\u2014</div><div class="gc-q-chg flat">Unavailable</div></div>'
        )
    last, prev = float(s.iloc[-1]), float(s.iloc[-2])
    chg = last - prev
    pct = chg / abs(prev) * 100 if prev else 0.0
    cls = "up" if chg > 0 else "down" if chg < 0 else "flat"
    color = {"up": COLORS["up"], "down": COLORS["down"], "flat": COLORS["muted"]}[cls]
    sign = "+" if chg > 0 else "\u2212" if chg < 0 else ""
    return (
        f'<div class="gc-q">'
        f'<div class="gc-q-top"><span class="gc-q-name">{html.escape(label)}</span></div>'
        f'<div class="gc-q-price">{last:,.{dp}f}</div>'
        f'<div class="gc-q-row"><span class="gc-q-chg {cls}">{sign}{abs(chg):,.{dp}f} ({sign}{abs(pct):.2f}%)</span>'
        f"{_sparkline(s.tolist(), color)}</div></div>"
    )


def _calendar_html():
    flt = "filter:invert(0.92) hue-rotate(180deg);" if DARKEN_CALENDAR else ""
    return f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;height:100%;background:transparent;}}
  .wrap{{height:calc(100% - 2px);border:1px solid {COLORS['rule']};border-radius:12px;overflow:hidden;background:{COLORS['panel']};}}
  iframe{{width:100%;height:100%;border:none;{flt}}}
</style></head><body><div class="wrap">
<iframe src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&importance=2,3&features=datepicker,timeselector,filters&countries=37,42,5&calType=week&timeZone=113&lang=1"
        frameborder="0" allowtransparency="true"></iframe>
</div></body></html>"""


# ---------------------------------------------------------------- page
def _go(page):
    st.session_state["nav_page"] = page


def main_page():
    series, fetched = load_quotes()

    # Masthead
    st.markdown(
        f"""
        <div class="gc-mast">
          <div class="gc-title">GCEM <span>Oil Indicator Dashboard</span></div>
          <div class="gc-meta">
            <b>{fetched:%d %b %Y}</b><br>
            Quotes as of {fetched:%H:%M} MYT, delayed
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quote strip
    cells = []
    for label, sym, dp in QUOTES:
        cells.append(_quote_cell(label, series.get(sym or "SPREAD"), dp))
    st.markdown(f'<div class="gc-strip">{"".join(cells)}</div>', unsafe_allow_html=True)

    # Chart + calendar
    left, right = st.columns([1.75, 1.0], gap="large")

    with left:
        st.markdown(
            '<div class="gc-h">Prices</div>'
            '<p class="gc-note">Daily front-month futures from Yahoo Finance. Continuous contracts can show small jumps at roll dates.</p>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1.25, 1.5, 0.85])
        with c1:
            choice = st.segmented_control("Instrument", list(CHARTS), default="Brent",
                                          key="main_chart", label_visibility="collapsed") or "Brent"
        with c2:
            rng = st.segmented_control("Range", list(RANGES), default="6M",
                                       key="main_range", label_visibility="collapsed") or "6M"
        with c3:
            kind = st.segmented_control("Style", ["Line", "Candles"], default="Line",
                                        key="main_kind", label_visibility="collapsed") or "Line"

        sym = CHARTS[choice]
        dp = next(d for _, s, d in QUOTES if s == sym)
        hist = load_history(sym, RANGES[rng])
        if hist is None:
            st.warning("Price history is unavailable from Yahoo Finance right now. Try again in a few minutes.")
        else:
            st.plotly_chart(_price_figure(hist, choice, dp, kind == "Candles"),
                            use_container_width=True, theme=None,
                            config={"displayModeBar": False, "scrollZoom": True})
        st.caption(f"Source: Yahoo Finance ({sym}), delayed")
    with right:
        st.markdown(
            '<div class="gc-h">Economic calendar</div>'
            '<p class="gc-note">GDP, employment, inflation and central bank events. Filter by country and date inside the widget.</p>',
            unsafe_allow_html=True,
        )
        components.html(_calendar_html(), height=CHART_HEIGHT, scrolling=False)
        st.caption("Source: Investing.com")

    # Section index
    st.markdown('<div style="height:28px"></div><div class="gc-h">Analysis</div>', unsafe_allow_html=True)
    st.markdown('<p class="gc-note">Jump to a section, or use the sidebar.</p>', unsafe_allow_html=True)
    cols = st.columns(len(SECTIONS), gap="medium")
    for i, (col, (name, blurb)) in enumerate(zip(cols, SECTIONS.items())):
        with col:
            st.markdown(
                f'<div class="gc-card"><div class="gc-card-t">{html.escape(name)}</div>'
                f'<div class="gc-card-d">{html.escape(blurb)}</div></div>',
                unsafe_allow_html=True,
            )
            st.button("Open", key=f"open_{i}", on_click=_go, args=(name,))

    # Disclaimer
    st.markdown(
        '<div class="gc-foot"><b>Data disclaimer.</b> The data on this platform comes from publicly available market '
        "information. Any interpretation or analysis derived from it is the responsibility of the user. GCEM does not "
        "guarantee the accuracy or completeness of the data and is not liable for decisions or actions taken based on its use.</div>",
        unsafe_allow_html=True,
    )

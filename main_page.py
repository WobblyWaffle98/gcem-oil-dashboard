import html
from datetime import datetime
from zoneinfo import ZoneInfo

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

PLOT_HEIGHT = 500
CAL_HEIGHT = 560  # calendar iframe, sized so both panels end at the same line


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


# ---------------------------------------------------------------- figure
def _price_figure(df, name, dp, candles):
    c = COLORS
    fig = go.Figure()
    if candles:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            increasing=dict(line=dict(color=c["up"]), fillcolor=c["up"]),
            decreasing=dict(line=dict(color=c["down"]), fillcolor=c["down"]),
            name=name, showlegend=False,
        ))
    else:
        lo, hi = float(df["Close"].min()), float(df["Close"].max())
        floor = lo - (hi - lo) * 0.08
        # invisible floor so the area fill stops just under the lowest close
        fig.add_trace(go.Scatter(x=df.index, y=[floor] * len(df), mode="lines", line=dict(width=0),
                                 hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name=name, showlegend=False,
            line=dict(color=c["brand"], width=2.4), fill="tonexty", fillcolor="rgba(0,169,157,0.10)",
            hovertemplate=f"%{{y:,.{dp}f}}<extra></extra>",
        ))
    last = float(df["Close"].iloc[-1])
    fig.add_hline(
        y=last, line=dict(color=c["muted"], width=1, dash="dot"),
        annotation_text=f"{last:,.{dp}f}", annotation_position="right",
        annotation_font=dict(color="#FFFFFF", size=12), annotation_bgcolor=c["deep"],
    )
    fig.update_layout(
        height=PLOT_HEIGHT, margin=dict(l=4, r=4, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=c["surface"],
        font=dict(family="Geist, Inter, system-ui, sans-serif", color=c["muted"], size=12),
        hovermode="x unified", dragmode="pan",
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=c["rule"], font=dict(color=c["ink"])),
        xaxis=dict(showgrid=False, showline=True, linecolor=c["rule"], rangeslider=dict(visible=False),
                   rangebreaks=[dict(bounds=["sat", "mon"])],
                   showspikes=True, spikecolor=c["muted"], spikethickness=1, spikedash="dot", spikemode="across"),
        yaxis=dict(side="right", gridcolor=c["rule"], zeroline=False, tickformat=f",.{min(dp, 2)}f",
                   showspikes=True, spikecolor=c["muted"], spikethickness=1, spikedash="dot"),
    )
    return fig


# ---------------------------------------------------------------- html builders
def _sparkline(values, color, w=88, h=30):
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1.0
    n = len(values) - 1
    pts = " ".join(
        f"{i * w / n:.1f},{h - 3 - (v - lo) / rng * (h - 6):.1f}" for i, v in enumerate(values)
    )
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def _quote_card(label, s, dp):
    name = f'<div class="gc-q-name">{html.escape(label)}</div>'
    if s is None:
        return (f'<div class="gc-q">{name}<div class="gc-q-price">\u2014</div>'
                f'<div><span class="gc-pill flat">Unavailable</span></div></div>')
    last, prev = float(s.iloc[-1]), float(s.iloc[-2])
    chg = last - prev
    pct = chg / abs(prev) * 100 if prev else 0.0
    cls = "up" if chg > 0 else "down" if chg < 0 else "flat"
    color = {"up": COLORS["up"], "down": COLORS["down"], "flat": COLORS["muted"]}[cls]
    arrow = {"up": "\u25B2 ", "down": "\u25BC ", "flat": ""}[cls]
    return (
        f'<div class="gc-q">{name}'
        f'<div class="gc-q-price">{last:,.{dp}f}</div>'
        f'<div class="gc-q-row"><span class="gc-pill {cls}">{arrow}{abs(pct):.2f}%</span>'
        f"{_sparkline(s.tolist(), color)}</div></div>"
    )


def _calendar_html():
    return f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;height:100%;background:transparent;}}
  .wrap{{height:100%;border-radius:10px;overflow:hidden;}}
  iframe{{width:100%;height:100%;border:none;}}
</style></head><body><div class="wrap">
<iframe src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&importance=2,3&features=datepicker,timeselector,filters&countries=37,42,5&calType=week&timeZone=113&lang=1"
        frameborder="0" allowtransparency="true"></iframe>
</div></body></html>"""


# ---------------------------------------------------------------- page
def _go(page):
    st.session_state["nav_page"] = page


def main_page():
    series, fetched = load_quotes()

    # Hero
    st.markdown(
        f"""
        <div class="gc-hero">
          <div>
            <div class="gc-hero-t">Oil Indicator Dashboard</div>
            <div class="gc-hero-s">Market prices, upcoming economic events and analysis for oil and gas.</div>
          </div>
          <div class="gc-hero-m">
            <b>{fetched:%d %b %Y}</b><br>
            Quotes as of {fetched:%H:%M} MYT, delayed
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quote cards
    cards = [_quote_card(label, series.get(sym or "SPREAD"), dp) for label, sym, dp in QUOTES]
    st.markdown(f'<div class="gc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    # Chart + calendar
    left, right = st.columns([1.75, 1.0], gap="medium")

    with left:
        with st.container(key="chart_card"):
            st.markdown(
                '<div class="gc-h">Prices</div>'
                '<p class="gc-note">Daily front-month futures from Yahoo Finance. Continuous contracts can show small jumps at roll dates.</p>',
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns([1.25, 1.5, 0.9])
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
        with st.container(key="cal_card"):
            st.markdown(
                '<div class="gc-h">Economic calendar</div>'
                '<p class="gc-note">GDP, employment, inflation and central bank events. Filter by country and date in the widget.</p>',
                unsafe_allow_html=True,
            )
            components.html(_calendar_html(), height=CAL_HEIGHT, scrolling=False)
            st.caption("Source: Investing.com")

    # Section cards
    st.markdown('<div style="height:22px"></div><div class="gc-h">Analysis</div>', unsafe_allow_html=True)
    st.markdown('<p class="gc-note">Jump to a section, or use the sidebar.</p>', unsafe_allow_html=True)
    cols = st.columns(len(SECTIONS), gap="medium")
    for i, (col, (name, (blurb, icon))) in enumerate(zip(cols, SECTIONS.items())):
        with col:
            with st.container(key=f"sec_{i}"):
                st.markdown(
                    f'<div class="gc-ic"><svg viewBox="0 0 24 24" aria-hidden="true">{icon}</svg></div>'
                    f'<div class="gc-card-t">{html.escape(name)}</div>'
                    f'<div class="gc-card-d">{html.escape(blurb)}</div>',
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

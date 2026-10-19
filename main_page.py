import html
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
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

# TradingView symbols for the main chart (same sources as before)
CHARTS = {
    "Brent": "VELOCITY:BRENT",
    "WTI": "NYMEX:CL1!",
    "Henry Hub": "NYMEX:NG1!",
}

CHART_HEIGHT = 640
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


def _tv_chart_html(symbol):
    return f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;height:100%;background:transparent;}}
  .wrap{{height:calc(100% - 2px);border:1px solid {COLORS['rule']};border-radius:12px;overflow:hidden;background:{COLORS['bg']};}}
  .tradingview-widget-container{{height:100%;width:100%;}}
</style></head><body><div class="wrap">
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {{
    "autosize": true,
    "symbol": "{symbol}",
    "interval": "D",
    "timezone": "Asia/Kuala_Lumpur",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "backgroundColor": "{COLORS['bg']}",
    "gridColor": "rgba(255, 255, 255, 0.04)",
    "hide_legend": true,
    "withdateranges": true,
    "allow_symbol_change": false,
    "calendar": false,
    "hide_volume": true,
    "support_host": "https://www.tradingview.com"
  }}
  </script>
</div></div></body></html>"""


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
        head, ctrl = st.columns([1, 1])
        with head:
            st.markdown(
                '<div class="gc-h">Prices</div>'
                '<p class="gc-note">Daily futures from TradingView. Small differences or delays against official settlements are possible.</p>',
                unsafe_allow_html=True,
            )
        with ctrl:
            choice = st.segmented_control(
                "Instrument", list(CHARTS), default="Brent",
                key="main_chart", label_visibility="collapsed",
            ) or "Brent"
        components.html(_tv_chart_html(CHARTS[choice]), height=CHART_HEIGHT, scrolling=False)
        st.caption(f"Source: TradingView ({CHARTS[choice].split(':')[0].title()})")

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

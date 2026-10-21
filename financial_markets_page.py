from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

from charts import FONT, layout, panel, show, unavailable
from markets_copy import TEXT
from sp500_universe import load_universe
from theme import COLORS, PALETTE_LONG, hero, kpi_grid, panel_head

YAHOO = "Source: Yahoo Finance, delayed"
TREASURY = "Source: U.S. Department of the Treasury"

EQUITY_TICKERS = {
    "^GSPC": "S&P 500", "^DJI": "Dow Jones Industrial Average", "^IXIC": "NASDAQ Composite", "BZ=F": "Brent Crude Oil",
    "000001.SS": "Shanghai Composite Index", "^N225": "Nikkei 225", "^GDAXI": "DAX", "^FTSE": "FTSE 100", "^NSEI": "NIFTY 50",
}
FX_TICKERS = {
    "BZ=F": "Brent Crude Oil", "EURUSD=X": "EUR/USD", "JPY=X": "USD/JPY", "GBPUSD=X": "GBP/USD", "AUDUSD=X": "AUD/USD",
    "USDCAD=X": "USD/CAD", "USDCHF=X": "USD/CHF", "NZDUSD=X": "NZD/USD", "DX-Y.NYB": "US Dollar Index",
}
PERIOD_DAYS = {"1 Year": 365, "5 Years": 5 * 365, "10 Years": 10 * 365}
PERF_WINDOWS = {"1D": 1, "1W": 5, "1M": 21, "3M": 63, "YTD": None}
PERF_LIMIT = {"1D": 3, "1W": 5, "1M": 10, "3M": 15, "YTD": 25}
RECESSIONS = [("2007-12-01", "2009-06-30"), ("2020-02-01", "2020-11-30")]
TENORS = ["1 Mo", "2 Mo", "3 Mo", "6 Mo", "1 Yr", "2 Yr", "3 Yr", "5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr"]
FX_CCY = ["EUR", "USD", "JPY", "GBP", "CAD", "MYR"]
FX_PAIRS = {"EUR": ("EURUSD=X", False), "GBP": ("GBPUSD=X", False), "JPY": ("JPY=X", True), "CAD": ("CAD=X", True), "MYR": ("MYR=X", True)}


# ---------------------------------------------------------------- data (each raises on failure; wrappers below catch)
def _clean(df):
    df = df.copy()
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df.index = df.index.normalize()
    return df[~df.index.duplicated(keep="last")].sort_index()


@st.cache_data(ttl=3600, show_spinner=False)
def _closes(tickers, start):
    """Daily closes, one column per ticker. Dates are normalised so markets in different time zones line up."""
    if len(tickers) == 1:
        s = yf.Ticker(tickers[0]).history(start=start)["Close"].dropna()
        out = s.to_frame(tickers[0])
    else:
        raw = yf.download(list(tickers), start=start, auto_adjust=True, progress=False, threads=True)["Close"]
        out = raw.dropna(axis=1, how="all")
    if out.empty:
        raise ValueError("No price data")
    return _clean(out)


def closes(tickers, start):
    try:
        return _closes(tuple(tickers), str(start))
    except Exception:
        return None


def _since(days):
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


@st.cache_data(ttl=12 * 3600, show_spinner=False)
def _market_caps(symbols):
    def one(sym):
        try:
            v = yf.Ticker(sym).fast_info["market_cap"]
            return sym, float(v) if v else None
        except Exception:
            return sym, None

    with ThreadPoolExecutor(max_workers=12) as ex:
        res = dict(ex.map(one, symbols))
    return {k: v for k, v in res.items() if v}


@st.cache_data(ttl=3600, show_spinner=False)
def _treasury(year_now):
    def fetch(year):
        url = (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all"
               f"?type=daily_treasury_yield_curve&field_tdr_date_value={year}page&_format=csv")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))

    frames = []
    with ThreadPoolExecutor() as ex:
        futures = [ex.submit(fetch, y) for y in (year_now, year_now - 1, year_now - 2)]
        for f in futures:
            try:
                frames.append(f.result())
            except Exception:
                pass
    if not frames:
        raise ValueError("No Treasury data")
    df = pd.concat(frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").sort_index()[TENORS].dropna()


def treasury():
    try:
        return _treasury(datetime.now().year)
    except Exception:
        return None


# ---------------------------------------------------------------- small helpers
def _arrow(d):
    return "\u25B2" if d > 0 else "\u25BC" if d < 0 else ""


def _seg(label, options, key, default=None):
    d = default or options[0]
    return st.segmented_control(label, options, default=d, key=key, label_visibility="collapsed") or d


def _unavail(key, title="Data unavailable", detail="The source could not be reached. Try again shortly."):
    with panel(key):
        unavailable(title, detail)


def _quote_card(label, s, dp=2, suffix=""):
    s = s.dropna()
    if len(s) < 2:
        return dict(label=label, value="\u2014", pill="Unavailable")
    last, prev = float(s.iloc[-1]), float(s.iloc[-2])
    pct = (last / prev - 1) * 100 if prev else 0.0
    cls = "flat" if round(pct, 2) == 0 else "up" if pct > 0 else "down"
    return dict(label=label, value=f"{last:,.{dp}f}{suffix}", pill=f"{_arrow(pct)} {abs(pct):.2f}%", pill_cls=cls,
                sub=f"Prior close {prev:,.{dp}f}{suffix}")


# ---------------------------------------------------------------- equities
def perf_from(closes_df, window):
    c = closes_df.ffill()
    if window == "YTD":
        prior = c[c.index.year < c.index[-1].year]
        base = prior.iloc[-1] if len(prior) else c.iloc[0]
    else:
        base = c.iloc[-1 - PERF_WINDOWS[window]]
    return (c.iloc[-1] / base - 1) * 100, c.iloc[-1]


def treemap_fig(df, window):
    c = COLORS
    lim = PERF_LIMIT[window]
    ids, labels, parents, values, colors, texts, custom = [], [], [], [], [], [], []
    total = df["Cap"].sum()
    root_perf = float(np.average(df["Perf"], weights=df["Cap"]))
    ids.append("root"), labels.append("S&P 500 large caps"), parents.append(""), values.append(total), colors.append(root_perf)
    texts.append(""), custom.append(["S&P 500 large caps", ""])
    for sector, g in df.groupby("Sector"):
        ids.append(sector), labels.append(sector), parents.append("root"), values.append(g["Cap"].sum())
        colors.append(float(np.average(g["Perf"], weights=g["Cap"]))), texts.append(""), custom.append([sector, ""])
        for r in g.itertuples():
            ids.append(f"{sector}/{r.Symbol}"), labels.append(r.Symbol), parents.append(sector), values.append(r.Cap)
            colors.append(float(r.Perf)), texts.append(f"{r.Perf:+.1f}%"), custom.append([r.Name, f"${r.Price:,.2f}"])
    fig = go.Figure(go.Treemap(
        ids=ids, labels=labels, parents=parents, values=values, branchvalues="total", text=texts, textinfo="label+text",
        customdata=custom, root_color="#FFFFFF",
        marker=dict(colors=colors, cmin=-lim, cmax=lim, cmid=0, line=dict(width=1.5, color="#FFFFFF"),
                    colorscale=[[0, c["down"]], [0.5, "#EEF3F3"], [1, c["up"]]],
                    colorbar=dict(title=dict(text="%", side="right"), ticksuffix="%", thickness=12, len=0.8),
                    pad=dict(t=26, l=3, r=3, b=3)),
        textfont=dict(family=FONT, color=c["ink"], size=13),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Market cap $%{value:,.0f}bn<br>%{color:+.2f}%<extra></extra>",
        pathbar=dict(visible=False), tiling=dict(packing="squarify"),
    ))
    fig.update_layout(height=620, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT))
    return fig


def heatmap_data(window):
    uni = load_universe()
    symbols = tuple(s for s, _, _ in uni)
    px_ = closes(symbols, _since(420))
    caps = _safe_call(_market_caps, symbols)
    if px_ is None or not caps or len(px_) < 70:
        return None
    perf, last = perf_from(px_, window)
    rows = []
    for sym, name, sector in uni:
        if sym in perf.index and sym in caps and pd.notna(perf[sym]):
            rows.append((sym, name, sector, caps[sym] / 1e9, float(perf[sym]), float(last[sym])))
    if len(rows) < 20:
        return None
    return pd.DataFrame(rows, columns=["Symbol", "Name", "Sector", "Cap", "Perf", "Price"])


def _safe_call(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None


def corr_fig(c):
    cols = COLORS
    fig = go.Figure(go.Heatmap(
        z=c.values, x=list(c.columns), y=list(c.index), zmin=-1, zmax=1, xgap=2, ygap=2,
        text=c.round(2).values, texttemplate="%{text:.2f}", textfont=dict(size=12),
        colorscale=[[0, cols["down"]], [0.5, "#FFFFFF"], [1, cols["blue"]]],
        colorbar=dict(title=dict(text="Correlation", side="right"), thickness=12, len=0.9),
        hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
    ))
    layout(fig, 540, legend=False, hover="closest")
    fig.update_layout(margin=dict(l=22, r=22, t=14, b=14))
    fig.update_xaxes(side="top", showline=False, tickangle=-30)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


def corr_panel(key, title, tickers, text_key, period_key, basis_key):
    with panel(key):
        panel_head(title, "Correlation coefficients run from -1 (red) to 1 (blue).")
        c1, c2, _ = st.columns([1.4, 1.5, 2])
        with c1:
            period = _seg("Period", list(PERIOD_DAYS), period_key, "1 Year")
        with c2:
            basis = _seg("Basis", ["Prices", "Daily returns"], basis_key)
        d = closes(tuple(tickers), _since(PERIOD_DAYS[period]))
        if d is None:
            unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
        else:
            d = d.rename(columns=tickers)
            d = d[[n for n in tickers.values() if n in d.columns]]
            if basis == "Daily returns":
                d = d.pct_change()
            show(corr_fig(d.corr()), f"{key}_chart")
        st.caption(YAHOO + ". 'Prices' correlates price levels, as the original page did; 'Daily returns' correlates daily percentage changes.")
    with st.expander("About this matrix"):
        st.markdown(TEXT[text_key])


def vix_fig(d, start):
    v = d[d.index >= start]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=v.index, y=v["^VIX"], mode="lines", name="VIX", line=dict(color=COLORS["down"], width=1.8),
                             hovertemplate="%{y:.1f}"), secondary_y=False)
    fig.add_trace(go.Scatter(x=v.index, y=v["^GSPC"], mode="lines", name="S&P 500", line=dict(color=COLORS["brand"], width=2),
                             hovertemplate="%{y:,.0f}"), secondary_y=True)
    for a, b in RECESSIONS:
        if pd.Timestamp(b) > start:
            fig.add_vrect(x0=max(pd.Timestamp(a), start), x1=b, fillcolor="rgba(229,72,77,0.10)", line_width=0, layer="below")
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="US recession",
                             marker=dict(size=10, symbol="square", color="rgba(229,72,77,0.30)")))
    layout(fig, 450)
    fig.update_yaxes(title_text="VIX", secondary_y=False)
    fig.update_yaxes(title_text="S&P 500", secondary_y=True, showgrid=False)
    return fig


def equities_tab():
    idx = closes(("^GSPC", "^DJI", "^IXIC", "^VIX"), _since(20))
    if idx is not None:
        kpi_grid([
            _quote_card("S&P 500", idx["^GSPC"]) if "^GSPC" in idx else dict(label="S&P 500", value="\u2014"),
            _quote_card("Dow Jones", idx["^DJI"]) if "^DJI" in idx else dict(label="Dow Jones", value="\u2014"),
            _quote_card("NASDAQ Composite", idx["^IXIC"]) if "^IXIC" in idx else dict(label="NASDAQ", value="\u2014"),
            _quote_card("VIX", idx["^VIX"]) if "^VIX" in idx else dict(label="VIX", value="\u2014"),
        ], cols=4)

    with panel("eq_heat"):
        panel_head("S&P 500 heatmap", "Block size is market capitalisation, colour is performance over the selected window.")
        window = _seg("Window", list(PERF_WINDOWS), "eq_window", "1W")
        with st.spinner("Loading prices and market caps"):
            df = _safe_call(heatmap_data, window)
        if df is None:
            unavailable("Heatmap unavailable", "Prices or market caps could not be loaded from Yahoo Finance. Try again shortly.")
        else:
            show(treemap_fig(df, window), "eq_heat_chart")
        st.caption(YAHOO + f". Covers {0 if df is None else len(df)} large constituents. Add sp500_constituents.csv (Symbol, Name, Sector) to cover all 500.")
    with st.expander("About this heatmap"):
        st.markdown(TEXT["heatmap"])

    with panel("eq_vix"):
        panel_head("VIX index and S&P 500", "The CBOE Volatility Index against the S&P 500, with US recessions shaded.")
        rng = _seg("Range", ["Max", "10Y", "5Y", "3Y", "1Y"], "eq_vix_range")
        d = closes(("^VIX", "^GSPC"), "2004-01-01")
        if d is None or not {"^VIX", "^GSPC"} <= set(d.columns):
            unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
        else:
            years = {"Max": None, "10Y": 10, "5Y": 5, "3Y": 3, "1Y": 1}[rng]
            start = d.index.min() if years is None else d.index.max() - pd.DateOffset(years=years)
            show(vix_fig(d.ffill(), start), "eq_vix_chart")
        st.caption(YAHOO)
    with st.expander("About the VIX"):
        st.markdown(TEXT["vix"])

    corr_panel("eq_corr", "Stock markets and Brent crude: correlation matrix", EQUITY_TICKERS, "corr_eq", "eq_corr_period", "eq_corr_basis")


# ---------------------------------------------------------------- fixed income
def _at(data, days):
    target = data.index[-1] - pd.Timedelta(days=days)
    return data.loc[:target].iloc[-1]


def curve_fig(data):
    rows = {"Current": data.iloc[-1], "Last Week": _at(data, 7), "Last Month": _at(data, 30), "Last Year": _at(data, 365)}
    colors = [COLORS["brand"], COLORS["blue"], "#F2A93B", COLORS["muted"]]
    fig = go.Figure()
    for (name, row), color in zip(rows.items(), colors):
        fig.add_trace(go.Scatter(x=list(row.index), y=row.values, mode="lines+markers", name=name,
                                 line=dict(color=color, width=2.6 if name == "Current" else 1.8, dash="solid" if name == "Current" else "dot"),
                                 marker=dict(size=5), hovertemplate="%{y:.2f}%"))
    layout(fig, 420)
    fig.update_xaxes(title_text="Maturity", type="category")
    fig.update_yaxes(title_text="Yield (%)", ticksuffix="%")
    return fig


def spread_fig(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["10 Yr"] - data["2 Yr"], mode="lines", name="10Y minus 2Y",
                             line=dict(color=COLORS["brand"], width=2.2), hovertemplate="%{y:+.2f}"))
    fig.add_trace(go.Scatter(x=data.index, y=data["10 Yr"] - data["3 Mo"], mode="lines", name="10Y minus 3M",
                             line=dict(color=COLORS["blue"], width=1.8), hovertemplate="%{y:+.2f}"))
    fig.add_hline(y=0, line=dict(color=COLORS["down"], width=1.2, dash="dash"))
    layout(fig, 420)
    fig.update_yaxes(title_text="Spread (percentage points)")
    return fig


def yields_fig(data, start):
    v = data[data.index >= start]
    fig = go.Figure()
    for i, col in enumerate(TENORS):
        fig.add_trace(go.Scatter(x=v.index, y=v[col], mode="lines", name=col, line=dict(color=PALETTE_LONG[i % len(PALETTE_LONG)], width=1.8),
                                 hovertemplate="%{y:.2f}%"))
    layout(fig, 470)
    fig.update_yaxes(title_text="Yield (%)", ticksuffix="%")
    return fig


def fixed_income_tab():
    data = treasury()
    if data is None:
        _unavail("fi_err", "Treasury data unavailable", "The U.S. Treasury website could not be reached. Try again shortly.")
        return

    last, prev = data.iloc[-1], data.iloc[-2]

    def ycard(label, col):
        bp = (last[col] - prev[col]) * 100
        return dict(label=label, value=f"{last[col]:.2f}%", pill=f"{_arrow(bp)} {abs(bp):.0f} bp" if round(bp) else "No change",
                    pill_cls="flat", sub=f"vs prior day \u00B7 {data.index[-1]:%d %b %Y}")

    def scard(label, a, b):
        s = (last[a] - last[b]) * 100
        return dict(label=label, value=f"{s:+.0f} bp", pill="Inverted" if s < 0 else "Normal", pill_cls="down" if s < 0 else "up",
                    sub="Long yield minus short yield")

    kpi_grid([ycard("2-year yield", "2 Yr"), ycard("10-year yield", "10 Yr"), ycard("30-year yield", "30 Yr"),
              scard("10Y minus 2Y", "10 Yr", "2 Yr"), scard("10Y minus 3M", "10 Yr", "3 Mo")], cols=5)

    a, b = st.columns(2, gap="medium")
    with a:
        with panel("fi_curve"):
            panel_head("Treasury yield curve", "Today's curve against one week, one month and one year ago.")
            show(curve_fig(data), "fi_curve_chart")
            st.caption(TREASURY)
    with b:
        with panel("fi_spread"):
            panel_head("Curve spreads", "Below zero means the curve is inverted, which has often preceded recessions.")
            show(spread_fig(data), "fi_spread_chart")
            st.caption(TREASURY)

    with panel("fi_series"):
        panel_head("Treasury yields over time", "Daily yields for each maturity. Click a legend entry to hide or show it.")
        rng = _seg("Range", ["3Y", "1Y", "6M", "3M"], "fi_range")
        days = {"3Y": None, "1Y": 365, "6M": 182, "3M": 91}[rng]
        start = data.index.min() if days is None else data.index.max() - pd.Timedelta(days=days)
        show(yields_fig(data, start), "fi_series_chart")
        st.caption(TREASURY)
    with st.expander("About the yield curve"):
        st.markdown(TEXT["treasury"])


# ---------------------------------------------------------------- FX
def fx_matrices(d):
    """Cross-rate and daily-change matrices for FX_CCY from USD pairs: rate[row][col] = value of 1 row in col units."""
    def usd_per(i):
        v = {"USD": 1.0}
        for ccy, (sym, inverse) in FX_PAIRS.items():
            x = float(d[sym].iloc[i])
            v[ccy] = 1 / x if inverse else x
        return v

    now, before = usd_per(-1), usd_per(-2)
    rate = pd.DataFrame({c: {r: now[r] / now[c] for r in FX_CCY} for c in FX_CCY})
    prev = pd.DataFrame({c: {r: before[r] / before[c] for r in FX_CCY} for c in FX_CCY})
    return rate, (rate / prev - 1) * 100


def cross_table(rate, chg):
    head = "".join(f"<th>{c}</th>" for c in FX_CCY)
    body = ""
    for r in FX_CCY:
        cells = ""
        for c in FX_CCY:
            if r == c:
                cells += '<td style="color:#9AABAA">\u2014</td>'
                continue
            ch = chg.loc[r, c]
            tint = "rgba(31,157,85,0.10)" if ch > 0.005 else "rgba(229,72,77,0.10)" if ch < -0.005 else "transparent"
            cells += f'<td style="background:{tint}">{rate.loc[r, c]:,.5g}</td>'
        body += f"<tr><td><b>{r}</b></td>{cells}</tr>"
    return f'<table class="gc-table"><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table>'


def change_fig(chg):
    lim = max(0.5, float(np.nanmax(np.abs(chg.values))))
    z = chg.values.copy()
    for i in range(len(z)):
        z[i, i] = np.nan
    text = [["" if i == j else f"{chg.iloc[i, j]:+.2f}%" for j in range(len(FX_CCY))] for i in range(len(FX_CCY))]
    fig = go.Figure(go.Heatmap(
        z=z, x=FX_CCY, y=FX_CCY, text=text, texttemplate="%{text}", zmin=-lim, zmax=lim, zmid=0, xgap=2, ygap=2, hoverongaps=False,
        colorscale=[[0, COLORS["down"]], [0.5, "#FFFFFF"], [1, COLORS["up"]]],
        colorbar=dict(title=dict(text="%", side="right"), ticksuffix="%", thickness=12, len=0.85),
        hovertemplate="1 %{y} in %{x}: %{z:+.2f}%<extra></extra>",
    ))
    layout(fig, 400, legend=False, hover="closest")
    fig.update_layout(margin=dict(l=22, r=22, t=14, b=14))
    fig.update_xaxes(side="top", showline=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


def dxy_figs(d):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=d.index, y=d["DX-Y.NYB"], mode="lines", name="US Dollar Index", line=dict(color=COLORS["blue"], width=1.8),
                             hovertemplate="%{y:.2f}"), secondary_y=False)
    fig.add_trace(go.Scatter(x=d.index, y=d["BZ=F"], mode="lines", name="Brent crude oil", line=dict(color=COLORS["brand"], width=1.8),
                             hovertemplate="%{y:.2f}"), secondary_y=True)
    layout(fig, 430)
    fig.update_yaxes(title_text="US Dollar Index", secondary_y=False)
    fig.update_yaxes(title_text="Brent (USD per barrel)", secondary_y=True, showgrid=False)

    roll = d["DX-Y.NYB"].rolling(window=252, min_periods=63).corr(d["BZ=F"])
    fig2 = go.Figure(go.Scatter(x=roll.index, y=roll, mode="lines", name="Rolling 1-year correlation", fill="tozeroy",
                                line=dict(color=COLORS["brand"], width=1.6), fillcolor="rgba(0,169,157,0.12)", hovertemplate="%{y:.2f}"))
    layout(fig2, 430, legend=False)
    fig2.update_yaxes(title_text="Correlation", range=[-1, 1], zeroline=True, zerolinecolor=COLORS["muted"])
    return fig, fig2


def fx_tab():
    pair_syms = [s for s, _ in FX_PAIRS.values()]
    d = closes(tuple(pair_syms + ["DX-Y.NYB"]), _since(21))
    ok = d is not None and all(s in d.columns for s in pair_syms)
    if ok:
        d = d.ffill()
        kpi_grid([
            _quote_card("US Dollar Index", d["DX-Y.NYB"]) if "DX-Y.NYB" in d else dict(label="US Dollar Index", value="\u2014"),
            _quote_card("USD/MYR", d["MYR=X"], 4), _quote_card("EUR/USD", d["EURUSD=X"], 4), _quote_card("USD/JPY", d["JPY=X"], 2),
        ], cols=4)
        rate, chg = fx_matrices(d)

    a, b = st.columns(2, gap="medium")
    with a:
        with panel("fx_cross"):
            panel_head("Latest cross rates", "Read across: the value of one unit of the row currency in the column currency. Shading shows the day's move.")
            if not ok:
                unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
            else:
                st.markdown(cross_table(rate, chg), unsafe_allow_html=True)
            st.caption(YAHOO + ". Cross rates are derived from USD pairs.")
    with b:
        with panel("fx_change"):
            panel_head("Daily percentage change", "Move in the cross rate since the previous close. Green means the row currency strengthened.")
            if not ok:
                unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
            else:
                show(change_fig(chg), "fx_change_chart")
            st.caption(YAHOO)
    with st.expander("About these rates"):
        st.markdown(TEXT["fx_intro"])

    corr_panel("fx_corr", "FX pairs and Brent crude: correlation matrix", FX_TICKERS, "corr_fx", "fx_corr_period", "fx_corr_basis")

    dd = closes(("DX-Y.NYB", "BZ=F"), "2007-07-01")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with panel("fx_dxy"):
            panel_head("US Dollar Index and Brent", "Daily history since July 2007.")
            if dd is None or not {"DX-Y.NYB", "BZ=F"} <= set(dd.columns):
                unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
            else:
                f1, f2 = dxy_figs(dd.ffill())
                show(f1, "fx_dxy_chart")
            st.caption(YAHOO)
    with c2:
        with panel("fx_roll"):
            panel_head("Rolling one-year correlation", "Correlation of the dollar index with Brent over the past 252 trading days.")
            if dd is None or not {"DX-Y.NYB", "BZ=F"} <= set(dd.columns):
                unavailable("Data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
            else:
                show(f2, "fx_roll_chart")
            st.caption(YAHOO)
    with st.expander("About the dollar and Brent"):
        st.markdown(TEXT["dxy"])


# ---------------------------------------------------------------- page
def financial_markets_page():
    hero("Financial Market Indicators",
         "Equities, U.S. Treasury yields and foreign exchange.",
         "Sources<br>Yahoo Finance, U.S. Treasury", slim=True)
    t1, t2, t3 = st.tabs(["Equities", "Fixed Income", "FX"])
    with t1:
        equities_tab()
    with t2:
        fixed_income_tab()
    with t3:
        fx_tab()

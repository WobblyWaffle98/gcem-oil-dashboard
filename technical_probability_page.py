import datetime as dt

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

from charts import layout, panel, show, unavailable
from technical_copy import TEXT
from theme import COLORS, hero, kpi_grid, panel_head

SYMBOL = "BZ=F"
TZ = "Asia/Kuala_Lumpur"
SOURCE = "Source: Yahoo Finance (BZ=F), delayed"
DAILY_RANGES = {"3M": 63, "6M": 126, "1Y": 252, "2Y": 504}
INTRADAY_RANGES = {"1D": 1, "5D": 5, "1M": 22}
LEVEL_COLORS = {"R3": "#E5484D", "R2": "#EE7A7E", "R1": "#F5A9AC", "PP": "#F2A93B",
                "S1": "#8FD3A8", "S2": "#4CB87A", "S3": "#1F9D55"}
MAX_CELLS = 80_000_000  # steps x iterations, to keep memory bounded


# ---------------------------------------------------------------- data (each raises on failure; wrappers below catch)
@st.cache_data(ttl=900, show_spinner=False)
def daily_ohlc():
    df = yf.Ticker(SYMBOL).history(period="2y", interval="1d")[["Open", "High", "Low", "Close"]].dropna()
    if len(df) < 30:
        raise ValueError("Not enough daily data")
    df.index = df.index.tz_localize(None).normalize()
    return df


@st.cache_data(ttl=300, show_spinner=False)
def intraday_ohlc(interval):
    period = "1mo" if interval in ("5m", "15m", "30m") else "3mo"
    df = yf.Ticker(SYMBOL).history(period=period, interval=interval)[["Open", "High", "Low", "Close"]].dropna()
    if len(df) < 60:
        raise ValueError("Not enough intraday data")
    df.index = df.index.tz_convert(TZ)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def brent_history(end, years):
    start = pd.Timestamp(end) - pd.DateOffset(years=years)
    s = yf.Ticker(SYMBOL).history(start=start.date(), end=(pd.Timestamp(end) + pd.Timedelta(days=1)).date())["Close"].dropna()
    if len(s) < 30:
        raise ValueError("Not enough price history")
    s.index = s.index.tz_localize(None).normalize()
    return s


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _csv(s):
    return s.to_csv().encode("utf-8")


# ---------------------------------------------------------------- indicators
def rsi(close, n=14):
    d = close.diff()
    up, down = d.clip(lower=0), -d.clip(upper=0)
    ag, al = up.ewm(alpha=1 / n, adjust=False).mean(), down.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + ag / al)


def macd(close, fast=12, slow=26, signal=9):
    line = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig


def pivot_levels(df, basis):
    """Standard pivot points per bar, using the previous completed period's high, low and close."""
    key = {"Daily": df.index, "Weekly": df.index.to_period("W"), "Monthly": df.index.to_period("M")}[basis]
    agg = df.groupby(key).agg(H=("High", "max"), L=("Low", "min"), C=("Close", "last")).shift(1)
    pp = (agg["H"] + agg["L"] + agg["C"]) / 3
    lv = pd.DataFrame({
        "R3": agg["H"] + 2 * (pp - agg["L"]), "R2": pp + (agg["H"] - agg["L"]), "R1": 2 * pp - agg["L"], "PP": pp,
        "S1": 2 * pp - agg["H"], "S2": pp - (agg["H"] - agg["L"]), "S3": agg["L"] - 2 * (agg["H"] - pp),
    })
    out = lv.reindex(key)
    out.index = df.index
    return out


# ---------------------------------------------------------------- technical charts
def daily_fig(df, lv, start):
    v, lvv = df[df.index >= start], lv[lv.index >= start]
    fig = go.Figure(go.Candlestick(
        x=v.index, open=v["Open"], high=v["High"], low=v["Low"], close=v["Close"], name="Brent", showlegend=False,
        increasing=dict(line=dict(color=COLORS["up"]), fillcolor=COLORS["up"]),
        decreasing=dict(line=dict(color=COLORS["down"]), fillcolor=COLORS["down"]),
    ))
    # Segments must start and end on trading days: points inside the hidden weekend break are dropped by Plotly
    tail = pd.Timedelta(hours=18)
    for col in ["R3", "R2", "R1", "PP", "S1", "S2", "S3"]:
        s = lvv[col]
        grp = (s != s.shift()).cumsum()
        xs, ys = [], []
        for _, g in s.dropna().groupby(grp.loc[s.dropna().index]):
            xs += [g.index.min(), g.index.max() + tail, None]
            ys += [g.iloc[0], g.iloc[0], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=col, line=dict(color=LEVEL_COLORS[col], width=1.4),
                                 hoverinfo="skip", connectgaps=False))
        last = s.dropna()
        if len(last):
            fig.add_trace(go.Scatter(x=[v.index.max() + pd.Timedelta(days=1)], y=[last.iloc[-1]], mode="text", text=[f"{col} {last.iloc[-1]:.2f}"],
                                     textposition="middle right", textfont=dict(size=11, color=LEVEL_COLORS[col]),
                                     showlegend=False, hoverinfo="skip"))
    layout(fig, 560, hover="x")
    fig.update_layout(margin=dict(l=22, r=22, t=46, b=14))
    fig.update_xaxes(rangeslider=dict(visible=False), rangebreaks=[dict(bounds=["sat", "mon"])],
                     range=[v.index.min() - pd.Timedelta(days=1), v.index.max() + pd.Timedelta(days=max(10, int((v.index.max() - v.index.min()).days * 0.19)))])
    fig.update_yaxes(side="right", title_text="USD per barrel")
    return fig


def intraday_fig(df, days):
    r = rsi(df["Close"])
    line, sig, hist = macd(df["Close"])
    cutoff = df.index.max() - pd.Timedelta(days=days if days > 1 else 1.0)
    keep = df.index >= cutoff
    v, r, line, sig, hist = df[keep], r[keep], line[keep], sig[keep], hist[keep]
    labels = v.index.strftime("%a %d %b %H:%M")
    day = v.index.strftime("%a %d %b")
    first = [i for i in range(len(v)) if i == 0 or day[i] != day[i - 1]]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.58, 0.19, 0.23])
    fig.add_trace(go.Candlestick(x=labels, open=v["Open"], high=v["High"], low=v["Low"], close=v["Close"], name="Brent", showlegend=False,
                                 increasing=dict(line=dict(color=COLORS["up"]), fillcolor=COLORS["up"]),
                                 decreasing=dict(line=dict(color=COLORS["down"]), fillcolor=COLORS["down"])), row=1, col=1)
    fig.add_trace(go.Scatter(x=labels, y=r, mode="lines", name="RSI (14)", line=dict(color=COLORS["brand"], width=1.8),
                             hovertemplate="%{y:.1f}"), row=2, col=1)
    for y, dash in ((70, "dot"), (50, "dash"), (30, "dot")):
        fig.add_hline(y=y, line=dict(color=COLORS["muted"], width=1, dash=dash), row=2, col=1)
    fig.add_trace(go.Bar(x=labels, y=hist, name="Histogram", marker_color=[COLORS["up"] if h >= 0 else COLORS["down"] for h in hist],
                         hovertemplate="%{y:.3f}"), row=3, col=1)
    fig.add_trace(go.Scatter(x=labels, y=line, mode="lines", name="MACD (12, 26, 9)", line=dict(color=COLORS["blue"], width=1.6),
                             hovertemplate="%{y:.3f}"), row=3, col=1)
    fig.add_trace(go.Scatter(x=labels, y=sig, mode="lines", name="Signal", line=dict(color="#F2A93B", width=1.6),
                             hovertemplate="%{y:.3f}"), row=3, col=1)
    layout(fig, 720)
    fig.update_layout(margin=dict(l=44, r=22, t=46, b=14))
    fig.update_xaxes(type="category", rangeslider=dict(visible=False), tickmode="array",
                     tickvals=[labels[i] for i in first], ticktext=[day[i] for i in first], showgrid=False)
    fig.update_yaxes(side="right")
    fig.update_yaxes(title_text="USD per barrel", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    return fig


def level_table(lv, close):
    """Current pivot levels as a table, followed by where the last close sits relative to the main pivot."""
    row = lv.iloc[-1]
    if row.isna().any():
        return ""
    body = ""
    for k in ["R3", "R2", "R1", "PP", "S1", "S2", "S3"]:
        cls = "r" if k.startswith("R") else "s" if k.startswith("S") else "p"
        body += f'<tr class="lv-{cls}"><td>{k}</td><td>{row[k]:,.2f}</td></tr>'
    bias = "above" if close > row["PP"] else "below"
    return (f'<table class="gc-table"><thead><tr><th>Level</th><th>Price</th></tr></thead><tbody>{body}</tbody></table>'
            f'<p class="gc-small">Last close {close:,.2f} is <b>{bias}</b> the main pivot point ({row["PP"]:,.2f}).</p>')


# ---------------------------------------------------------------- Monte Carlo
def _monthly_last(close):
    try:
        return close.resample("ME").last()
    except ValueError:  # older pandas
        return close.resample("M").last()


def simulate(S0, drift, stdev, steps, iterations):
    z = np.random.default_rng().standard_normal((steps, iterations))
    r = np.exp(drift + stdev * z)
    r[0] = 1.0
    return S0 * np.cumprod(r, axis=0)  # same recursion as the original loop: P[0] = S0, P[t] = P[t-1] * r[t]


PCTS = [1, 5, 30, 80, 95, 99]
VOL_MODES = ["1 year", "2 years", "5 years", "Full history", "Custom"]
VOL_YEARS = {"1 year": 1, "2 years": 2, "5 years": 5}
MIN_OBS = {"daily": 30, "monthly": 6}  # minimum returns needed to estimate a volatility


def _log_returns(kind, close):
    series = close if kind == "daily" else _monthly_last(close)
    return series, np.log(1 + series.pct_change())


def realised_vols(kind, end_date, years):
    """Annualised realised volatility over each lookback, to help choose one."""
    close = _safe(brent_history, end_date, max(years, 5))
    if close is None:
        return None
    series, lr = _log_returns(kind, close)
    ann = np.sqrt(252 if kind == "daily" else 12)
    last = series.index[-1]
    out = {}
    for label, y in VOL_YEARS.items():
        w = lr[lr.index > last - pd.DateOffset(years=y)].dropna()
        if len(w) >= MIN_OBS[kind]:
            out[label] = float(w.std() * ann)
    hist = lr if max(years, 5) == years else lr[lr.index > last - pd.DateOffset(years=years)]
    out[f"Full history ({years}y)"] = float(hist.dropna().std() * ann)
    return out


def run_mc(kind, end_date, future_date, years, iterations, vol_mode="Full history", custom_vol=None):
    lookback = VOL_YEARS.get(vol_mode)
    close = brent_history(end_date, max(years, lookback or 0))
    series, lr = _log_returns(kind, close)
    last_date = series.index[-1]
    if kind == "daily":
        steps = (pd.Timestamp(future_date) - last_date).days
        unit, per_year = "days", 252
    else:
        steps = (pd.Timestamp(future_date) - last_date).days // 30
        unit, per_year = "months", 12
    if steps < 2:
        raise ValueError("Choose a forecast date at least two periods after the last price date.")
    if steps * iterations > MAX_CELLS:
        raise ValueError("That horizon is too long for this many iterations. Shorten the horizon or lower the iterations.")

    # Drift: mean log return over the history window. Volatility: from the chosen lookback, or typed in (annualised).
    lr_hist = lr if len(close) and max(years, lookback or 0) == years else lr[lr.index > last_date - pd.DateOffset(years=years)]
    u = lr_hist.mean()
    if vol_mode == "Custom":
        if not custom_vol or custom_vol <= 0:
            raise ValueError("Enter an annualised volatility above zero.")
        stdev = float(custom_vol) / 100 / np.sqrt(per_year)
        vol_label = "Custom input"
    elif vol_mode == "Full history":
        stdev = float(lr_hist.std())
        vol_label = f"Full history ({years}y)"
    else:
        w = lr[lr.index > last_date - pd.DateOffset(years=lookback)].dropna()
        if len(w) < MIN_OBS[kind]:
            raise ValueError(f"Not enough price history for a {vol_mode} volatility lookback.")
        stdev = float(w.std())
        vol_label = f"{vol_mode} lookback"
    drift = float(u - 0.5 * stdev ** 2)
    S0 = float(series.iloc[-1])
    paths = simulate(S0, drift, stdev, steps, iterations)

    final = paths[-1].copy()
    pooled = np.percentile(paths, PCTS)
    final_p = np.percentile(final, PCTS)
    band = np.percentile(paths, [5, 30, 80, 95], axis=1)
    if kind == "daily":
        dates = [last_date + pd.Timedelta(days=i) for i in range(steps)]
        roll = lr.rolling(252).std() * np.sqrt(252)
        roll_label = "Rolling 252-day volatility (annualised)"
        if roll.dropna().empty:
            roll = lr.rolling(63).std() * np.sqrt(252)
            roll_label = "Rolling 63-day volatility (annualised)"
        vol = dict(daily=stdev, monthly=stdev * np.sqrt(21), annual=stdev * np.sqrt(252))
        recent = series.iloc[-126:]
    else:
        dates = list(pd.date_range(start=last_date, periods=steps, freq="ME"))
        roll = lr.rolling(12).std() * np.sqrt(12)
        roll_label = "Rolling 12-month volatility (annualised)"
        vol = dict(monthly=stdev, annual=stdev * np.sqrt(12))
        recent = series.iloc[-24:]

    return dict(
        kind=kind, unit=unit, inputs=(end_date, future_date, years, iterations), S0=S0, vol_mode=vol_mode, vol_label=vol_label,
        custom_vol=custom_vol, stdev=stdev, drift=drift, key=(kind, end_date, future_date, years, iterations, vol_mode, custom_vol), last_date=last_date, price_date=close.index[-1], steps=steps,
        iterations=iterations, vol=vol, mean_pooled=float(paths.mean()), mean_final=float(final.mean()),
        pooled=pooled, final_p=final_p, final=final, mean_path=paths.mean(axis=1), band=band, dates=dates,
        hist=close, hist_series=series, roll=roll, roll_label=roll_label, recent=recent,
    )


def mc_paths_fig(res):
    c = COLORS
    d = res["dates"]
    fig = go.Figure()
    rec = res["recent"]
    fig.add_trace(go.Scatter(x=rec.index, y=rec.values, mode="lines", name="Recent actual", line=dict(color=c["muted"], width=1.8),
                             hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=d, y=res["band"][3], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=d, y=res["band"][0], mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(0,169,157,0.12)",
                             name="P5 to P95", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=d, y=res["mean_path"], mode="lines", name="Mean path", line=dict(color=c["brand"], width=2.4),
                             hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=d, y=res["band"][1], mode="lines", name="P30", line=dict(color=c["down"], width=1.8, dash="dash"),
                             hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=d, y=res["band"][2], mode="lines", name="P80", line=dict(color="#F2A93B", width=1.8, dash="dash"),
                             hovertemplate="%{y:.2f}"))
    layout(fig, 430)
    fig.update_yaxes(title_text="USD per barrel")
    return fig


def mc_hist_fig(res):
    c = COLORS
    f = res["final"]
    fig = go.Figure(go.Histogram(x=f, nbinsx=100, marker=dict(color=c["brand"], line=dict(width=0)), opacity=0.85, name="Final price",
                                 hovertemplate="%{x:.1f}: %{y}<extra></extra>"))
    for x, label, color, pos in ((float(f.mean()), "Mean", c["ink"], "top"),
                                 (float(np.percentile(f, 30)), "P30", c["down"], "top left"),
                                 (float(np.percentile(f, 80)), "P80", "#F2A93B", "top right")):
        fig.add_vline(x=x, line=dict(color=color, width=1.6, dash="dash"), annotation_text=f"{label} {x:.1f}",
                      annotation_position=pos, annotation_font=dict(size=11, color=color))
    layout(fig, 430, legend=False, hover="closest")
    fig.update_layout(margin=dict(l=22, r=22, t=30, b=14), bargap=0.05)
    fig.update_xaxes(title_text="Price at forecast date (USD per barrel)")
    fig.update_yaxes(title_text="Frequency")
    return fig


def mc_history_fig(res):
    c = COLORS
    h, roll = res["hist"], res["roll"]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=h.index, y=h.values, mode="lines", name="Brent price", line=dict(color=c["brand"], width=2.2),
                             hovertemplate="%{y:.2f}"), secondary_y=False)
    fig.add_trace(go.Scatter(x=roll.index, y=roll.values, mode="lines", name=res["roll_label"], line=dict(color="#F2A93B", width=1.8),
                             hovertemplate="%{y:.1%}"), secondary_y=True)
    fig.add_trace(go.Scatter(x=[h.index.min(), h.index.max()], y=[res["vol"]["annual"]] * 2, mode="lines", name="Volatility used",
                             line=dict(color=c["ink"], width=1.4, dash="dash"), hovertemplate="%{y:.1%}"), secondary_y=True)
    layout(fig, 430)
    fig.update_yaxes(title_text="USD per barrel", secondary_y=False)
    fig.update_yaxes(title_text="Volatility", tickformat=".0%", showgrid=False, secondary_y=True)
    return fig


def pct_table(res):
    rows = [("Mean", res["mean_pooled"], res["mean_final"], True)]
    rows += [(f"P{p}", a, b, False) for p, a, b in zip(PCTS, res["pooled"], res["final_p"])]
    body = "".join(
        f'<tr><td>{name}</td><td class="{"hl" if hl else ""}">{a:,.2f}</td><td class="{"hl" if hl else ""}">{b:,.2f}</td></tr>'
        for name, a, b, hl in rows
    )
    return ('<table class="gc-table"><thead><tr><th></th><th>All simulated {u}</th><th>At forecast date</th></tr></thead>'
            f"<tbody>{body}</tbody></table>").replace("{u}", "days" if res["kind"] == "daily" else "months")


def render_mc(res):
    S0, ann = res["S0"], res["vol"]["annual"]
    end_date, future_date, years, iters = res["inputs"]
    detail = (f"Daily {res['vol']['daily'] * 100:.2f}% \u00B7 Monthly (21 days) {res['vol']['monthly'] * 100:.2f}%"
              if res["kind"] == "daily" else f"Monthly {res['vol']['monthly'] * 100:.2f}%")
    vol_sub = f"{res['vol_label']}<br>{detail}"
    chg = (res["mean_pooled"] / S0 - 1) * 100
    arrow = "\u25B2" if chg > 0 else "\u25BC" if chg < 0 else ""
    kpi_grid([
        dict(label="Current closing price", value=f"{S0:,.2f}", sub=f"USD per barrel \u00B7 {res['price_date']:%d %b %Y}"),
        dict(label="Forecast horizon", value=f"{res['steps']} {res['unit']}", sub=f"To {pd.Timestamp(future_date):%d %b %Y} \u00B7 {iters:,} iterations"),
        dict(label="Expected average price", value=f"{res['mean_pooled']:,.2f}", pill=f"{arrow} {abs(chg):.1f}% vs current",
             pill_cls="flat", sub="Mean of all simulated prices"),
        dict(label="Volatility (annualised)", value=f"{ann * 100:.1f}%", sub=vol_sub),
    ], cols=4)

    left, right = st.columns([1.7, 1], gap="medium")
    with left:
        with panel(f"mc_{res['kind']}_paths"):
            panel_head("Key paths", "Mean path with the 30th and 80th percentile paths, and the 5th to 95th percentile band.")
            show(mc_paths_fig(res), f"mc_{res['kind']}_paths_chart")
            st.caption(SOURCE)
    with right:
        with panel(f"mc_{res['kind']}_table"):
            panel_head("Price distribution", "Simulated prices in USD per barrel.")
            st.markdown(pct_table(res), unsafe_allow_html=True)
            st.markdown('<p class="gc-small">"All simulated" pools every price on every day and path. "At forecast date" uses only the final day.</p>',
                        unsafe_allow_html=True)
            st.download_button("Download price history as CSV", _csv(res["hist"][::-1].rename("Close")), file_name="Brent_Price.csv",
                               mime="text/csv", key=f"mc_{res['kind']}_dl")

    a, b = st.columns(2, gap="medium")
    with a:
        with panel(f"mc_{res['kind']}_hist"):
            panel_head("Distribution of final prices", "Simulated Brent price on the forecast date. Lines mark the mean, P30 and P80 of this distribution.")
            show(mc_hist_fig(res), f"mc_{res['kind']}_hist_chart")
    with b:
        with panel(f"mc_{res['kind']}_history"):
            panel_head("Historical price and rolling volatility", "The price history used to calibrate the simulation.")
            show(mc_history_fig(res), f"mc_{res['kind']}_history_chart")
            st.caption(SOURCE)


def _default_forecast(kind):
    """Daily: this year-end (or next if under 60 days remain). Monthly: next year-end, so there are enough monthly steps."""
    today = dt.date.today()
    year_end = dt.date(today.year, 12, 31)
    if kind == "monthly" or (year_end - today).days <= 60:
        return dt.date(today.year + 1, 12, 31)
    return year_end


def mc_tab(kind):
    ss = f"mc_{kind}_result"
    st.markdown(f'<p class="gc-lead">{"Daily" if kind == "daily" else "Monthly"} Monte Carlo simulation of Brent prices, calibrated on historical log returns.</p>',
                unsafe_allow_html=True)
    with st.expander("How the simulation works"):
        st.markdown(TEXT["mc_daily" if kind == "daily" else "mc_monthly"])
        per = "daily" if kind == "daily" else "monthly"
        st.markdown(
            f"**Volatility lookback.** Choose how the volatility is estimated: the standard deviation of {per} log returns over the last "
            "1, 2 or 5 years, over the full history set by the slider (the original behaviour), or type your own annualised volatility. "
            f"An annualised figure is scaled to each step by dividing by the square root of {252 if kind == 'daily' else 12}. "
            "The drift is the average log return over the history window less half the squared volatility being used, "
            "so it follows the volatility you choose."
        )

    today = dt.date.today()
    with panel(f"mc_{kind}_inputs"):
        panel_head("Simulation inputs")
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1.25, 1, 0.9])
        with c1:
            end_date = st.date_input("Current date", today - dt.timedelta(days=1), max_value=today - dt.timedelta(days=1), key=f"mc_{kind}_end")
        with c2:
            future = st.date_input("Forecast date", max(_default_forecast(kind), end_date + dt.timedelta(days=2)),
                                   min_value=end_date + dt.timedelta(days=1), key=f"mc_{kind}_future")
        with c3:
            years = st.slider("Years of history", 1, 10, 10, key=f"mc_{kind}_years",
                              help="Sets the price history used for the drift and shown in the history chart. Volatility is chosen below.")
        with c4:
            iters = st.selectbox("Iterations", [5000, 10000, 25000], index=1, key=f"mc_{kind}_iters")
        with c5:
            st.markdown('<div style="height:1.75rem"></div>', unsafe_allow_html=True)
            run = st.button("Run simulation", type="primary", key=f"mc_{kind}_run", use_container_width=True)

        v1, v2, _ = st.columns([2.6, 1.2, 1.4])
        with v1:
            vol_mode = st.segmented_control("Volatility lookback", VOL_MODES, default="Full history", key=f"mc_{kind}_vol") or "Full history"
        custom = None
        with v2:
            if vol_mode == "Custom":
                custom = st.number_input("Annualised volatility (%)", min_value=1.0, max_value=200.0, value=30.0, step=0.5,
                                         key=f"mc_{kind}_custom")
        rv = realised_vols(kind, end_date, years)
        if rv:
            basis = "daily returns" if kind == "daily" else "monthly returns"
            chips = " \u00B7 ".join(f"{k} <b>{v * 100:.1f}%</b>" for k, v in rv.items())
            st.markdown(f'<p class="gc-small" style="margin-bottom:10px">Realised volatility, annualised, from {basis}: {chips}</p>', unsafe_allow_html=True)

    key = (kind, end_date, future, years, iters, vol_mode, custom)
    cur = st.session_state.get(ss)
    if run or cur is None or cur.get("key") != key:
        try:
            with st.spinner("Running simulation"):
                st.session_state[ss] = run_mc(kind, end_date, future, years, iters, vol_mode, custom)
        except ValueError as e:
            st.session_state.pop(ss, None)
            with panel(f"mc_{kind}_err"):
                unavailable("Could not run the simulation", str(e))
            return
        except Exception:
            st.session_state.pop(ss, None)
            with panel(f"mc_{kind}_err"):
                unavailable("Price history unavailable", "Yahoo Finance could not be reached. Try again shortly.")
            return
    render_mc(st.session_state[ss])


# ---------------------------------------------------------------- technical tab
def technical_tab():
    st.markdown(f'<p class="gc-lead">{TEXT["tech_intro"]}</p>', unsafe_allow_html=True)

    with panel("tech_daily"):
        panel_head("Daily price with pivot points", "Standard pivot points from the previous period's high, low and close.")
        c1, c2, _ = st.columns([1.3, 1.5, 2])
        with c1:
            rng = st.segmented_control("Range", list(DAILY_RANGES), default="6M", key="tech_d_range", label_visibility="collapsed") or "6M"
        with c2:
            basis = st.segmented_control("Pivot basis", ["Weekly", "Monthly", "Daily"], default="Weekly", key="tech_d_basis",
                                         label_visibility="collapsed") or "Weekly"
        df = _safe(daily_ohlc)
        if df is None:
            unavailable("Price data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
        else:
            lv = pivot_levels(df, basis)
            start = df.index[-DAILY_RANGES[rng]]
            left, right = st.columns([1, 3.6], gap="medium")
            with left:
                st.markdown(level_table(lv, float(df["Close"].iloc[-1])), unsafe_allow_html=True)
            with right:
                show(daily_fig(df, lv, start), "tech_daily_chart")
        st.caption(SOURCE + ". Pivot basis is the period the levels are calculated from.")
    with st.expander("About pivot points"):
        st.markdown(TEXT["pivot"])

    with panel("tech_intraday"):
        panel_head("Intraday price with RSI and MACD", "Times are shown in Malaysia time (MYT).")
        c1, c2, _ = st.columns([1.5, 1.3, 2])
        with c1:
            interval = st.segmented_control("Interval", ["5m", "15m", "30m", "1h"], default="15m", key="tech_i_interval",
                                            label_visibility="collapsed") or "15m"
        with c2:
            days = st.segmented_control("Window", list(INTRADAY_RANGES), default="5D", key="tech_i_range", label_visibility="collapsed") or "5D"
        idf = _safe(intraday_ohlc, interval)
        if idf is None:
            unavailable("Intraday data unavailable", "Yahoo Finance could not be reached. Try again shortly.")
        else:
            show(intraday_fig(idf, INTRADAY_RANGES[days]), "tech_intraday_chart")
        st.caption(SOURCE)
    with st.expander("About RSI and MACD"):
        st.markdown(TEXT["rsi_macd"])


# ---------------------------------------------------------------- page
def technical_probability_page():
    hero("Technical and Probability Analysis",
         "Pivot points, momentum indicators and Monte Carlo price scenarios for Brent crude.",
         "Source<br>Yahoo Finance (BZ=F)", slim=True)
    t1, t2, t3 = st.tabs(["Technical Analysis", "MonteCarlo Analysis (Daily)", "MonteCarlo Analysis (Monthly)"])
    with t1:
        technical_tab()
    with t2:
        mc_tab("daily")
    with t3:
        mc_tab("monthly")

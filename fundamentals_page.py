from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

from app_secrets import get_secret
from charts import layout, legend_swatch, panel, show, unavailable
from fundamentals_copy import TEXT
from theme import COLORS, PALETTE_LONG, hero, kpi_grid, panel_head

STEO_URL = "https://api.eia.gov/v2/steo/data/"
WEEKLY_URL = "https://api.eia.gov/v2/petroleum/sum/sndw/data/"
MBD = "Volume (million barrels per day)"

# ---------------------------------------------------------------- series definitions (labels in plot order)
WORLD_BREAKDOWN = {  # annual; "Other" is world minus the two groups below
    "PAPR_OPECPLUS_OPEC": "OPEC members",
    "PAPR_OPECPLUS_OTHER": "Additional OPEC+ members",
}
OPEC_MEMBERS = {
    "PAPR_AG": "Algeria", "PAPR_CF": "Congo (Brazzaville)", "PAPR_EK": "Equatorial Guinea", "PAPR_GB": "Gabon",
    "PAPR_IR": "Iran", "PAPR_IZ": "Iraq", "PAPR_KU": "Kuwait", "PAPR_LY": "Libya", "PAPR_NI": "Nigeria",
    "PAPR_SA": "Saudi Arabia", "PAPR_TC": "United Arab Emirates", "PAPR_VE": "Venezuela",
}
OPECPLUS_OTHER = {
    "PAPR_AJ": "Azerbaijan", "PAPR_BA": "Bahrain", "PAPR_BX": "Brunei", "PAPR_KZ": "Kazakhstan", "PAPR_MY": "Malaysia",
    "PAPR_MX": "Mexico", "PAPR_MU": "Oman", "PAPR_RS": "Russia", "PAPR_OD": "South Sudan", "PAPR_SU": "Sudan",
}
NON_OPEC_NAMED = {  # subtracted from "non-OPEC+ ex-US" to leave "Others"
    "PAPR_CA": "Canada", "PAPR_AR": "Argentina", "PAPR_BR": "Brazil", "PAPR_CO": "Colombia", "PAPR_GY": "Guyana",
    "PAPR_NO": "Norway", "PAPR_UK": "United Kingdom", "PAPR_QA": "Qatar", "PAPR_AO": "Angola", "PAPR_EG": "Egypt",
    "PAPR_CH": "China", "PAPR_IN": "India", "PAPR_ID": "Indonesia",
}
NON_OPEC_ORDER = ["PAPR_CA", "PAPR_US", "PAPR_AR", "PAPR_BR", "PAPR_CO", "PAPR_GY", "PAPR_NO", "PAPR_UK", "PAPR_QA",
                  "PAPR_AO", "PAPR_EG", "PAPR_CH", "PAPR_IN", "PAPR_ID"]
CONSUMPTION = {
    "PATC_CA": "Canada", "PATC_OECD_EUROPE": "Europe OECD", "PATC_JA": "Japan", "PATC_US": "United States",
    "PATC_UST": "U.S. Territories", "PATC_OTHER_OECD": "Other OECD", "PATC_CH": "China", "PATC_FSU": "Eurasia",
    "PATC_NONOECD_EUROPE": "Europe non-OECD", "PATC_OTHER_ASIA": "Other Asia", "PATC_OTHER_NONOECD": "Other Non-OECD",
}
OECD = ["PATC_CA", "PATC_OECD_EUROPE", "PATC_JA", "PATC_US", "PATC_UST", "PATC_OTHER_OECD"]
NON_OECD = ["PATC_CH", "PATC_FSU", "PATC_NONOECD_EUROPE", "PATC_OTHER_ASIA", "PATC_OTHER_NONOECD"]
MONTHLY = {"COPR_OPECPLUS": "OPEC+", "COPRPUS": "US", "COPR_NONOPECPLUS_XUS": "Non-OPEC+ ex-US"}
STOCKS = {
    "WCESTUS1": ("Crude oil (ex-SPR)", "U.S. Ending Stocks excluding SPR of Crude Oil"),
    "WGTSTUS1": ("Gasoline", "U.S. Ending Stocks of Total Gasoline"),
    "WDISTUS1": ("Distillate", "U.S. Ending Stocks of Distillate Fuel Oil"),
}
SPR_SERIES = "WCSSTUS1"
RANGE_DAYS = {"6M": 182, "1Y": 365, "2Y": 730, "5Y": 1826}


# ---------------------------------------------------------------- data (each raises on failure; wrappers below catch)
def _key():
    return get_secret("EIA_API_KEY", "eia", "api_key")


def _verify():
    insecure = get_secret("EIA_INSECURE_SSL") == "1"
    if insecure:
        requests.packages.urllib3.disable_warnings()
    return not insecure


def _get_rows(url, params, verify):
    rows, offset = [], 0
    while True:
        r = requests.get(url, params={**params, "offset": offset}, timeout=30, verify=verify)
        r.raise_for_status()
        resp = r.json()["response"]
        chunk = resp.get("data", [])
        rows += chunk
        offset += len(chunk)
        if not chunk or offset >= int(resp.get("total", offset)):
            return rows


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _steo(series_ids, frequency, start, key, verify):
    rows = _get_rows(STEO_URL, {
        "api_key": key, "frequency": frequency, "data[]": "value", "start": start,
        "facets[seriesId][]": list(series_ids), "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 5000,
    }, verify)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No data returned")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    wide = df.pivot_table(index="period", columns="seriesId", values="value", aggfunc="first").sort_index()
    if frequency == "annual":
        wide.index = wide.index.astype(int)
    return wide.reindex(columns=list(series_ids))


def steo(series_ids, frequency="annual", start="2000"):
    key = _key()
    if not key:
        return None
    try:
        return _steo(tuple(series_ids), frequency, start, key, _verify())
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def _weekly(series, start, key, verify):
    rows = _get_rows(WEEKLY_URL, {
        "api_key": key, "frequency": "weekly", "data[0]": "value", "facets[series][]": series, "start": start,
        "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 5000,
    }, verify)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No data returned")
    df["date"] = pd.to_datetime(df["period"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["date", "value"]].dropna().sort_values("date").reset_index(drop=True)


def weekly(series):
    key = _key()
    if not key:
        return None
    start = (datetime.now() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")
    try:
        return _weekly(series, start, key, _verify())
    except Exception:
        return None


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def brent_close():
    s = yf.Ticker("BZ=F").history(start="2014-01-01")["Close"].dropna()
    if s.empty:
        raise ValueError("No prices")
    return s


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def csv_bytes(df):
    return df.to_csv().encode("utf-8")


# ---------------------------------------------------------------- charts
def _forecast_band(fig, years):
    """Shade the EIA forecast period (the current and following year) on annual charts."""
    now = datetime.now().year
    if len(years) and max(years) >= now:
        fig.add_vrect(x0=now - 0.5, x1=max(years) + 0.5, fillcolor="rgba(36,145,207,0.08)", line_width=0, layer="below")
        legend_swatch(fig, "EIA forecast period", "rgba(36,145,207,0.35)")


def stacked_bar(wide, columns, labels, height=480, totals=True):
    fig = go.Figure()
    for i, col in enumerate(columns):
        fig.add_trace(go.Bar(x=wide.index, y=wide[col], name=labels[col], marker_color=PALETTE_LONG[i % len(PALETTE_LONG)],
                             hovertemplate="%{y:.2f}"))
    if totals:
        t = wide[columns].sum(axis=1)
        fig.add_trace(go.Scatter(x=wide.index, y=t, mode="text", text=[f"{v:.1f}" for v in t], textposition="top center",
                                 textfont=dict(size=11, color=COLORS["ink"]), showlegend=False, hoverinfo="skip"))
    fig.update_layout(barmode="stack")
    _forecast_band(fig, list(wide.index))
    layout(fig, height)
    fig.update_yaxes(title_text=MBD)
    fig.update_xaxes(dtick=1 if len(wide) <= 30 else None)
    return fig


def pc_fig(x, prod, cons, annual):
    fig = go.Figure()
    mode = "lines+markers" if annual else "lines"
    fig.add_trace(go.Scatter(x=x, y=prod, mode=mode, name="Production", line=dict(color=COLORS["brand"], width=2.4),
                             marker=dict(size=6), hovertemplate="%{y:.2f}"))
    fig.add_trace(go.Scatter(x=x, y=cons, mode=mode, name="Consumption", line=dict(color=COLORS["blue"], width=2.4),
                             marker=dict(size=6), hovertemplate="%{y:.2f}"))
    if annual:
        _forecast_band(fig, list(x))
    layout(fig, 430)
    fig.update_yaxes(title_text=MBD)
    return fig


def balance_fig(x, bal, annual):
    colors = [COLORS["up"] if v >= 0 else COLORS["down"] for v in bal]
    fig = go.Figure(go.Bar(x=x, y=bal, marker_color=colors, name="Oversupply / undersupply", showlegend=False, hovertemplate="%{y:.2f}",
                           text=[f"{v:.2f}" for v in bal] if annual else None, textposition="outside",
                           textfont=dict(size=10, color=COLORS["muted"]), cliponaxis=False))
    if annual:
        _forecast_band(fig, list(x))
    layout(fig, 430, legend=annual)
    fig.update_yaxes(title_text=MBD, zeroline=True, zerolinecolor=COLORS["muted"], zerolinewidth=1)
    return fig


def lines_fig(monthly):
    fig = go.Figure()
    for col, color in zip(MONTHLY, [COLORS["brand"], COLORS["blue"], "#F2A93B"]):
        fig.add_trace(go.Scatter(x=monthly.index, y=monthly[col], name=MONTHLY[col] + " production",
                                 line=dict(color=color, width=2.2), hovertemplate="%{y:.2f}"))
    layout(fig, 430)
    fig.update_yaxes(title_text=MBD)
    return fig


def share_fig(share):
    fig = go.Figure(go.Scatter(x=share.index, y=share, mode="lines", name="OPEC+ market share",
                               line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:.1f}%"))
    layout(fig, 430, legend=False)
    fig.update_yaxes(title_text="Market share (%)", ticksuffix="%", rangemode="normal")
    return fig


def area100_fig(monthly):
    fig = go.Figure()
    for col, color in zip(MONTHLY, [COLORS["brand"], COLORS["blue"], "#F2A93B"]):
        fig.add_trace(go.Scatter(x=monthly.index, y=monthly[col], name=MONTHLY[col] + " production", mode="none",
                                 stackgroup="one", groupnorm="percent", fillcolor=color, hovertemplate="%{y:.1f}%"))
    layout(fig, 400)
    fig.update_yaxes(title_text="Production (%)", ticksuffix="%", range=[0, 100])
    return fig


def seasonality_table(close, rule, unit):
    try:
        res = close.resample(rule).last()
    except ValueError:  # older pandas
        res = close.resample(rule.replace("ME", "M").replace("QE", "Q")).last()
    pct = res.pct_change() * 100
    parts = [(i.year, i.month if unit == "Month" else i.quarter) for i in pct.index]
    pct.index = pd.MultiIndex.from_tuples(parts, names=["Year", unit])
    return pct.unstack(level=unit)


def heatmap_fig(table, labels):
    z = table.values
    text = [["" if pd.isna(v) else f"{v:.1f}" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=[str(y) for y in table.index], text=text, texttemplate="%{text}",
        textfont=dict(size=11), zmin=-10, zmax=10, zmid=0, hoverongaps=False, xgap=2, ygap=2,
        colorscale=[[0, COLORS["down"]], [0.5, "#FFFFFF"], [1, COLORS["brand"]]],
        colorbar=dict(title=dict(text="%", side="right"), thickness=12, len=0.9),
        hovertemplate="%{y} %{x}: %{z:.2f}%<extra></extra>",
    ))
    layout(fig, 470, legend=False, hover="closest")
    fig.update_layout(margin=dict(l=22, r=22, t=14, b=14))
    fig.update_xaxes(side="top", showline=False)
    fig.update_yaxes(type="category", showgrid=False)
    return fig


def wow_fig(df, name):
    d = df.copy()
    d["chg"] = d["value"].diff()
    d = d.dropna()
    fig = go.Figure(go.Bar(x=d["date"], y=d["chg"], name="Week-on-week change",
                           marker_color=[COLORS["up"] if v > 0 else COLORS["down"] for v in d["chg"]],
                           hovertemplate="%{y:,.0f} k bbl"))
    layout(fig, 420, legend=False)
    fig.update_yaxes(title_text="W-o-W change (thousand barrels)")
    return fig


def week_stats(df):
    """5-year min / max / average by week of year (same grouping as the original charts)."""
    wk = df["date"].dt.strftime("%U")
    g = df.groupby(wk)["value"]
    out = df.copy()
    out["week"] = wk
    out["min5"], out["max5"], out["avg5"] = wk.map(g.min()), wk.map(g.max()), wk.map(g.mean())
    return out


def range_fig(stats, start, with_avg=True):
    v = stats[stats["date"] >= start]
    x = list(v["date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x + x[::-1], y=list(v["max5"]) + list(v["min5"])[::-1], fill="toself",
                             fillcolor="rgba(0,169,157,0.14)", line=dict(width=0), hoverinfo="skip", name="5-year range"))
    if with_avg:
        fig.add_trace(go.Scatter(x=v["date"], y=v["avg5"], mode="lines", name="5-year average",
                                 line=dict(color="#F2A93B", width=1.8, dash="dash"), hovertemplate="%{y:,.0f}"))
    fig.add_trace(go.Scatter(x=v["date"], y=v["value"], mode="lines", name="Actual",
                             line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:,.0f}"))
    layout(fig, 420)
    fig.update_yaxes(title_text="Thousand barrels")
    return fig


# ---------------------------------------------------------------- small UI helpers
def _need_key(tab):
    with panel(f"fund_nokey_{tab}"):
        unavailable("EIA API key not set",
                    "Add <code>EIA_API_KEY</code> to your Streamlit secrets (or environment) to load EIA data.")


def _chart_panel(key, title, note, fig, source="Source: EIA"):
    with panel(key):
        panel_head(title, note)
        if fig is None:
            unavailable("Data unavailable", "The source could not be reached. Try again shortly.")
        else:
            show(fig, key)
        st.caption(source)


def _download(label, df, name, key):
    st.download_button(label, csv_bytes(df), file_name=name, mime="text/csv", key=key)


def _arrow(d):
    return "\u25B2" if d > 0 else "\u25BC" if d < 0 else ""


def _seg(label, options, key, default=None):
    return st.segmented_control(label, options, default=default or options[0], key=key, label_visibility="collapsed") or (default or options[0])


# ---------------------------------------------------------------- tab: balances
def balances_tab():
    if not _key():
        return _need_key("bal")
    ids = ["PAPR_WORLD", "PATC_WORLD"]
    ann, qtr = steo(ids, "annual"), steo(ids, "quarterly")

    if ann is not None and ann.dropna().shape[0] > 1:
        a = ann.dropna()
        now = datetime.now().year
        y = now if now in a.index else int(a.index.max())
        P, C = a.loc[y, "PAPR_WORLD"], a.loc[y, "PATC_WORLD"]
        pp, cp = a["PAPR_WORLD"].get(y - 1), a["PATC_WORLD"].get(y - 1)
        tag = "forecast" if y >= now else "actual"

        def delta(cur, prev):
            if prev is None or pd.isna(prev):
                return {}
            d = cur - prev
            return dict(pill=f"{_arrow(d)} {abs(d):.2f} vs {y - 1}", pill_cls="flat")

        bal = P - C
        y2 = y + 1 if (y + 1) in a.index else None
        cards = [
            dict(label=f"World production, {y}", value=f"{P:.2f}", sub=f"Million barrels per day \u00B7 EIA {tag}", **delta(P, pp)),
            dict(label=f"World consumption, {y}", value=f"{C:.2f}", sub=f"Million barrels per day \u00B7 EIA {tag}", **delta(C, cp)),
            dict(label=f"Balance, {y}", value=f"{bal:+.2f}", pill="Oversupply" if bal >= 0 else "Undersupply",
                 pill_cls="up" if bal >= 0 else "down", sub="Production minus consumption, mb/d"),
        ]
        if y2:
            b2 = a.loc[y2, "PAPR_WORLD"] - a.loc[y2, "PATC_WORLD"]
            cards.append(dict(label=f"Balance, {y2}", value=f"{b2:+.2f}", pill="Oversupply" if b2 >= 0 else "Undersupply",
                              pill_cls="up" if b2 >= 0 else "down", sub="EIA forecast, mb/d"))
        kpi_grid(cards, cols=len(cards))

    freq = _seg("Frequency", ["Annual", "Quarterly"], "fund_bal_freq")
    d = ann if freq == "Annual" else qtr
    annual = freq == "Annual"
    if d is not None:
        d = d.fillna(0)
        bal_series = d["PAPR_WORLD"] - d["PATC_WORLD"]

    left, right = st.columns(2, gap="medium")
    with left:
        _chart_panel("bal_pc", "Production vs consumption", "World petroleum and other liquids.",
                     pc_fig(d.index, d["PAPR_WORLD"], d["PATC_WORLD"], annual) if d is not None else None)
    with right:
        _chart_panel("bal_bal", "Oversupply / undersupply", "Production minus consumption. Green is oversupply, red is undersupply.",
                     balance_fig(d.index, bal_series, annual) if d is not None else None)

    with st.expander("About the balances"):
        st.markdown(TEXT["balances"])
    with st.expander("Other sources of supply-demand balances (may require paid subscriptions)"):
        st.markdown(TEXT["other_sources"])
    if d is not None:
        out = d.rename(columns={"PAPR_WORLD": "Production", "PATC_WORLD": "Consumption"}).copy()
        out["Oversupply/Undersupply"] = bal_series
        _download("Download data as CSV", out, "OilBalances.csv", "dl_balances")


# ---------------------------------------------------------------- tab: production
def production_tab():
    if not _key():
        return _need_key("prod")
    view = _seg("View", ["Annual breakdown", "Monthly trends"], "fund_prod_view")

    if view == "Annual breakdown":
        ids = ["PAPR_WORLD", *WORLD_BREAKDOWN]
        w = steo(ids, "annual")
        fig = None
        if w is not None:
            w = w.copy()
            w["OTHER"] = w["PAPR_WORLD"] - w["PAPR_OPECPLUS_OPEC"] - w["PAPR_OPECPLUS_OTHER"]
            labels = {**WORLD_BREAKDOWN, "OTHER": "Other production"}
            fig = stacked_bar(w, [*WORLD_BREAKDOWN, "OTHER"], labels, height=470)
        _chart_panel("prod_total", "World production breakdown", TEXT["production"], fig)

        group = _seg("Group", ["OPEC members", "Additional OPEC+ members", "Non-OPEC"], "fund_prod_group")
        if group == "OPEC members":
            g = steo(list(OPEC_MEMBERS), "annual")
            fig = stacked_bar(g, list(OPEC_MEMBERS), OPEC_MEMBERS, height=520) if g is not None else None
            _chart_panel("prod_group", "OPEC member production", TEXT["opec_note"], fig)
        elif group == "Additional OPEC+ members":
            g = steo(list(OPECPLUS_OTHER), "annual")
            fig = stacked_bar(g, list(OPECPLUS_OTHER), OPECPLUS_OTHER, height=520) if g is not None else None
            _chart_panel("prod_group", "Additional OPEC+ member production", TEXT["opecplus_note"], fig)
        else:
            g = steo([*NON_OPEC_ORDER, "PAPR_NONOPECPLUS_XUS"], "annual")
            fig = None
            if g is not None:
                g = g.copy()
                g["OTHERS"] = g["PAPR_NONOPECPLUS_XUS"] - g[list(NON_OPEC_NAMED)].sum(axis=1)
                labels = {**NON_OPEC_NAMED, "PAPR_US": "United States", "OTHERS": "Others"}
                fig = stacked_bar(g, ["OTHERS", *NON_OPEC_ORDER], labels, height=520)
            _chart_panel("prod_group", "Non-OPEC production", TEXT["nonopec_note"], fig)
        return

    # monthly trends
    m = steo(list(MONTHLY), "monthly", "1998")
    if m is not None:
        m = m.dropna().copy()
        m.index = pd.to_datetime(m.index)
        total = m.sum(axis=1)
        share = m["COPR_OPECPLUS"] / total * 100
    left, right = st.columns(2, gap="medium")
    with left:
        _chart_panel("prod_lines", "Production by OPEC+, US and non-OPEC ex-US", TEXT["lines"],
                     lines_fig(m) if m is not None else None)
    with right:
        _chart_panel("prod_share", "OPEC+ market share", "Share of world petroleum and other liquids production.",
                     share_fig(share) if m is not None else None)
    _chart_panel("prod_area", "Production mix, 100% stacked", "Each group's share of the three-way total.",
                 area100_fig(m) if m is not None else None)
    with st.expander("About the OPEC+ market share chart"):
        st.markdown(TEXT["share"])
    if m is not None:
        out = m.rename(columns={"COPR_OPECPLUS": "OPEC+ Production", "COPRPUS": "US Production",
                                "COPR_NONOPECPLUS_XUS": "Non OPEC+ exUS Production"})
        out["OPEC+ Market Share (%)"] = share
        _download("Download data as CSV", out, "OilMonthlyProduction.csv", "dl_monthly")


# ---------------------------------------------------------------- tab: consumption
def consumption_tab():
    if not _key():
        return _need_key("cons")
    w = steo(list(CONSUMPTION), "annual")
    view = _seg("View", ["Components", "OECD vs non-OECD"], "fund_cons_view")
    fig = None
    if w is not None:
        w = w.copy()
        if view == "Components":
            fig = stacked_bar(w, list(CONSUMPTION), CONSUMPTION, height=520)
        else:
            w["OECD"], w["NONOECD"] = w[OECD].sum(axis=1), w[NON_OECD].sum(axis=1)
            fig = stacked_bar(w, ["OECD", "NONOECD"], {"OECD": "OECD", "NONOECD": "Non-OECD"}, height=520)
    _chart_panel("cons_main", "World petroleum and other liquids consumption",
                 "Annual consumption by region, in million barrels per day.", fig)
    with st.expander("About this chart"):
        st.markdown(TEXT["consumption"])
    if w is not None:
        csv = pd.DataFrame({"Year": w.index})
        for sid, name in CONSUMPTION.items():
            csv[f"{name} Petroleum Consumption"] = w[sid].values
        csv["Total OECD Petroleum Consumption"] = w[OECD].sum(axis=1).values
        csv["Total non-OECD Petroleum Consumption"] = w[NON_OECD].sum(axis=1).values
        csv["Total World Petroleum Consumption"] = csv["Total OECD Petroleum Consumption"] + csv["Total non-OECD Petroleum Consumption"]
        _download("Download data as CSV", csv.set_index("Year"), "OilAnnualConsumption.csv", "dl_cons")


# ---------------------------------------------------------------- tab: seasonality
def seasonality_tab():
    close = _safe(brent_close)
    left, right = st.columns(2, gap="medium")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    with left:
        _chart_panel("seas_m", "Month-on-month change", "Brent crude, percentage change by month since 2014.",
                     heatmap_fig(seasonality_table(close, "ME", "Month"), months) if close is not None else None,
                     "Source: Yahoo Finance (BZ=F)")
    with right:
        _chart_panel("seas_q", "Quarter-on-quarter change", "Brent crude, percentage change by quarter since 2014.",
                     heatmap_fig(seasonality_table(close, "QE", "Quarter"), ["Q1", "Q2", "Q3", "Q4"]) if close is not None else None,
                     "Source: Yahoo Finance (BZ=F)")
    with st.expander("How to read the heatmaps"):
        st.markdown(TEXT["seasonality"])


# ---------------------------------------------------------------- tab: EIA inventory
def _stock_card(label, df, stats):
    if df is None or len(df) < 2:
        return dict(label=label, value="\u2014", pill="Unavailable")
    last, prev = float(df["value"].iloc[-1]), float(df["value"].iloc[-2])
    chg = last - prev
    pct = chg / prev * 100 if prev else 0.0
    wk = stats["week"].iloc[-1]
    avg = stats.loc[stats["week"] == wk, "value"].mean()
    return dict(
        label=label, value=f"{last / 1000:,.1f}",
        pill=f"{_arrow(chg)} {abs(chg) / 1000:,.1f} mb ({pct:+.2f}%) w/w",
        pill_cls="flat" if chg == 0 else "up" if chg > 0 else "down",
        sub=f"Million barrels \u00B7 week ending {df['date'].iloc[-1]:%d %b %Y} \u00B7 5Y avg {avg / 1000:,.1f}",
    )


def inventory_tab():
    if not _key():
        return _need_key("inv")
    data = {sid: weekly(sid) for sid in STOCKS}
    stats = {sid: week_stats(d) if d is not None else None for sid, d in data.items()}

    names = {"WCESTUS1": "U.S. crude oil (ex-SPR)", "WGTSTUS1": "U.S. gasoline", "WDISTUS1": "U.S. distillate"}
    kpi_grid([_stock_card(names[sid], data[sid], stats[sid]) for sid in STOCKS], cols=3)
    st.markdown('<p class="gc-lead">Green marks an inventory build and red a draw. '
                + TEXT["inv_intro"].strip() + "</p>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([2, 1.6, 1.2])
    with c1:
        which = _seg("Product", [STOCKS[s][0] for s in STOCKS], "fund_inv_which")
    with c2:
        rng = _seg("Range", list(RANGE_DAYS), "fund_inv_range", "2Y")
    sid = next(s for s, v in STOCKS.items() if v[0] == which)
    d, s = data[sid], stats[sid]
    start = pd.Timestamp(datetime.now() - timedelta(days=RANGE_DAYS[rng]))

    left, right = st.columns(2, gap="medium")
    with left:
        _chart_panel("inv_wow", f"{which}: week-on-week change", "Weekly build (green) or draw (red), thousand barrels.",
                     wow_fig(d[d["date"] >= start - pd.Timedelta(days=7)], which) if d is not None else None)
    with right:
        _chart_panel("inv_rng", f"{which}: level vs 5-year range", "Actual stocks against the 5-year range and average for the same week.",
                     range_fig(s, start) if s is not None else None)
    with st.expander("About these charts"):
        st.markdown(TEXT["inv_wow"])
        st.markdown(TEXT["inv_hist"])

    frames = []
    for sid_, st_ in stats.items():
        if st_ is not None:
            f = st_.rename(columns={"date": "Date", "value": "Actual Values", "min5": "5-Year Min",
                                    "max5": "5-Year Max", "avg5": "5-Year Average"}).drop(columns=["week"])
            f["Series"] = STOCKS[sid_][1]
            frames.append(f)
    if frames:
        _download("Download data as CSV", pd.concat(frames, ignore_index=True), "CRUDE-EIA-Inventory.csv", "dl_inv")


# ---------------------------------------------------------------- tab: SPR
def spr_tab():
    if not _key():
        return _need_key("spr")
    d = weekly(SPR_SERIES)
    s = week_stats(d) if d is not None else None
    if s is not None and len(d) > 1:
        kpi_grid([_stock_card("U.S. Strategic Petroleum Reserve", d, s)], cols=3)

    c1, _ = st.columns([1.6, 3])
    with c1:
        rng = _seg("Range", ["1Y", "2Y", "5Y"], "fund_spr_range", "5Y")
    start = pd.Timestamp(datetime.now() - timedelta(days=RANGE_DAYS[rng]))
    _chart_panel("spr_main", "U.S. crude oil in the Strategic Petroleum Reserve",
                 "Actual stocks against the 5-year range for the same week, thousand barrels.",
                 range_fig(s, start, with_avg=False) if s is not None else None)
    with st.expander("About the Strategic Petroleum Reserve"):
        st.markdown(TEXT["spr"])


# ---------------------------------------------------------------- page
def fundamentals_page():
    hero("Fundamental Indicators",
         "Global supply and demand, production, seasonality and U.S. inventories.",
         "Sources<br>U.S. EIA, Yahoo Finance", slim=True)
    t1, t2, t3, t4, t5, t6 = st.tabs(["Balances", "Production", "Consumption", "Seasonality",
                                       "EIA Inventory", "EIA Inventory (SPR)"])
    with t1:
        balances_tab()
    with t2:
        production_tab()
    with t3:
        consumption_tab()
    with t4:
        seasonality_tab()
    with t5:
        inventory_tab()
    with t6:
        spr_tab()

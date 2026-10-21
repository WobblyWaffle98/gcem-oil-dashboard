from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from app_secrets import get_secret
from charts import layout, panel, show, unavailable
from others_copy import TEXT
from theme import COLORS, hero, kpi_grid, panel_head

GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
SOURCE = "Source: Caldara and Iacoviello, www.matteoiacoviello.com"
RANGES = {"1Y": 1, "3Y": 3, "5Y": 5, "10Y": 10, "Max": None}

EVENTS = {
    "War & attacks": ("#E5484D", [
        ("1990-08-02", "Iraq Invades Kuwait"), ("1991-01-17", "Start of Gulf War"), ("2001-09-11", "9/11 Attacks"),
        ("2003-03-20", "Iraq War Begins"), ("2008-08-08", "Russo-Georgian War"), ("2011-12-17", "Arab Spring"),
        ("2014-02-20", "Ukraine Crisis"), ("2015-11-13", "Paris Attacks"), ("2020-01-03", "Killing of Qasem Soleimani"),
        ("2022-02-24", "Russian Invasion of Ukraine"), ("2023-10-07", "Hamas-Israel Conflict Escalation"),
    ]),
    "Financial events": ("#2491CF", [
        ("2016-06-23", "Brexit Referendum"), ("2008-09-15", "Lehman Brothers Collapse (Global Financial Crisis)"),
    ]),
    "Other events": ("#F2A93B", [
        ("2002-11-01", "SARS Outbreak"), ("2010-01-12", "Haiti Earthquake"), ("2011-03-11", "Fukushima Nuclear Disaster"),
        ("2013-12-28", "Ebola Outbreak in West Africa"), ("2019-12-31", "COVID-19 Pandemic"),
    ]),
}


# ---------------------------------------------------------------- data
def _verify():
    insecure = get_secret("GPR_INSECURE_SSL") == "1"
    if insecure:
        requests.packages.urllib3.disable_warnings()
    return not insecure


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _gpr(verify):
    r = requests.get(GPR_URL, timeout=40, verify=verify)
    r.raise_for_status()
    df = pd.read_excel(BytesIO(r.content), engine="xlrd")
    df["date"] = pd.to_datetime(df["date"])
    d = df[["date", "GPRD"]].copy()
    d["GPRD_smoothed"] = d["GPRD"].rolling(window=7).mean()              # 7-day rolling average
    d["GPRD_1yr_rolling_avg"] = d["GPRD"].rolling(window=180).mean()     # 180-day (about 6 months); column name kept for CSV compatibility
    d["Difference"] = d["GPRD_smoothed"] - d["GPRD_1yr_rolling_avg"]
    return d.sort_values("date").reset_index(drop=True)


def gpr_data():
    try:
        return _gpr(_verify())
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _csv(df):
    return df.to_csv().encode("utf-8")


# ---------------------------------------------------------------- charts
def risk_fig(d, start, events_on):
    v = d[d["date"] >= start]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v["date"], y=v["GPRD_smoothed"], mode="lines", name="7-day rolling average",
                             line=dict(color=COLORS["brand"], width=2.2), hovertemplate="%{y:.1f}"))
    fig.add_trace(go.Scatter(x=v["date"], y=v["GPRD_1yr_rolling_avg"], mode="lines", name="6-month (180-day) rolling average",
                             line=dict(color=COLORS["blue"], width=1.8, dash="dash"), hovertemplate="%{y:.1f}"))
    if events_on:
        s = d.set_index("date")["GPRD_smoothed"].dropna()
        for name, (color, items) in EVENTS.items():
            pts = [(pd.Timestamp(day), label) for day, label in items if pd.Timestamp(day) >= start and pd.Timestamp(day) <= d["date"].max()]
            pts = [(day, label, s.asof(day)) for day, label in pts]
            pts = [p for p in pts if pd.notna(p[2])]
            if pts:
                fig.add_trace(go.Scatter(
                    x=[p[0] for p in pts], y=[p[2] for p in pts], mode="markers", name=name,
                    marker=dict(size=10, color=color, line=dict(width=1.5, color="#FFFFFF")),
                    text=[f"{p[0]:%d %b %Y}: {p[1]}" for p in pts], hoverinfo="text"))
    layout(fig, 430, hover="x unified")
    fig.update_yaxes(title_text="Index value")
    return fig


def gap_fig(d, start):
    v = d[d["date"] >= start]
    diff = v["Difference"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v["date"], y=diff.clip(lower=0), mode="lines", line=dict(width=0), fill="tozeroy",
                             fillcolor="rgba(229,72,77,0.30)", name="Above 6-month average", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=v["date"], y=diff.clip(upper=0), mode="lines", line=dict(width=0), fill="tozeroy",
                             fillcolor="rgba(0,169,157,0.30)", name="Below 6-month average", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=v["date"], y=diff, mode="lines", name="Difference", line=dict(color=COLORS["ink"], width=1.1),
                             hovertemplate="%{y:+.1f}", showlegend=False))
    layout(fig, 340)
    fig.update_yaxes(title_text="Difference", zeroline=True, zerolinecolor=COLORS["muted"], zerolinewidth=1)
    return fig


# ---------------------------------------------------------------- page
def others_page():
    hero("Geopolitical Risk Daily Index",
         "News-based measure of geopolitical risk, with a 7-day average against its 6-month baseline.",
         "Source<br>Caldara and Iacoviello", slim=True)

    d = gpr_data()
    if d is None:
        with panel("gpr_err"):
            unavailable("Geopolitical risk data unavailable",
                        "The data file could not be reached. Try again shortly. If your network inspects HTTPS traffic, "
                        "set <code>GPR_INSECURE_SSL=1</code> in your environment or secrets.")
        return

    valid = d.dropna(subset=["GPRD_smoothed"])
    last = d.dropna(subset=["Difference"]).iloc[-1]
    latest = d.iloc[-1]
    diff = float(last["Difference"])
    pct = float((valid["GPRD_smoothed"] <= last["GPRD_smoothed"]).mean() * 100)
    arrow = "\u25B2" if diff > 0 else "\u25BC" if diff < 0 else ""
    kpi_grid([
        dict(label="Latest daily value", value=f"{latest['GPRD']:.1f}", sub=f"GPRD \u00B7 {latest['date']:%d %b %Y}"),
        dict(label="7-day average", value=f"{last['GPRD_smoothed']:.1f}", pill=f"{arrow} {abs(diff):.1f} vs 6-month average",
             pill_cls="flat" if diff == 0 else "down" if diff > 0 else "up", sub="Above the baseline means elevated risk" if diff > 0 else "Below the baseline"),
        dict(label="6-month average", value=f"{last['GPRD_1yr_rolling_avg']:.1f}", sub="180-day rolling average"),
        dict(label="Percentile of history", value=f"{pct:.0f}%", sub=f"7-day average vs all days since {valid['date'].min():%Y}"),
    ], cols=4)

    c1, c2, _ = st.columns([1.6, 1.2, 2])
    with c1:
        rng = st.segmented_control("Range", list(RANGES), default="3Y", key="gpr_range", label_visibility="collapsed") or "3Y"
    with c2:
        events_on = st.toggle("Show events", value=True, key="gpr_events")
    years = RANGES[rng]
    start = d["date"].min() if years is None else d["date"].max() - pd.DateOffset(years=years)

    with panel("gpr_risk"):
        panel_head("Geopolitical risk index", "Daily index smoothed over 7 days, against its 180-day average. Markers show major events; hover for details.")
        show(risk_fig(d, start, events_on), "gpr_risk_chart")
        st.caption(SOURCE)

    with panel("gpr_gap"):
        panel_head("Gap to the 6-month average", "The 7-day average minus the 180-day average. Red is above the baseline, teal is below.")
        show(gap_fig(d, start), "gpr_gap_chart")
        st.caption(SOURCE)

    with st.expander("About the index"):
        st.markdown(TEXT["gpr"])

    st.download_button("Download data as CSV", _csv(d), file_name="GPR.csv", mime="text/csv", key="gpr_dl")

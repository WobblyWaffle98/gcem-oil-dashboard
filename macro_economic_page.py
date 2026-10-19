import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from bs4 import BeautifulSoup
from plotly.subplots import make_subplots

from macro_copy import TEXT
from theme import COLORS, COLORWAY, hero, kpi_grid, panel_head

FONT = "Geist, Inter, system-ui, sans-serif"

# ---------------------------------------------------------------- sources
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
HOPE_START = "2004-01-01"

TE_URL = "https://tradingeconomics.com/matrix?g=top"
TE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}
# Trading Economics column order -> display name
TE_COLUMNS = {
    "Country": "Country",
    "GDP": "GDP (USD Bil)",
    "GDP Growth": "GDP Annualized QoQ Growth (%)",
    "Interest Rate": "Interest Rate (%)",
    "Inflation Rate": "Inflation Rate (%)",
    "Jobless Rate": "Jobless Rate (%)",
    "Gov. Budget": "Gov. Budget (%)",
    "Debt/GDP": "Debt/GDP (%)",
    "Current Account": "Current Account (%)",
    "Population": "Population (mil)",
}
TE_NUMERIC = [c for c in TE_COLUMNS.values() if c != "Country"]
TE_FORMAT = {
    "GDP (USD Bil)": "{:,.0f}", "GDP Annualized QoQ Growth (%)": "{:,.2f}", "Interest Rate (%)": "{:,.2f}",
    "Inflation Rate (%)": "{:,.2f}", "Jobless Rate (%)": "{:,.2f}", "Gov. Budget (%)": "{:,.2f}",
    "Debt/GDP (%)": "{:,.2f}", "Current Account (%)": "{:,.2f}", "Population (mil)": "{:,.0f}",
}

GDP_URL = "https://api.db.nomics.world/v22/series/WB/WDI/A-NY.GDP.MKTP.CD-{code}?&observations=1"
GDP_COUNTRIES = {
    "United States": "USA", "China": "CHN", "Japan": "JPN", "Eurozone": "EMU",
    "India": "IND", "United Kingdom": "GBR", "Italy": "ITA", "Canada": "CAN",
}
PMI_URL = "https://api.db.nomics.world/v22/series/ISM/pmi?facets=1&format=json&limit=1000&observations=1"
NAHB_URL = "https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index"
NAHB_LABEL = "Chart: NAHB/Wells Fargo HMI and Single-Family Housing Starts"

# Shorter column headers so all nine indicators fit without sideways scrolling
TE_LABELS = {
    "GDP (USD Bil)": st.column_config.Column("GDP (USD bn)"),
    "GDP Annualized QoQ Growth (%)": st.column_config.Column("GDP growth (%)", help="Annualized quarter-on-quarter"),
    "Interest Rate (%)": st.column_config.Column("Interest rate (%)"),
    "Inflation Rate (%)": st.column_config.Column("Inflation (%)"),
    "Jobless Rate (%)": st.column_config.Column("Jobless (%)"),
    "Gov. Budget (%)": st.column_config.Column("Budget (%)", help="Government budget balance, % of GDP"),
    "Debt/GDP (%)": st.column_config.Column("Debt/GDP (%)"),
    "Current Account (%)": st.column_config.Column("Current acct (%)", help="Current account balance, % of GDP"),
    "Population (mil)": st.column_config.Column("Population (mn)"),
}

RECESSIONS = [("2007-12-01", "2009-06-30"), ("2020-02-01", "2020-11-30")]
RANGES = {"Max": None, "15Y": 15, "10Y": 10, "5Y": 5, "3Y": 3}


# ---------------------------------------------------------------- data (each raises on failure; wrappers below catch)
def _fred_key():
    """FRED key from the environment, or from Streamlit secrets (FRED_API_KEY or [fred] api_key)."""
    if os.environ.get("FRED_API_KEY"):
        return os.environ["FRED_API_KEY"]
    paths = [os.path.expanduser("~/.streamlit/secrets.toml"), os.path.join(os.getcwd(), ".streamlit", "secrets.toml")]
    if not any(os.path.exists(p) for p in paths):
        return None  # touching st.secrets with no file would render an error banner
    try:
        s = st.secrets
        if "FRED_API_KEY" in s:
            return s["FRED_API_KEY"]
        if "fred" in s and "api_key" in s["fred"]:
            return s["fred"]["api_key"]
    except Exception:
        pass
    return None


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _fred(series_id, start, key):
    r = requests.get(
        FRED_URL,
        params={"series_id": series_id, "api_key": key, "file_type": "json", "observation_start": start},
        timeout=25,
    )
    r.raise_for_status()
    df = pd.DataFrame(r.json()["observations"])[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna(subset=["value"]).reset_index(drop=True)


def get_fred(series_id, start=HOPE_START):
    key = _fred_key()
    if not key:
        return None
    try:
        return _fred(series_id, start, key)
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def trading_economics():
    r = requests.get(TE_URL, headers=TE_HEADERS, timeout=25)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    rows = []
    for tr in soup.select("tr"):
        cells = tr.find_all("td")
        if len(cells) >= len(TE_COLUMNS):
            rows.append([c.get_text(strip=True) for c in cells[: len(TE_COLUMNS)]])
    if not rows:
        raise ValueError("No rows found")
    df = pd.DataFrame(rows, columns=list(TE_COLUMNS)).rename(columns=TE_COLUMNS)
    for col in TE_NUMERIC:
        df[col] = pd.to_numeric(df[col].str.replace(",", "").str.replace("%", "").str.strip(), errors="coerce")
    return df


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def gdp_series():
    def one(country, code):
        r = requests.get(GDP_URL.format(code=code), timeout=25)
        r.raise_for_status()
        docs = r.json().get("series", {}).get("docs", [])
        if not docs:
            return []
        doc = docs[0]
        out = []
        for year, value in zip(doc.get("period", []), doc.get("value", [])):
            v = pd.to_numeric(value, errors="coerce")
            if pd.notna(v) and int(year) >= 2000:
                out.append((country, int(year), float(v)))
        return out

    rows = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(one, c, code) for c, code in GDP_COUNTRIES.items()]
        for f in as_completed(futures):
            try:
                rows += f.result()
            except Exception:
                pass
    if not rows:
        raise ValueError("No GDP data")
    return pd.DataFrame(rows, columns=["Country", "Year", "GDP"]).sort_values(["Country", "Year"])


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def ism_pmi():
    r = requests.get(PMI_URL, timeout=25)
    r.raise_for_status()
    doc = r.json().get("series", {}).get("docs", [])[0]
    df = pd.DataFrame({"date": doc["period"], "PMI": doc["value"]})
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m")
    df["PMI"] = pd.to_numeric(df["PMI"], errors="coerce")
    return df.dropna().reset_index(drop=True)


@st.cache_data(ttl=12 * 3600, show_spinner=False)
def nahb():
    page = requests.get(NAHB_URL, timeout=25)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")
    li = soup.find("li", string=NAHB_LABEL)
    a = li.find("a", href=True) if li else None
    if not a:
        raise ValueError("NAHB download link not found")
    url = a["href"] if a["href"].startswith("http") else "https://www.nahb.org" + a["href"]
    f = requests.get(url, timeout=40)
    f.raise_for_status()
    df = pd.read_excel(BytesIO(f.content))
    start = pd.to_datetime(df["Unnamed: 0"].iloc[0])
    try:
        dates = pd.date_range(start=start, periods=len(df), freq="ME")
    except ValueError:  # older pandas
        dates = pd.date_range(start=start, periods=len(df), freq="M")
    df["date"] = dates
    df = df.drop(columns=["Unnamed: 0"])
    return df[df["date"] >= HOPE_START].reset_index(drop=True)


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception:
        return None


def growth_frame(df, periods):
    """Percent change plus the +/- 2 standard deviation band used in the original charts."""
    d = df.copy()
    d["value"] = d["value"].round(2)
    d["pct"] = d["value"].pct_change(periods=periods) * 100
    sd = d["pct"].std()
    d["upper"], d["lower"] = d["pct"] + 2 * sd, d["pct"] - 2 * sd
    return d


# ---------------------------------------------------------------- charts
def _layout(fig, height=400, legend=True):
    fig.update_layout(
        height=height, margin=dict(l=22, r=22, t=46 if legend else 14, b=14),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=COLORS["surface"],
        font=dict(family=FONT, color=COLORS["muted"], size=12), colorway=COLORWAY,
        hovermode="x unified", showlegend=legend,
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=COLORS["rule"], font=dict(color=COLORS["ink"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, showline=True, linecolor=COLORS["rule"], automargin=True),
        yaxis=dict(gridcolor=COLORS["rule"], zeroline=False, automargin=True),
    )
    return fig


def _shade(fig, start):
    """Shade US recessions and add a legend entry for them."""
    s = pd.Timestamp(start)
    for a, b in RECESSIONS:
        if pd.Timestamp(b) > s:
            fig.add_vrect(x0=max(pd.Timestamp(a), s), x1=b, fillcolor="rgba(229,72,77,0.12)", line_width=0, layer="below")
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="US recession",
                             marker=dict(size=10, symbol="square", color="rgba(229,72,77,0.30)")))


def growth_fig(d, name, start):
    v = d[d["date"] >= start]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v["date"], y=v["upper"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=v["date"], y=v["lower"], mode="lines", fill="tonexty", fillcolor="rgba(94,119,118,0.16)",
                             line=dict(width=0), name="2 std dev interval", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=v["date"], y=v["pct"], mode="lines", name=name,
                             line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:.2f}%"))
    fig.add_hline(y=0, line=dict(color=COLORS["muted"], width=1, dash="dash"))
    _shade(fig, start)
    _layout(fig)
    fig.update_yaxes(ticksuffix="%")
    return fig


def nahb_fig(df, start):
    v = df[df["date"] >= start]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=v["date"], y=v["Housing Market Index"], mode="lines", name="Housing Market Index",
                             line=dict(color=COLORS["brand"], width=2.4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=v["date"], y=v["Single-Family Starts"], mode="lines", name="Single-family starts (thousands)",
                             line=dict(color=COLORS["blue"], width=2)), secondary_y=True)
    fig.add_trace(go.Scatter(x=[v["date"].min(), v["date"].max()], y=[50, 50], mode="lines", showlegend=False,
                             hoverinfo="skip", line=dict(color=COLORS["muted"], width=1, dash="dash")), secondary_y=False)
    _shade(fig, start)
    _layout(fig)
    fig.update_yaxes(title_text="HMI", secondary_y=False)
    fig.update_yaxes(title_text="Starts (thousands)", secondary_y=True, showgrid=False)
    return fig


def pmi_fig(df, start):
    v = df[df["date"] >= start]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v["date"], y=v["PMI"], mode="lines", name="ISM PMI",
                             line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:.1f}"))
    fig.add_trace(go.Scatter(x=[v["date"].min(), v["date"].max()], y=[50, 50], mode="lines", name="50 = expansion line",
                             hoverinfo="skip", line=dict(color=COLORS["muted"], width=1, dash="dash")))
    _shade(fig, start)
    return _layout(fig)


def line_fig(df, col, name, start, suffix=""):
    v = df[df["date"] >= start]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v["date"], y=v[col], mode="lines", name=name,
                             line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:.1f}" + suffix))
    _shade(fig, start)
    _layout(fig)
    fig.update_yaxes(ticksuffix=suffix)
    return fig


def sahm_fig(sahm, rec):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=rec["date"], y=rec["value"], mode="lines", name="US recession (NBER)", line=dict(width=0),
                             fill="tozeroy", fillcolor="rgba(229,72,77,0.18)", hoverinfo="skip"), secondary_y=True)
    fig.add_trace(go.Scatter(x=sahm["date"], y=sahm["value"], mode="lines", name="Real-time Sahm indicator",
                             line=dict(color=COLORS["brand"], width=2.4), hovertemplate="%{y:.2f} pts"), secondary_y=False)
    fig.add_trace(go.Scatter(x=[sahm["date"].min(), sahm["date"].max()], y=[0.5, 0.5], mode="lines", name="0.50 threshold",
                             hoverinfo="skip", line=dict(color=COLORS["down"], width=1.6, dash="dash")), secondary_y=False)
    _layout(fig, height=440)
    fig.update_yaxes(title_text="Percentage points", secondary_y=False)
    fig.update_yaxes(range=[0, 1], showgrid=False, showticklabels=False, secondary_y=True)
    return fig


def show(fig, key):
    st.plotly_chart(fig, use_container_width=True, theme=None, key=key, config={"displayModeBar": False})


def unavailable(title, detail):
    st.markdown(f'<div class="gc-state"><b>{title}</b>{detail}</div>', unsafe_allow_html=True)


def panel(key):
    return st.container(key=f"panel_{key}")


def _key_missing():
    unavailable(
        "FRED API key not set",
        "Add <code>FRED_API_KEY</code> to your Streamlit secrets (or environment) to load the US series.",
    )


# ---------------------------------------------------------------- tab 1: global data
def _hl(s, n=3):
    top, bottom = s.nlargest(n).index, s.nsmallest(n).index
    return ["background-color:#CDEDE9" if i in top else "background-color:#FBDAD8" if i in bottom else "" for i in s.index]


def global_tab():
    df = _safe(trading_economics)

    if df is not None:
        c1, _ = st.columns([1, 3])
        with c1:
            countries = df["Country"].tolist()
            default = countries.index("United States") if "United States" in countries else 0
            who = st.selectbox("Country", countries, index=default, key="macro_country", label_visibility="collapsed")
        row = df[df["Country"] == who].iloc[0]

        def card(label, col, suffix="%"):
            v, med = row[col], df[col].median()
            val = "\u2014" if pd.isna(v) else f"{v:,.2f}{suffix}"
            sub = f"Median of {len(df)} countries: {med:,.2f}{suffix}" if pd.notna(med) else ""
            return dict(label=label, value=val, sub=sub)

        kpi_grid([
            card("GDP growth (annualized QoQ)", "GDP Annualized QoQ Growth (%)"),
            card("Interest rate", "Interest Rate (%)"),
            card("Inflation rate", "Inflation Rate (%)"),
            card("Jobless rate", "Jobless Rate (%)"),
            card("Debt / GDP", "Debt/GDP (%)"),
        ], cols=5)

        with panel("snapshot"):
            panel_head("Economic indicators snapshot", "Key indicators by country. Use the toggle to mark the three highest and three lowest values in each column.")
            hl = st.toggle("Highlight top and bottom three", key="macro_hl")
            styler = df.style.apply(_hl, subset=TE_NUMERIC, axis=0) if hl else df.style
            st.dataframe(styler.format(TE_FORMAT), hide_index=True, use_container_width=True,
                         height=min(36 * (len(df) + 1) + 20, 640), column_config=TE_LABELS)
            st.caption("Source: World Bank, US Federal Reserve, central banks, Trading Economics")
            with st.expander("About these indicators"):
                st.markdown(TEXT["indicators"])
    else:
        with panel("snapshot"):
            panel_head("Economic indicators snapshot")
            unavailable("Country table unavailable", "Trading Economics could not be reached. Try again shortly.")

    left, right = st.columns(2, gap="medium")

    with left:
        with panel("bubble"):
            panel_head("GDP, growth and population", TEXT["bubble"])
            if df is None:
                unavailable("Unavailable", "This chart uses the country table above.")
            else:
                b = df.dropna(subset=["GDP (USD Bil)", "GDP Annualized QoQ Growth (%)", "Population (mil)"])
                fig = px.scatter(b, x="GDP Annualized QoQ Growth (%)", y="GDP (USD Bil)", size="Population (mil)",
                                 color="Country", text="Country", size_max=52, color_discrete_sequence=COLORWAY,
                                 labels={"GDP (USD Bil)": "GDP (USD billion)", "GDP Annualized QoQ Growth (%)": "GDP growth (%)",
                                         "Population (mil)": "Population (million)"})
                fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FFFFFF")),
                                  textposition="top center", textfont=dict(size=11, color=COLORS["ink"]))
                _layout(fig, height=470, legend=False)
                fig.update_layout(hovermode="closest", margin=dict(l=22, r=22, t=14, b=14))
                fig.update_xaxes(showgrid=True, gridcolor=COLORS["rule"], ticksuffix="%")
                show(fig, "macro_bubble")
            st.caption("Source: World Bank")

    with right:
        with panel("gdp"):
            panel_head("GDP of major economies", "Annual GDP in current US dollars, 2000 onwards. Click a legend entry to hide or show a country.")
            g = _safe(gdp_series)
            if g is None:
                unavailable("GDP series unavailable", "DBnomics could not be reached. Try again shortly.")
            else:
                fig = px.line(g, x="Year", y="GDP", color="Country", color_discrete_sequence=COLORWAY,
                              labels={"GDP": "GDP (current US$)"})
                fig.update_traces(line=dict(width=2.2))
                _layout(fig, height=470)
                fig.update_layout(hovermode="x unified", legend=dict(title=None, orientation="h", yanchor="top", y=-0.18))
                fig.update_layout(margin=dict(l=22, r=22, t=14, b=14))
                fig.update_yaxes(tickformat="$.2s")
                show(fig, "macro_gdp")
            st.caption("Source: World Bank")


# ---------------------------------------------------------------- tab 2: HOPE
def _arrow(delta):
    return "\u25B2" if delta > 0 else "\u25BC" if delta < 0 else ""


def _step_card(step, label, d, col, sub, level=False, adverse_up=False):
    if d is None or d[col].dropna().shape[0] < 2:
        return dict(step=step, label=label, value="\u2014", pill="Unavailable", sub=sub)
    s = d.dropna(subset=[col])
    v, p, dt = float(s[col].iloc[-1]), float(s[col].iloc[-2]), s["date"].iloc[-1]
    delta = v - p
    flat = abs(delta) < 0.05
    cls = "flat" if flat else ("down" if (delta > 0) == adverse_up else "up")
    return dict(
        step=step, label=label,
        value=f"{v:.1f}%" if level else f"{v:+.1f}%",
        pill=("No change" if flat else f"{_arrow(delta)} {abs(delta):.1f} pt vs prior"), pill_cls=cls,
        sub=f"{sub} \u00B7 {dt:%b %Y}",
    )


def hope_tab():
    st.markdown(
        '<p class="gc-lead">The HOPE model tracks the order in which US activity weakens during a tightening cycle: '
        "<b>H</b>ousing, new <b>O</b>rders, corporate <b>P</b>rofits, then <b>E</b>mployment.</p>",
        unsafe_allow_html=True,
    )
    with st.expander("About the HOPE model"):
        st.markdown(TEXT["hope_intro"])

    if not _fred_key():
        with panel("hope_nokey"):
            _key_missing()
        return

    cs, orders, cp, un = (get_fred(s) for s in ("CSUSHPINSA", "AMTMNO", "CP", "UNRATE"))
    cs_d = growth_frame(cs, 12) if cs is not None else None
    or_d = growth_frame(orders, 12) if orders is not None else None
    cp_d = growth_frame(cp, 1) if cp is not None else None
    un_d = None
    if un is not None:
        un_d = un.copy()
        un_d["value"] = un_d["value"].round(2)

    kpi_grid([
        _step_card("1", "Housing", cs_d, "pct", "Case-Shiller, YoY"),
        _step_card("2", "Orders", or_d, "pct", "Mfg new orders, YoY"),
        _step_card("3", "Profits", cp_d, "pct", "After-tax profits, QoQ"),
        _step_card("4", "Employment", un_d, "value", "Unemployment rate", level=True, adverse_up=True),
    ], cols=4)

    c1, c2, _ = st.columns([1.5, 1.3, 1.2])
    with c1:
        view = st.segmented_control("Component", ["Housing", "Orders", "Profits", "Employment"], default="Housing",
                                    key="hope_view", label_visibility="collapsed") or "Housing"
    with c2:
        rng = st.segmented_control("Range", list(RANGES), default="Max", key="hope_range",
                                   label_visibility="collapsed") or "Max"
    years = RANGES[rng]
    start = pd.Timestamp(HOPE_START) if years is None else max(pd.Timestamp(HOPE_START), pd.Timestamp(datetime.now() - timedelta(days=365 * years)))

    blurb = {
        "Housing": "Interest-rate sensitive, so it tends to turn first.",
        "Orders": "Forward demand for manufactured goods; the next to roll over after housing.",
        "Profits": "After-tax corporate profits, the third signal in the sequence.",
        "Employment": "Usually the last to weaken, sometimes only after a recession has begun.",
    }
    with panel(f"hope_about_{view.lower()}"):
        panel_head(view, blurb[view])
        with st.expander("Read more"):
            st.markdown(TEXT[view.lower()])

    def chart_panel(key, title, note, fig, source):
        with panel(key):
            panel_head(title, note)
            if fig is None:
                unavailable("Data unavailable", "The source could not be reached. Try again shortly.")
            else:
                show(fig, key)
            st.caption(source)

    fed = "Source: US Federal Reserve (FRED)"
    a, b = st.columns(2, gap="medium")
    if view == "Housing":
        with a:
            chart_panel("cs", "Case-Shiller Home Price Index", "Percent change from a year earlier.",
                        growth_fig(cs_d, "Case-Shiller YoY", start) if cs_d is not None else None, fed)
        with b:
            nh = _safe(nahb)
            chart_panel("nahb", "Housing Market Index and single-family starts", "Builder sentiment (above 50 is favourable) against new construction.",
                        nahb_fig(nh, start) if nh is not None else None, "Source: US National Association of Home Builders")
    elif view == "Orders":
        with a:
            chart_panel("orders", "Manufacturers' new orders", "Total manufacturing, percent change from a year earlier.",
                        growth_fig(or_d, "New orders YoY", start) if or_d is not None else None, fed)
        with b:
            pm = _safe(ism_pmi)
            chart_panel("pmi", "ISM manufacturing PMI", "A reading above 50 signals expansion.",
                        pmi_fig(pm, start) if pm is not None else None, "Source: Institute for Supply Management")
    elif view == "Profits":
        chart_panel("profits", "Corporate profits after tax", "Without IVA and CCAdj, percent change from the previous data point.",
                    growth_fig(cp_d, "Profits QoQ", start) if cp_d is not None else None, fed)
    else:
        chart_panel("unrate", "Unemployment rate", "US civilian unemployment rate.",
                    line_fig(un_d, "value", "Unemployment rate", start, "%") if un_d is not None else None, fed)


# ---------------------------------------------------------------- tab 3: recession
def recession_tab():
    if not _fred_key():
        with panel("rec_nokey"):
            _key_missing()
        return

    sahm = get_fred("SAHMREALTIME", "2000-01-01")
    rec = get_fred("USRECD", "2000-01-01")

    if sahm is not None and not sahm.empty:
        v, dt = float(sahm["value"].iloc[-1]), sahm["date"].iloc[-1]
        trig = v >= 0.5
        cards = [
            dict(label="Sahm indicator", value=f"{v:.2f}", sub=f"Percentage points \u00B7 {dt:%b %Y}",
                 pill="At or above threshold" if trig else "Below threshold", pill_cls="down" if trig else "up"),
            dict(label="Distance to 0.50 trigger", value=f"{abs(0.5 - v):.2f}",
                 sub="Points above the trigger" if trig else "Points below the trigger"),
        ]
        if rec is not None and not rec.empty:
            flag = int(rec["value"].iloc[-1]) == 1
            cards.append(dict(label="NBER recession flag", value="Yes" if flag else "No",
                              sub=f"Latest observation \u00B7 {rec['date'].iloc[-1]:%d %b %Y}"))
        kpi_grid(cards, cols=len(cards))

    with panel("sahm"):
        panel_head("Real-time Sahm rule recession indicator", "")
        st.markdown(TEXT["sahm"])
        if sahm is None or rec is None or sahm.empty:
            unavailable("Data unavailable", "FRED could not be reached. Try again shortly.")
        else:
            show(sahm_fig(sahm, rec), "sahm")
        st.caption("Source: US Federal Reserve (FRED)")


# ---------------------------------------------------------------- page
def macro_economic_page():
    hero("Macro-economic Indicators",
         "A global snapshot, the HOPE leading-indicator sequence and recession risk.",
         "Sources<br>FRED, World Bank, Trading Economics, NAHB, ISM", slim=True)

    t1, t2, t3 = st.tabs(["Global data", "HOPE analysis", "Recession"])
    with t1:
        global_tab()
    with t2:
        hope_tab()
    with t3:
        recession_tab()

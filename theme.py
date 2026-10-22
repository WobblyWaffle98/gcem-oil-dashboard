"""Shared look and feel: PETRONAS-inspired colour tokens, CSS, and the dashboard section list."""
from string import Template

import streamlit as st

# Brand teal is sampled from the GCEM logo (#00A99D), in the PETRONAS emerald family.
# Change a value here and the whole app follows.
COLORS = {
    "bg": "#F3F7F7",
    "surface": "#FFFFFF",
    "ink": "#10302F",
    "muted": "#5E7776",
    "rule": "#E2EBEA",
    "brand": "#00A99D",       # fills, lines, selected borders
    "brand_dark": "#007A72",  # text and links on white (readable contrast)
    "brand_tint": "#E6F6F4",
    "deep": "#00403D",        # hero and strong accents
    "blue": "#2491CF",        # secondary series
    "up": "#1F9D55",
    "down": "#E5484D",
}

# Multi-series chart colours, brand teal first
COLORWAY = ["#00A99D", "#00403D", "#2491CF", "#F2A93B", "#7A5AF8", "#E5484D", "#6C8A89", "#9BD3CC"]

# Longer palette for stacked charts with many series (teal family first, then distinct hues)
PALETTE_LONG = ["#00A99D", "#00403D", "#2491CF", "#F2A93B", "#7A5AF8", "#E5484D", "#6C8A89", "#9BD3CC",
                "#0B4F8A", "#C026D3", "#84CC16", "#B45309", "#F472B6", "#94A3B8", "#06B6D4", "#5B6B1F"]

# Sidebar names (exact radio labels): blurb shown on the Main page, and an icon path set (24x24, stroked).
SECTIONS = {
    "Macro-economic": (
        "Global indicators, GDP, and the HOPE recession model.",
        '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c3 3.2 3 14.8 0 18"/><path d="M12 3c-3 3.2-3 14.8 0 18"/>',
    ),
    "Fundamentals": (
        "EIA supply-demand balances, production, consumption and inventories.",
        '<path d="M5 20V11"/><path d="M12 20V4"/><path d="M19 20v-7"/>',
    ),
    "Financial Markets": (
        "Equities, Treasury yields and FX, with correlations to Brent.",
        '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    ),
    "Technical and Probability Analysis": (
        "Technical views and Monte Carlo price paths for Brent.",
        '<path d="M3 19c3 0 4-14 9-14s6 14 9 14"/><path d="M3 19h18"/>',
    ),
    "Others": (
        "Geopolitical risk index.",
        '<path d="M12 3l9.5 16.5h-19z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
    ),
}

_CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap');

:root{
  --bg:${bg}; --surface:${surface}; --ink:${ink}; --muted:${muted}; --rule:${rule};
  --brand:${brand}; --brand-dark:${brand_dark}; --tint:${brand_tint}; --deep:${deep};
  --up:${up}; --down:${down};
  --shadow:0 1px 2px rgba(16,48,47,.05), 0 8px 24px rgba(16,48,47,.05);
}

/* Base */
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background:var(--bg); color:var(--ink);
  font-family:'Geist','Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
}
[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer, [data-testid="stDeployButton"], [data-testid="stAppDeployButton"], .stDeployButton{ display:none !important; }
.block-container{ padding-top:2rem; padding-bottom:4rem; max-width:1500px; }
h1,h2,h3,h4{ font-family:'Geist','Inter',system-ui,sans-serif; font-weight:600; letter-spacing:-0.02em; color:var(--ink); }
a{ color:var(--brand-dark); }
hr{ border-color:var(--rule); }
[data-testid="stCaptionContainer"], .stCaption{ color:var(--muted); }

/* Sidebar */
[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--rule); }
[data-testid="stSidebar"] h1{ font-size:0.8rem; font-weight:500; color:var(--muted); letter-spacing:0.01em; margin-top:0.5rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] > label{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]{ gap:2px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  padding:9px 12px; border-radius:10px; border-left:3px solid transparent; cursor:pointer; width:100%;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{ background:var(--bg); }
[data-testid="stSidebar"] [data-testid="stRadio"] label p{ color:var(--muted); font-size:0.95rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){ background:var(--tint); border-left-color:var(--brand); }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p{ color:var(--brand-dark); font-weight:600; }

/* Buttons and controls */
.stButton > button{
  background:var(--surface); border:1px solid var(--rule); color:var(--ink); border-radius:10px; font-weight:500;
}
.stButton > button:hover{ border-color:var(--brand); color:var(--brand-dark); background:var(--surface); }
.stButton > button:focus-visible{ outline:2px solid var(--brand); outline-offset:2px; }
[data-testid="stButtonGroup"]{ flex-wrap:nowrap; }
button[data-testid="stBaseButton-segmented_control"], button[data-testid="stBaseButton-segmented_controlActive"]{ padding:0.25rem 0.7rem; white-space:nowrap; }
button[data-testid="stBaseButton-segmented_control"]{
  background:var(--surface); border:1px solid var(--rule); color:var(--muted); font-weight:500;
}
button[data-testid="stBaseButton-segmented_control"]:hover{ color:var(--brand-dark); border-color:var(--brand); }
button[data-testid="stBaseButton-segmented_controlActive"]{
  background:var(--tint); border:1px solid var(--brand); color:var(--brand-dark); font-weight:600;
}

/* Hero */
.gc-hero{
  position:relative; overflow:hidden; color:#fff; border-radius:18px; padding:26px 30px;
  display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; margin-bottom:18px;
  background:linear-gradient(115deg, var(--deep) 0%, #006660 55%, #00968B 100%);
}
.gc-hero::before{
  content:""; position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(circle at 94% -30%, rgba(255,255,255,.16) 0 130px, transparent 131px),
    radial-gradient(circle at 82% 140%, rgba(255,255,255,.09) 0 100px, transparent 101px);
}
.gc-hero > *{ position:relative; }
.gc-hero-t{ font-size:2rem; font-weight:600; letter-spacing:-0.03em; line-height:1.1; }
.gc-hero-s{ margin-top:6px; color:rgba(255,255,255,.78); font-size:0.95rem; max-width:60ch; }
.gc-hero-m{ text-align:right; color:rgba(255,255,255,.78); font-size:0.85rem; line-height:1.5; font-variant-numeric:tabular-nums; }
.gc-hero-m b{ color:#fff; font-weight:600; font-size:1rem; }

/* Quote cards */
.gc-grid{ display:grid; grid-template-columns:repeat(6, minmax(0,1fr)); gap:14px; margin-bottom:18px; }
.gc-q{ background:var(--surface); border:1px solid var(--rule); border-radius:16px; padding:16px 18px 14px;
  box-shadow:var(--shadow); display:flex; flex-direction:column; gap:8px; min-width:0; }
.gc-q-name{ color:var(--muted); font-size:0.85rem; font-weight:500; }
.gc-q-price{ font-size:1.65rem; font-weight:600; letter-spacing:-0.03em; font-variant-numeric:tabular-nums; line-height:1.1; }
.gc-q-row{ display:flex; justify-content:space-between; align-items:flex-end; gap:8px; }
.gc-pill{ display:inline-block; font-size:0.78rem; font-weight:600; font-variant-numeric:tabular-nums; padding:3px 8px; border-radius:999px; white-space:nowrap; }
.gc-pill.up{ color:#14773F; background:rgba(31,157,85,.12); }
.gc-pill.down{ color:#C3282D; background:rgba(229,72,77,.12); }
.gc-pill.flat{ color:var(--muted); background:var(--bg); }
.gc-q svg{ display:block; flex:1 1 40px; min-width:40px; max-width:96px; height:30px; }
@media (max-width:1280px){ .gc-grid{ grid-template-columns:repeat(3, minmax(0,1fr)); } }
@media (max-width:640px){ .gc-grid{ grid-template-columns:repeat(2, minmax(0,1fr)); } .gc-hero-t{ font-size:1.5rem; } .gc-hero-m{ text-align:left; } }

/* Panels (st.container(key=...)) */
.st-key-chart_card, .st-key-cal_card, [class*="st-key-panel_"]{
  background:var(--surface); border:1px solid var(--rule); border-radius:16px; padding:20px 0 12px;
  box-shadow:var(--shadow); overflow:hidden;
}
/* Text and controls get side padding; the chart and calendar run edge to edge so they size to the card exactly */
.st-key-chart_card > [data-testid="stElementContainer"], .st-key-cal_card > [data-testid="stElementContainer"],
[class*="st-key-panel_"] > [data-testid="stElementContainer"],
.st-key-chart_card > [data-testid="stHorizontalBlock"], [class*="st-key-panel_"] > [data-testid="stHorizontalBlock"]{ box-sizing:border-box; padding:0 22px; }
.st-key-chart_card > [data-testid="stElementContainer"]:has(.stPlotlyChart, [data-testid="stPlotlyChart"], .js-plotly-plot),
[class*="st-key-panel_"] > [data-testid="stElementContainer"]:has(.stPlotlyChart, [data-testid="stPlotlyChart"], .js-plotly-plot),
[class*="st-key-panel_"] > [data-testid="stElementContainer"]:has([data-testid="stDataFrame"]),
.st-key-cal_card > [data-testid="stElementContainer"]:has(iframe){ padding:0; }
.gc-h{ font-size:1.15rem; font-weight:600; letter-spacing:-0.02em; margin:0 0 2px; }
.gc-note{ color:var(--muted); font-size:0.86rem; margin:0 0 12px; max-width:64ch; }

/* Streamlit sizes children to the card's outer width; make them fit the padded inner width */
.st-key-chart_card > div, .st-key-cal_card > div, [class*="st-key-sec_"] > div, [class*="st-key-panel_"] > div{ width:100% !important; max-width:100% !important; min-width:0; }
.st-key-chart_card, .st-key-cal_card, [class*="st-key-sec_"], [class*="st-key-panel_"]{ box-sizing:border-box; min-width:0; }
.st-key-cal_card iframe{ width:100% !important; }
/* Streamlit also pins inner markdown/button wrappers to the card's outer width; let them follow the padded box */
.st-key-chart_card [data-testid="stMarkdown"], .st-key-cal_card [data-testid="stMarkdown"], [class*="st-key-panel_"] [data-testid="stMarkdown"],
[class*="st-key-sec_"] [data-testid="stMarkdown"], [class*="st-key-sec_"] .stButton{ width:100% !important; }

[class*="st-key-panel_"] [data-testid="stMultiSelect"], [class*="st-key-panel_"] [data-testid="stSelectbox"],
[class*="st-key-panel_"] .stToggle, [class*="st-key-panel_"] [data-testid="stCaptionContainer"], [class*="st-key-panel_"] .stDownloadButton{ width:100% !important; }
[class*="st-key-panel_"] [data-testid="stExpander"]{ box-sizing:border-box; margin:0 22px; width:calc(100% - 44px) !important; }

/* Widgets stay light with dark text, even if the browser or Streamlit asks for dark */
:root, .stApp{ color-scheme:light; }
[data-baseweb="select"] *, [data-baseweb="input"] *, [data-baseweb="textarea"] *{ color:var(--ink); }
[data-baseweb="select"] svg{ fill:var(--muted); }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul[role="listbox"]{ background:var(--surface); }
[data-baseweb="popover"] li, [data-baseweb="popover"] [role="option"]{ color:var(--ink); background:var(--surface); }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] [role="option"]:hover, [data-baseweb="popover"] [aria-selected="true"]{ background:var(--tint); color:var(--brand-dark); }
[data-baseweb="tag"]{ background:var(--brand); }
[data-baseweb="tag"] *{ color:#FFFFFF; }
[data-testid="stToggle"] label, [data-testid="stToggle"] p, [data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p{ color:var(--ink); }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p{ color:var(--ink); }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p{ color:var(--ink); }

/* Side-by-side panels stretch to the same height: every wrapper between the column and the panel fills its parent */
[data-testid="stColumn"] div:has([class*="st-key-panel_"]){ height:100%; }
[class*="st-key-panel_"]{ height:100%; }

/* Section cards */
[class*="st-key-sec_"]{
  background:var(--surface); border:1px solid var(--rule); border-radius:16px; padding:18px 0 10px;
  box-shadow:var(--shadow); gap:0.4rem; transition:border-color .15s; height:100%; min-height:236px;
}
[class*="st-key-sec_"] > [data-testid="stElementContainer"]{ box-sizing:border-box; padding:0 18px; }
[class*="st-key-sec_"]:hover{ border-color:var(--brand); }
.gc-ic{ width:40px; height:40px; border-radius:12px; background:var(--tint); color:var(--brand-dark);
  display:flex; align-items:center; justify-content:center; margin-bottom:12px; }
.gc-ic svg{ width:22px; height:22px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
.gc-card-t{ font-size:1.02rem; font-weight:600; letter-spacing:-0.015em; line-height:1.25; margin-bottom:6px; min-height:2.5em; }
.gc-card-d{ color:var(--muted); font-size:0.86rem; line-height:1.45; min-height:5.9em; }
[class*="st-key-open_"] button{ border:none; background:transparent; padding:6px 0; color:var(--brand-dark); justify-content:flex-start; min-height:0; font-weight:600; }
[class*="st-key-open_"] button:hover{ color:var(--deep); background:transparent; }

.gc-foot{ color:var(--muted); font-size:0.78rem; line-height:1.55; max-width:95ch; border-top:1px solid var(--rule); padding-top:16px; margin-top:32px; }

/* KPI grid variants */
.gc-grid.n3{ grid-template-columns:repeat(3, minmax(0,1fr)); }
.gc-grid.n4{ grid-template-columns:repeat(4, minmax(0,1fr)); }
.gc-grid.n5{ grid-template-columns:repeat(5, minmax(0,1fr)); }
@media (max-width:1100px){ .gc-grid.n4, .gc-grid.n5{ grid-template-columns:repeat(2, minmax(0,1fr)); } }
.gc-q-sub{ color:var(--muted); font-size:0.78rem; line-height:1.35; }
.gc-q-step{ display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:7px;
  background:var(--tint); color:var(--brand-dark); font-size:0.78rem; font-weight:700; margin-right:8px; }
.gc-q-name.step{ display:flex; align-items:center; }
.gc-pill.warn{ color:#9A5B00; background:rgba(242,169,59,.18); }
.gc-hero.slim{ padding:20px 28px; margin-bottom:16px; }
.gc-hero.slim .gc-hero-t{ font-size:1.6rem; }
.gc-lead{ color:var(--muted); font-size:0.92rem; line-height:1.5; margin:0 0 14px; max-width:78ch; }
.gc-lead b{ color:var(--ink); font-weight:600; }

/* Tabs */
[data-baseweb="tab-list"]{ gap:4px; }
button[data-baseweb="tab"]{ background:transparent; padding:10px 16px; color:var(--muted); font-weight:500; }
button[data-baseweb="tab"]:hover{ color:var(--brand-dark); background:transparent; }
button[data-baseweb="tab"][aria-selected="true"]{ color:var(--brand-dark); font-weight:600; }
[data-baseweb="tab-highlight"]{ background:var(--brand); height:3px; border-radius:3px 3px 0 0; }
[data-baseweb="tab-border"]{ background:var(--rule); }

/* Expanders, toggles, selects */
[data-testid="stExpander"]{ background:var(--surface); border:1px solid var(--rule); border-radius:14px; box-shadow:none; }
[data-testid="stExpander"] summary{ font-weight:600; color:var(--ink); }
[data-testid="stExpander"] summary:hover{ color:var(--brand-dark); }
[data-baseweb="select"] > div{ background:var(--surface); border-color:var(--rule); border-radius:10px; }
.gc-state{ color:var(--muted); font-size:0.9rem; line-height:1.5; padding:34px 6px 30px; text-align:center; }
.gc-state b{ display:block; color:var(--ink); font-weight:600; margin-bottom:4px; }

/* Primary button */
button[data-testid="stBaseButton-primary"]{ background:var(--brand-dark); color:#fff; border:1px solid var(--brand-dark); border-radius:10px; font-weight:600; }
button[data-testid="stBaseButton-primary"]:hover{ background:var(--deep); border-color:var(--deep); color:#fff; }

/* Compact table */
.gc-table{ width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; font-size:0.9rem; }
.gc-table th{ text-align:right; font-weight:500; color:var(--muted); font-size:0.78rem; padding:6px 8px; border-bottom:1px solid var(--rule); }
.gc-table th:first-child, .gc-table td:first-child{ text-align:left; }
.gc-table td{ text-align:right; padding:9px 8px; border-bottom:1px solid var(--rule); color:var(--ink); }
.gc-table td:first-child{ color:var(--muted); font-weight:500; }
.gc-table tr:last-child td{ border-bottom:none; }
.gc-table td.hl{ font-weight:600; }
.gc-table tr.lv-r td:first-child{ color:#C3282D; font-weight:600; }
.gc-table tr.lv-s td:first-child{ color:#14773F; font-weight:600; }
.gc-table tr.lv-p td{ background:var(--tint); font-weight:600; }
.gc-table tr.lv-p td:first-child{ color:var(--brand-dark); }
.gc-small{ color:var(--muted); font-size:0.78rem; line-height:1.5; margin:10px 0 0; }
</style>
""")


LIGHT_THEME = {
    "theme.base": "light",
    "theme.primaryColor": COLORS["brand"],
    "theme.backgroundColor": COLORS["bg"],
    "theme.secondaryBackgroundColor": COLORS["surface"],
    "theme.textColor": COLORS["ink"],
}


def force_light_theme():
    """Pin the Streamlit theme to light from code, so the app looks the same whether or not
    .streamlit/config.toml is deployed and whatever the viewer's OS dark-mode setting is.
    Must run before any other Streamlit call on each run."""
    changed = False
    try:
        for k, v in LIGHT_THEME.items():
            if st._config.get_option(k) != v:
                st._config.set_option(k, v)
                changed = True
    except Exception:
        return  # private API; the CSS below and config.toml still apply
    if changed:
        st.rerun()  # the theme is sent to the browser at the start of a run, so run once more


def apply_theme():
    st.markdown(_CSS.substitute(COLORS), unsafe_allow_html=True)


def hero(title, subtitle="", meta="", slim=False):
    cls = "gc-hero slim" if slim else "gc-hero"
    st.markdown(
        f'<div class="{cls}"><div><div class="gc-hero-t">{title}</div>'
        + (f'<div class="gc-hero-s">{subtitle}</div>' if subtitle else "")
        + f'</div><div class="gc-hero-m">{meta}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_grid(cards, cols=4):
    """cards: list of dicts with label, value, and optional pill, pill_cls (up/down/flat/warn), sub, step."""
    cells = []
    for c in cards:
        step = f'<span class="gc-q-step">{c["step"]}</span>' if c.get("step") else ""
        name_cls = "gc-q-name step" if step else "gc-q-name"
        pill = f'<div><span class="gc-pill {c.get("pill_cls", "flat")}">{c["pill"]}</span></div>' if c.get("pill") else ""
        sub = f'<div class="gc-q-sub">{c["sub"]}</div>' if c.get("sub") else ""
        cells.append(
            f'<div class="gc-q"><div class="{name_cls}">{step}{c["label"]}</div>'
            f'<div class="gc-q-price">{c["value"]}</div>{pill}{sub}</div>'
        )
    st.markdown(f'<div class="gc-grid n{cols}">{"".join(cells)}</div>', unsafe_allow_html=True)


def panel_head(title, note=""):
    st.markdown(
        f'<div class="gc-h">{title}</div>' + (f'<p class="gc-note">{note}</p>' if note else ""),
        unsafe_allow_html=True,
    )

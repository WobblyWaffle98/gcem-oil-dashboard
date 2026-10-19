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
.st-key-chart_card, .st-key-cal_card{
  background:var(--surface); border:1px solid var(--rule); border-radius:16px; padding:20px 0 12px;
  box-shadow:var(--shadow); overflow:hidden;
}
/* Text and controls get side padding; the chart and calendar run edge to edge so they size to the card exactly */
.st-key-chart_card > [data-testid="stElementContainer"], .st-key-cal_card > [data-testid="stElementContainer"],
.st-key-chart_card > [data-testid="stHorizontalBlock"]{ box-sizing:border-box; padding:0 22px; }
.st-key-chart_card > [data-testid="stElementContainer"]:has(.stPlotlyChart, [data-testid="stPlotlyChart"], .js-plotly-plot),
.st-key-cal_card > [data-testid="stElementContainer"]:has(iframe){ padding:0; }
.gc-h{ font-size:1.15rem; font-weight:600; letter-spacing:-0.02em; margin:0 0 2px; }
.gc-note{ color:var(--muted); font-size:0.86rem; margin:0 0 12px; max-width:64ch; }

/* Streamlit sizes children to the card's outer width; make them fit the padded inner width */
.st-key-chart_card > div, .st-key-cal_card > div, [class*="st-key-sec_"] > div{ width:100% !important; max-width:100% !important; min-width:0; }
.st-key-chart_card, .st-key-cal_card, [class*="st-key-sec_"]{ box-sizing:border-box; min-width:0; }
.st-key-cal_card iframe{ width:100% !important; }
/* Streamlit also pins inner markdown/button wrappers to the card's outer width; let them follow the padded box */
.st-key-chart_card [data-testid="stMarkdown"], .st-key-cal_card [data-testid="stMarkdown"],
[class*="st-key-sec_"] [data-testid="stMarkdown"], [class*="st-key-sec_"] .stButton{ width:100% !important; }

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
</style>
""")


def apply_theme():
    st.markdown(_CSS.substitute(COLORS), unsafe_allow_html=True)

"""Shared look and feel: colour tokens, CSS, and the list of dashboard sections."""
import streamlit as st

COLORS = {
    "bg": "#0B1215",
    "panel": "#111B1F",
    "raise": "#16232A",
    "rule": "#223139",
    "text": "#E6ECEA",
    "muted": "#8A9CA0",
    "accent": "#5CC8B0",
    "up": "#4CC38A",
    "down": "#F0705A",
}

# Sidebar names (exact radio labels) and the one-line blurb shown on the Main page.
SECTIONS = {
    "Macro-economic": "Global indicators, GDP, and the HOPE recession model.",
    "Fundamentals": "EIA supply-demand balances, production, consumption and inventories.",
    "Financial Markets": "Equities, Treasury yields and FX, with correlations to Brent.",
    "Technical and Probability Analysis": "Technical views and Monte Carlo price paths for Brent.",
    "Others": "Geopolitical risk index.",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap');

:root{
  --bg:%(bg)s; --panel:%(panel)s; --raise:%(raise)s; --rule:%(rule)s;
  --text:%(text)s; --muted:%(muted)s; --accent:%(accent)s; --up:%(up)s; --down:%(down)s;
}

/* Base */
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background:var(--bg); color:var(--text);
  font-family:'Instrument Sans', system-ui, sans-serif;
}
[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer, [data-testid="stDeployButton"]{ visibility:hidden; }
.block-container{ padding-top:2.4rem; padding-bottom:4rem; max-width:1480px; }
h1,h2,h3,h4{ font-family:'Newsreader', Georgia, serif; font-weight:500; letter-spacing:-0.01em; color:var(--text); }
a{ color:var(--accent); }
hr{ border-color:var(--rule); }
[data-testid="stCaptionContainer"], .stCaption{ color:var(--muted); }

/* Sidebar */
[data-testid="stSidebar"]{ background:var(--panel); border-right:1px solid var(--rule); }
[data-testid="stSidebar"] [data-testid="stRadio"] > label{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]{ gap:2px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  padding:8px 12px; border-radius:8px; border-left:2px solid transparent; cursor:pointer;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{ background:var(--raise); }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){
  background:var(--raise); border-left-color:var(--accent);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p{ color:var(--text); font-weight:600; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p{ color:var(--muted); font-size:0.95rem; }
[data-testid="stSidebar"] h1{ font-size:1.1rem; color:var(--muted); font-family:'Instrument Sans',sans-serif; font-weight:500; }

/* Buttons and controls */
.stButton > button{
  background:transparent; border:1px solid var(--rule); color:var(--text); border-radius:8px;
}
.stButton > button:hover{ border-color:var(--accent); color:var(--accent); background:transparent; }
.stButton > button:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
[data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-segmented_controlActive"]{
  font-family:'Instrument Sans',sans-serif;
}

/* Masthead */
.gc-mast{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap;
  padding-bottom:18px; margin-bottom:20px; border-bottom:1px solid var(--rule); }
.gc-title{ font-family:'Newsreader', Georgia, serif; font-size:2.5rem; line-height:1.05; font-weight:400; letter-spacing:-0.02em; }
.gc-title span{ color:var(--muted); }
.gc-meta{ text-align:right; color:var(--muted); font-size:0.85rem; line-height:1.5; font-variant-numeric:tabular-nums; }
.gc-meta b{ color:var(--text); font-weight:500; }

/* Quote strip: one hairline-divided band rather than separate cards */
.gc-strip{ display:grid; grid-template-columns:repeat(6, 1fr); gap:1px; background:var(--rule);
  border:1px solid var(--rule); border-radius:12px; overflow:hidden; margin-bottom:28px; }
.gc-q{ background:var(--panel); padding:16px 18px 14px; display:flex; flex-direction:column; gap:6px; min-width:0; }
.gc-q-top{ display:flex; justify-content:space-between; align-items:baseline; gap:8px; }
.gc-q-name{ color:var(--muted); font-size:0.85rem; }
.gc-q-price{ font-size:1.65rem; font-weight:500; letter-spacing:-0.01em; font-variant-numeric:tabular-nums; line-height:1.1; }
.gc-q-row{ display:flex; justify-content:space-between; align-items:flex-end; gap:8px; }
.gc-q-chg{ font-size:0.85rem; font-variant-numeric:tabular-nums; font-weight:500; }
.gc-q-chg.up{ color:var(--up); } .gc-q-chg.down{ color:var(--down); } .gc-q-chg.flat{ color:var(--muted); }
.gc-q svg{ display:block; flex:none; }
@media (max-width:1200px){ .gc-strip{ grid-template-columns:repeat(3, 1fr); } }
@media (max-width:640px){ .gc-strip{ grid-template-columns:repeat(2, 1fr); } .gc-title{ font-size:1.9rem; } .gc-meta{ text-align:left; } }

/* Section headings on the page */
.gc-h{ font-family:'Newsreader', Georgia, serif; font-size:1.5rem; font-weight:500; margin:0 0 2px; }
.gc-note{ color:var(--muted); font-size:0.88rem; margin:0 0 12px; max-width:62ch; }

/* Section index */
.gc-card{ background:var(--panel); border:1px solid var(--rule); border-radius:12px; padding:18px 18px 16px; min-height:128px; }
.gc-card-t{ font-family:'Newsreader', Georgia, serif; font-size:1.2rem; line-height:1.2; margin-bottom:8px; }
.gc-card-d{ color:var(--muted); font-size:0.88rem; line-height:1.45; }
[class*="st-key-open_"] button{ border:none; padding:6px 2px; color:var(--accent); justify-content:flex-start; min-height:0; }
[class*="st-key-open_"] button:hover{ color:var(--text); }

.gc-foot{ color:var(--muted); font-size:0.78rem; line-height:1.55; max-width:90ch; border-top:1px solid var(--rule); padding-top:16px; margin-top:36px; }
</style>
"""


def apply_theme():
    st.markdown(_CSS % COLORS, unsafe_allow_html=True)

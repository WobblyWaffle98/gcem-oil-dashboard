import streamlit as st
from main_page import main_page
from macro_economic_page import macro_economic_page
from fundamentals_page import fundamentals_page
from financial_markets_page import financial_markets_page
from technical_probability_page import technical_probability_page

# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide")

# Streamlit app title
st.title("Oil Indicator Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main", "Macro-economic", "Fundamentals", "Financial Markets", "Technical and Probability Analysis"])

# Render selected page
if page == "Main":
    main_page()
elif page == "Macro-economic":
    macro_economic_page()
elif page == "Fundamentals":
    fundamentals_page()
elif page == "Financial Markets":
    financial_markets_page()
elif page == "Technical and Probability Analysis":
    technical_probability_page()

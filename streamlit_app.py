import streamlit as st
from main_page import main_page
from macro_economic_page import macro_economic_page
from fundamentals_page import fundamentals_page
from financial_markets_page import financial_markets_page
from technical_probability_page import technical_probability_page
from others_page import others_page
from theme import apply_theme, SECTIONS

# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide", page_icon=r'Images/Theta_icon_changed.png')

apply_theme()

# Sidebar for navigation
st.sidebar.image(r'Images/Untitled design (1).png', use_container_width=True)
st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Main", *SECTIONS], key="nav_page")

with st.sidebar:
    st.html(
        """
        <div style="text-align:center; font-size:12px; ">
            <hr style="margin-bottom: 6%; margin-top: 6%;">
            </a><br><br>
            <b>Data Disclamer</b><br>
            Please note that the data provided on this platform is sourced from publicly available market information. Any interpretation or analysis derived from this data is solely the responsibility of the user.
            <br><br>GCEM does not guarantee the accuracy or completeness of the data and will
            not be held liable for any decisions or actions taken based on its use.
        </div>
        """
    )

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
elif page == "Others":
    others_page()

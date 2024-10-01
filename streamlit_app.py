import streamlit as st
from main_page import main_page
from macro_economic_page import macro_economic_page
from fundamentals_page import fundamentals_page
from financial_markets_page import financial_markets_page
from technical_probability_page import technical_probability_page
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)




# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide",page_icon=r'Images/Theta_icon_changed.png')


# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)



# Sidebar for navigation
st.sidebar.image(r'Images/Heading (4).png',use_column_width=True)
st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Main", "Macro-economic", "Fundamentals", "Financial Markets", "Technical and Probability Analysis"])

with st.sidebar:
    st.html(
            """
            <div style="text-align:center; font-size:12px; color:grey">
                <hr style="margin-bottom: 6%; margin-top: 6%;">
                </a><br><br>
                <b>Data Disclamer</b><br>
                Please note that the data provided on this platform is sourced from publicly available market information. Any interpretation or analysis derived from this data is solely the responsibility of the user.
                <br><br>GCEM does not guarantee the accuracy or completeness of the data and will 
                not be held liable for any decisions or actions taken based on its use.
            </div>
        """
        )


if st.session_state["authentication_status"]:
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


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


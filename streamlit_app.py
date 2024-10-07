import streamlit as st
from main_page import main_page
from macro_economic_page import macro_economic_page
from fundamentals_page import fundamentals_page
from financial_markets_page import financial_markets_page
from technical_probability_page import technical_probability_page
from user_settings_page import user_settings
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
from pymongo.server_api import ServerApi
from pymongo import MongoClient


def get_password(username):
    # Fetch the user's data from MongoDB
    config = config_collection.find_one({})

    # Check if the user exists in the 'usernames' dictionary
    if username in config['credentials']['usernames']:
        # Return the user's password
        return config['credentials']['usernames'][username]['password']
    else:
        return f"Username {username} not found."
    
def change_password(username, new_password):
    # Fetch the user's data from MongoDB
    config = config_collection.find_one({})

    # Check if the user exists in the 'usernames' dictionary
    if username in config['credentials']['usernames']:
        # Update the user's password
        config['credentials']['usernames'][username]['password'] = new_password

        # Save the updated document back to MongoDB
        config_collection.update_one(
            {},  # match the document (assuming there's only one document)
            {"$set": {"credentials.usernames": config['credentials']['usernames']}}
        )
    else:
        print(f"Username {username} not found.")



# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide",page_icon=r'Images/Theta_icon_changed.png')


uri = st.secrets["uri"]
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Step 2: Access the database
db = client['TEST_DATABASE']
config_collection = db['TEST_COLLECTION']

# Fetch the configuration from MongoDB
config = config_collection.find_one({})  # Fetch the first document

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

page = st.sidebar.radio("Go to", ["Main", "Macro-economic", "Fundamentals", "Financial Markets", "Technical and Probability Analysis", "User Settings"])

with st.sidebar:
    if st.session_state["authentication_status"]:
        authenticator.logout()
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
    elif page == "User Settings":
        user_settings()


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


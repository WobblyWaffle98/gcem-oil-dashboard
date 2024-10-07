import streamlit as st
from pymongo.server_api import ServerApi
from pymongo import MongoClient


uri = "mongodb+srv://harithzahrin:bLfv0OY29B0xxaDw@oil-dashboard.cey6w.mongodb.net/?retryWrites=true&w=majority&appName=Oil-Dashboard"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Step 2: Access the database
db = client['TEST_DATABASE']
config_collection = db['TEST_COLLECTION']

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

def user_settings():
    st.header("Password Reset")
    with st.form(key="change_password_form"):
        st.write("Please refrain from using any existing passwords or passwords that grant access to sensitive data")
        # Fields for current and new password
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        reenter_password = st.text_input("Re-enter New Password", type="password")

        password = get_password(st.session_state["username"])
        # Submit button
        submit_button = st.form_submit_button(label="Change Password")

        # Password validation logic
        if submit_button:
            if current_password != password:
                st.error("Current password do not match")
            elif new_password != reenter_password:
                st.error("New passwords do not match.")
            else:
                change_password(st.session_state["username"], new_password)
                st.success("Password changed successfully!")
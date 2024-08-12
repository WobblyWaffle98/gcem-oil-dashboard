import streamlit as st
from main_page import main_page
from macro_economic_page import macro_economic_page
from fundamentals_page import fundamentals_page
from financial_markets_page import financial_markets_page
from technical_probability_page import technical_probability_page
import base64

def displayLocalGIF2(placeholder, localImagePath, caption):
    imgFile  = open(localImagePath, "rb")
    contents = imgFile.read()
    imgData  = base64.b64encode(contents).decode("utf-8")
    imgFile.close()
    
    # Define CSS styles for the container and caption
    # Define CSS styles
    container_style = "max-width: 100%; text-align: center; margin: auto;"
    caption_style = "font-size: 14px; color: #555; margin-top: 10px;"
    
    caption_style = (
        "font-size: 14px;"      # Adjust the font size as needed
        "color: #888888;"       # Dimmer color
        "text-align: center;"   # Center the caption text
    )
    
    # Display the GIF and caption within the placeholder
    placeholder.markdown(
        f"""
        <div style="{container_style}">
            <img src="data:image/gif;base64,{imgData}" style="width: 100%; height: auto;">
            <p style="{caption_style}">{caption}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    





# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide",page_icon=r'Images/Theta_icon_changed.png')
# Streamlit app title
st.title("GCEM Oil Indicator Dashboard")
image_placeholder2 = st.empty()
imagePath2 = "Images/DASHBOARD_GIF.gif
displayLocalGIF2(image_placeholder2, imagePath2,"")



# Sidebar for navigation
st.sidebar.image(r'Images/Heading (4).png',use_column_width=True)
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

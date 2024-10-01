import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import streamlit.components.v1 as components


import os, sys
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import base64

# Suppress SSL verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


    




def main_page():

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

    
    # Streamlit app title
    image_placeholder2 = st.empty()
    imagePath2 = "Images/DASHBOARD_GIF_2optimized.gif"
    displayLocalGIF2(image_placeholder2, imagePath2,"")



    st.write("""
    Welcome to the GCEM Oil Indicator Dashboard! This is the main page where you can find upcoming economic events and current market prices for oil and gas. 

    For more detailed analysis, please use the sidebar to navigate to the following sections:

    - **Macro-economic**: Explore detailed macroeconomic data and insights.
    - **Fundamentals**: Access fundamental analysis for various commodities and markets.
    - **Financial Markets**: View data and trends from different financial markets.
    - **Technical and Probability Analysis**: Dive into technical analysis tools and probability-based evaluations.

    """)
    with st.container():
        st.write("This is inside the container")
        st.write("Please note that the data provided is sourced from publicly available market information. Any interpretation or analysis derived from this data is solely the responsibility of the user. GCEM does not guarantee the accuracy or completeness of the data and will not be held liable for any decisions or actions taken based on its use.")
        

    st.divider()
    

    col1,col2 = st.columns(2)

    with col1:
        st.header("Economic Calendar")
        st.write("""
                The Economic calendar provides a schedule of significant economic events and data releases, 
                such as GDP figures, employment reports, inflation data, and central bank announcements.​
                
                 Users can also filter the data by countries and timeline.​
                 
                 """)
        # Define the HTML content for the Investing.com Economic Calendar iframe
        # HTML content for the iframe
        investing_calendar = """
            <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Centered Content Example</title>
        <style>
            body {
                margin: 0;
                display: flex;
                justify-content: left;
                align-items: left;
                height: 100vh;
            }

            .container {
                width: 90%;
                max-width: 800px; /* Adjust max-width as per your design */
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="width: 100%; height: 100%; overflow: hidden;">
                <iframe src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&importance=2,3&features=datepicker,timeselector,filters&countries=37,42,5&calType=week&timeZone=113&lang=1" 
                style="width: 100%; height: 100%; border: none;" 
                frameborder="0" allowtransparency="true"></iframe>
            </div>

        </div>
    </body>
    </html>
        """

        
        components.html(investing_calendar, height=800, scrolling=False)

        # Import IBM Plex Sans font
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

            body {
                font-family: 'IBM Plex Sans', sans-serif;
            }
            .left-align {
                text-align: left;
                font-family: 'IBM Plex Sans', sans-serif;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Use the font with right-aligned text
        st.markdown("<p class='left-align'>Source: Investing.com</p>", unsafe_allow_html=True)

    with col2:
        

        # Define the HTML content for the Investing.com Economic Calendar iframe
        # HTML content for the iframe
        Brent_chart = """
                            <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Centered Content Example</title>
                        <style>
                            body {
                                margin: 0;
                                display: flex;
                                justify-content: left;
                                align-items: left;
                                height: 100vh;
                            }

                            .container {
                                width: 90%;
                                max-width: 800px; /* Adjust max-width as per your design */
                                text-align: left;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <!-- TradingView Widget BEGIN -->
                            <div class="tradingview-widget-container" style="height:100%;width:100%">
                            <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
                            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                            {
                            "autosize": true,
                            "symbol": "VELOCITY:BRENT",
                            "interval": "D",
                            "timezone": "Asia/Kuala_Lumpur",
                            "theme": "dark",
                            "style": "1",
                            "locale": "en",
                            "hide_legend": true,
                            "withdateranges": true,
                            "allow_symbol_change": false,
                            "calendar": false,
                            
                            "hide_volume": true,
                            "support_host": "https://www.tradingview.com"
                            }
                            </script>
                            </div>
                            <!-- TradingView Widget END -->

                        </div>
                    </body>
                    </html>
                    """
        
        WTI_chart = """
                            <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Centered Content Example</title>
                        <style>
                            body {
                                margin: 0;
                                display: flex;
                                justify-content: left;
                                align-items: left;
                                height: 100vh;
                            }

                            .container {
                                width: 90%;
                                max-width: 800px; /* Adjust max-width as per your design */
                                text-align: left;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <!-- TradingView Widget BEGIN -->
                            <div class="tradingview-widget-container" style="height:100%;width:100%">
                            <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
                            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                            {
                            "autosize": true,
                            "symbol": "NYMEX:CL1!",
                            "interval": "D",
                            "timezone": "Asia/Kuala_Lumpur",
                            "theme": "dark",
                            "style": "1",
                            "locale": "en",
                            "hide_legend": true,
                            "withdateranges": true,
                            "allow_symbol_change": false,
                            "calendar": false,

                            "hide_volume": true,
                            "support_host": "https://www.tradingview.com"
                            }
                            </script>
                            </div>
                            <!-- TradingView Widget END -->

                        </div>
                    </body>
                    </html>
                    """
        
        NatGas_chart = """
                            <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Centered Content Example</title>
                        <style>
                            body {
                                margin: 0;
                                display: flex;
                                justify-content: left;
                                align-items: left;
                                height: 100vh;
                            }

                            .container {
                                width: 90%;
                                max-width: 800px; /* Adjust max-width as per your design */
                                text-align: left;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <!-- TradingView Widget BEGIN -->
                            <div class="tradingview-widget-container" style="height:100%;width:100%">
                            <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
                            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                            {
                            "autosize": true,
                            "symbol": "NYMEX:NG1!",
                            "interval": "D",
                            "timezone": "Asia/Kuala_Lumpur",
                            "theme": "dark",
                            "style": "1",
                            "locale": "en",
                            "hide_legend": true,
                            "withdateranges": true,
                            "allow_symbol_change": false,
                            "calendar": false,

                            "hide_volume": true,
                            "support_host": "https://www.tradingview.com"
                            }
                            </script>
                            </div>
                            <!-- TradingView Widget END -->

                        </div>
                    </body>
                    </html>
                    """
        st.header("Latest Price (Daily)")
        st.write("""
                 The latest price data is sourced from TradingView. 

                 While there may be slight deviations or delays compared to official price data, this information is generally reliable for tracking price direction and trends. 
                 """)
        st.subheader('Brent Price (Velocity)')
        components.html(Brent_chart, height=500, scrolling=False)
        st.markdown("<p class='left-align'>Source:TradingView (Velocity)</p>", unsafe_allow_html=True)    
        st.subheader('WTI Price (NYMEX)')
        components.html(WTI_chart, height=500, scrolling=False)
        st.markdown("<p class='left-align'>Source:TradingView (NYMEX)</p>", unsafe_allow_html=True)  
        st.subheader('Henry Hub Price (NYMEX)')
        components.html(NatGas_chart, height=500, scrolling=False)
        s
        st.markdown("<p class='left-align'>Source:TradingView (NYMEX)</p>", unsafe_allow_html=True)  


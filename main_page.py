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

# Suppress SSL verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def main_page():

    

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Economic Calendar")
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

    with col2:
        st.subheader('Latest Brent Price')

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
            "studies": [
                "STD;Pivot%1Points%1High%1Low"
            ],
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

        components.html(Brent_chart, height=800, scrolling=False)




import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import yfinance as yf
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import plotly.graph_objs as go

def financial_markets_page():
    st.header("Financial Market Indicators")
    # Add financial markets page specific code here
    tab1, tab2, tab3 = st.tabs(["Equities","Fixed Income","FX"])

    with tab1:
        # Define the ticker symbols and their corresponding names
        tickers = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones Industrial Average',
            '^IXIC': 'NASDAQ Composite',
            'BZ=F': 'Brent Crude Oil',
            '000001.SS': 'Shanghai Composite Index',
            '^N225': 'Nikkei 225',
            '^GDAXI': 'DAX',
            '^FTSE': 'FTSE 100',
            '^NSEI': 'NIFTY 50'
        }

        # Function to fetch data and plot heatmap
        def fetch_and_plot_correlation(period):
            # Determine the start date based on the selected period
            end_date = datetime.now()
            if period == '1 Year':
                start_date = end_date - timedelta(days=365)
            elif period == '5 Years':
                start_date = end_date - timedelta(days=5*365)
            elif period == '10 Years':
                start_date = end_date - timedelta(days=10*365)
            
            # Fetch historical data
            data = yf.download(list(tickers.keys()), start=start_date, end=end_date)['Adj Close']
            
            # Rename columns to equity names
            data.rename(columns=tickers, inplace=True)
            
            # Calculate the correlation matrix
            correlation_matrix = data.corr()
            
            # Plot the heatmap using Plotly
            fig = px.imshow(correlation_matrix, 
                            text_auto=True, 
                            aspect="auto", 
                            color_continuous_scale='RdBu_r',
                            labels={'color': 'Correlation Coefficient'},
                            title=f'Correlation Matrix of Stock Markets and Brent Crude Oil Prices ({period} Data)',zmin=-1, zmax=1)
            
            st.plotly_chart(fig, use_container_width=True)

        # Streamlit app layout
        st.title('Correlation Matrix of Stock Markets and Brent Crude Oil Prices')

        # Dropdown menu for selecting period
        period = st.selectbox('Select Period:', ['1 Year', '5 Years', '10 Years'])

        # Fetch data and plot correlation matrix
        fetch_and_plot_correlation(period)

    with tab2:

        # Suppress SSL verification warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # FRED API endpoint for Treasury yields
        fred_api_url = "https://api.stlouisfed.org/fred/series/observations"

        # API key (get your own API key from FRED)
        api_key = "0ba1761f1d82d23194c202620bb7d7f9"

        # Define the Treasury yield symbols (constant maturity) and their order
        treasury_yields = {
            "3-Month": "DGS3MO",
            "6-Month": "DGS6MO",
            "1-Year": "DGS1",
            "2-Year": "DGS2",
            "5-Year": "DGS5",
            "10-Year": "DGS10",
            "30-Year": "DGS30"
        }

        # Streamlit app
        st.title('US Treasury Yield Curve Visualization')

        # Date input for user to select a date
        specific_date = st.date_input('Select a date', datetime(2024, 6, 6))

        # Fetch Treasury yield data from FRED
        yields = {}
        for maturity, symbol in treasury_yields.items():
            params = {
                "series_id": symbol,
                "api_key": api_key,
                "file_type": "json"
            }
            response = requests.get(fred_api_url, params=params, verify=False)
            if response.status_code == 200:
                data = response.json()
                # Find the observation for the specified date
                observation = next((obs for obs in data["observations"] if obs["date"] == specific_date.strftime('%Y-%m-%d')), None)
                if observation:
                    try:
                        yields[maturity] = float(observation["value"])
                    except ValueError:
                        st.warning(f"Invalid data for {maturity} on {specific_date}: {observation['value']}")
                else:
                    st.warning(f"No data available for {maturity} on {specific_date}")
            else:
                st.error(f"Failed to fetch data for {maturity}")

        # Check if any data was fetched
        if not yields:
            st.error(f"No yield data available for the specified date: {specific_date}")
        else:
            # Sort yields by maturity
            sorted_yields = dict(sorted(yields.items(), key=lambda item: list(treasury_yields.keys()).index(item[0])))

            # Plot the yield curve using Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(sorted_yields.keys()), y=list(sorted_yields.values()), mode='lines+markers'))
            fig.update_layout(
                title=f'US Treasury Yield Curve (Data as of {specific_date})',
                xaxis_title='Maturity',
                yaxis_title='Yield (%)',
                xaxis=dict(tickangle=45),
                showlegend=False
            )
            st.plotly_chart(fig)


    with tab3:
        # Define the FX ticker symbols and their corresponding names
        fx_tickers = {
            'BZ=F': 'Brent Crude Oil',
            'EURUSD=X': 'EUR/USD',
            'JPY=X': 'USD/JPY',
            'GBPUSD=X': 'GBP/USD',
            'AUDUSD=X': 'AUD/USD',
            'USDCAD=X': 'USD/CAD',
            'USDCHF=X': 'USD/CHF',
            'NZDUSD=X': 'NZD/USD',
            'DX-Y.NYB': 'US Dollar Index'
        }

        # Function to fetch data and plot heatmap
        def fetch_and_plot_fx_correlation(period):
            # Determine the start date based on the selected period
            end_date = datetime.now()
            if period == '1 Year':
                start_date = end_date - timedelta(days=365)
            elif period == '5 Years':
                start_date = end_date - timedelta(days=5*365)
            elif period == '10 Years':
                start_date = end_date - timedelta(days=10*365)
            
            # Fetch historical data
            data = yf.download(list(fx_tickers.keys()), start=start_date, end=end_date)['Adj Close']
            
            # Rename columns to FX pair names
            data.rename(columns=fx_tickers, inplace=True)
            
            # Calculate the correlation matrix
            correlation_matrix = data.corr()
            
            # Plot the heatmap using Plotly
            fig = px.imshow(correlation_matrix, 
                            text_auto=True, 
                            aspect="auto", 
                            color_continuous_scale='RdBu_r',
                            labels={'color': 'Correlation Coefficient'},
                            title=f'Correlation Matrix of FX Pairs ({period} Data)',zmin=-1, zmax=1)
            
            st.plotly_chart(fig, use_container_width=True)

        # Streamlit app layout
        st.title('Correlation Matrix of FX Pairs')

        # Dropdown menu for selecting period
        fx_period = st.selectbox('Select Period for FX:', ['1 Year', '5 Years', '10 Years'])

        # Fetch data and plot correlation matrix
        fetch_and_plot_fx_correlation(fx_period)
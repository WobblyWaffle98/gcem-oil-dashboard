import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import yfinance as yf
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import plotly.graph_objs as go
import time



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
        
        current_year = datetime.now().year
        previous_year = current_year - 1
        previousprevious_year = current_year - 2

        # Python code to download data from Treasury
        def get_data():
            all_data = []
            for year in [current_year, previous_year,previousprevious_year]:
                print(year)
                year = str(year)
                url1 = f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/'+year+'/all?type=daily_treasury_yield_curve&field_tdr_date_value='+year+'page&_format=csv'
                
                data = pd.read_csv(url1)
                all_data.append(data)
            
            pd_alldata = pd.concat(all_data, ignore_index=True)
            pd_alldata['Date'] = pd.to_datetime(pd_alldata['Date'])
            pd_alldata.index = pd_alldata['Date']
            
            req_cols = ['1 Mo','2 Mo','3 Mo', '6 Mo', '1 Yr', '2 Yr', '3 Yr', '5 Yr', 
                        '7 Yr', '10 Yr', '20 Yr', '30 Yr']
            final = pd_alldata[req_cols]

            return final

        # Get the data
        data = get_data()


        # Create traces for each column
        traces = []
        for col in data.columns:
            trace = go.Scatter(x=data.index, y=data[col], mode='lines', name=col)
            traces.append(trace)

        # Create layout
        layout = go.Layout(title='Treasury Yield Time Series',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Yield (%)'))

        # Create figure
        fig = go.Figure(data=traces, layout=layout)

        st.plotly_chart(fig, use_container_width=True)

        #########################

        # Extract the first and seventh rows
        Current = data.iloc[0]
        Last_week = data.iloc[6]
        Last_Month = data.iloc[29]
        Last_Year = data.iloc[364]

        # Create a figure
        fig = go.Figure()

        # Add first row data to the plot
        fig.add_trace(go.Scatter(x=Current.index, y=Current.values, mode='lines', name='Current'))

        # Add seventh row data to the plot
        fig.add_trace(go.Scatter(x=Last_week.index, y=Last_week.values, mode='lines', name='Last Week'))

        # Add seventh row data to the plot
        fig.add_trace(go.Scatter(x=Last_Month.index, y=Last_Month.values, mode='lines', name='Last Month'))

        # Add seventh row data to the plot
        fig.add_trace(go.Scatter(x=Last_Year.index, y=Last_Year.values, mode='lines', name='Last Year'))

        # Customize layout
        fig.update_layout(
            title="Treasury Yield Curve",
            xaxis_title="Maturity",
            yaxis_title="Rate (%)"
        )

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)


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

     # Function to plot time series of DXY and Brent
        def plot_time_series():
            # Define start date as July 2007
            start_date = datetime(2007, 7, 1)
            
            # Fetch data for DXY and Brent Crude Oil
            df_dxy = yf.download("DX-Y.NYB", start=start_date)['Adj Close']
            df_brent = yf.download("BZ=F", start=start_date)['Adj Close']

            fig_ts = go.Figure()

            # Add trace for DXY
            fig_ts.add_trace(go.Scatter(x=df_dxy.index, y=df_dxy, name="US Dollar Index", yaxis="y1"))

            # Add trace for Brent Crude Oil
            fig_ts.add_trace(go.Scatter(x=df_brent.index, y=df_brent, name="Brent Crude Oil", yaxis="y2"))

            # Update layout to have two y-axes
            fig_ts.update_layout(
                title="Time Series of DXY and Brent",
                xaxis_title="Date",
                yaxis=dict(title="US Dollar Index", color="blue"),
                yaxis2=dict(title="Brent Crude Oil", color="red", overlaying="y", side="right")
            )

            st.plotly_chart(fig_ts, use_container_width=True)

            # Calculate rolling one-year correlation
            rolling_corr = df_dxy.rolling(window=252, min_periods=1).corr(df_brent)

            # Plot rolling correlation
            fig_corr = go.Figure()
            fig_corr.add_trace(go.Scatter(x=rolling_corr.index, y=rolling_corr,fill='tozeroy', name="Rolling 1-Year Correlation"))
            fig_corr.update_layout(
                title="Rolling 1-Year Correlation between DXY and Brent Crude Oil",
                xaxis_title="Date",
                yaxis_title="Correlation",
                showlegend=False
            )
            st.plotly_chart(fig_corr, use_container_width=True)

        # Streamlit app layout
        st.title('Time Series of DXY and Brent')

        # Plot time series and rolling correlation
        plot_time_series()
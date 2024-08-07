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
import streamlit.components.v1 as components



def financial_markets_page():
    st.header("Financial Market Indicators")
    # Add financial markets page specific code here
    tab1, tab2, tab3 = st.tabs(["Equities","Fixed Income","FX"])

    with tab1:
        Equities_overview = """
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
                                    justify-content: centre;
                                    align-items: centre;
                                    height: 100vh;
                                }

                                .container {
                                    width: 90%;
                                    max-width: 1500px; /* Adjust max-width as per your design */
                                    text-align: centre;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <!-- TradingView Widget BEGIN -->
                                    <div class="tradingview-widget-container">
                                    <div class="tradingview-widget-container__widget"></div>
                                    <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                                    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>
                                    {
                                    "exchanges": [],
                                    "dataSource": "SPX500",
                                    "grouping": "sector",
                                    "blockSize": "market_cap_basic",
                                    "blockColor": "Perf.W",
                                    "locale": "en",
                                    "symbolUrl": "",
                                    "colorTheme": "dark",
                                    "hasTopBar": false,
                                    "isDataSetEnabled": false,
                                    "isZoomEnabled": true,
                                    "hasSymbolTooltip": true,
                                    "isMonoSize": false,
                                    "width": "100%",
                                    "height": "100%"
                                    }
                                    </script>
                                    </div>
                                    <!-- TradingView Widget END -->

                            </div>
                        </body>
                        </html>
                        """

        st.subheader('Market Overview Heatmap')
        st.write('''
            The interactive heatmap provides a comprehensive view of all companies in the S&P500 index. 
            The heatmap is color-coded to reflect each company's weekly performance, with block sizes proportional to their market capitalization.
             Grouped by sector, it allows you to easily identify trends and performance across different industries. 
                 
            Hover over specific sectors or companies for detailed insights and a closer look at individual performance.

            ''')

        components.html(Equities_overview, height=500, scrolling=False)

        st.divider()

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
            correlation_matrix = data.corr().round(2)
            
            # Plot the heatmap using Plotly
            fig = px.imshow(
                correlation_matrix, 
                text_auto=True, 
                aspect="auto", 
                color_continuous_scale='rdbu',
                labels={'color': 'Correlation Coefficient'},
                title=f'Correlation Matrix of Stock Markets and Brent Crude Oil Prices ({period} Data)',
                zmin=-1, zmax=1
            )
            
            # Update the hover template to display the correlation value rounded to 2 decimal places
            fig.update_traces(hovertemplate='Value: %{z:.2f}')
            
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("VIX index")

        st.write("""
                The VIX Index, often referred to as the "Fear Gauge," is a measure of market volatility and investor sentiment. Officially known as the CBOE Volatility Index, it is calculated and published by the Chicago Board Options Exchange (CBOE). 
                The VIX Index represents the market's expectations of 30-day future volatility based on options prices for the S&P 500 Index (SPX).
                 """)

        # Define the start date 5 years ago
        end_date = datetime.now()

        # Download the VIX and S&P 500 data
        vix_data = yf.download("^VIX", start='2004-01-01', end=end_date)
        sp500_data = yf.download("^GSPC", start='2004-01-01', end=end_date)

        # Create a plotly figure
        fig = go.Figure()

        # Add the VIX data to the figure
        fig.add_trace(go.Scatter(x=vix_data.index, y=vix_data['Close'], mode='lines', name='VIX'))

        # Add the S&P 500 data to the figure
        fig.add_trace(go.Scatter(x=sp500_data.index, y=sp500_data['Close'], mode='lines', name='S&P 500', yaxis='y2'))

        # Add shaded regions for recession periods
        recession_periods = [
            ('2007-12-01', '2009-06-30'),  # Great Recession
            ('2020-02-01', '2020-11-30'),  # COVID-19 Recession
        ]
        for start, end in recession_periods:
            fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor="red",
                opacity=0.2,
                layer="below",
                line_width=0,
                name="Recession Period"
            )

        # Update the layout for dual y-axes
        fig.update_layout(
            title="CBOE Volatility Index and S&P 500",
            xaxis_title="Date",
            yaxis=dict(
                title="VIX Value",

            ),
            yaxis2=dict(
                title="S&P 500 Value",

                overlaying='y',
                side='right'
            ),
            legend=dict(
                    orientation="h",  # Horizontal orientation
                    yanchor="top",    # Position at the top
                    y=-0.2,           # Move below the plot
                    xanchor="center", # Center horizontally
                    x=0.5)
                    # Center horizontally
            
        )

        # Show the figure
        st.plotly_chart(fig)

        # Streamlit app layout
        st.subheader('Correlation Matrix of Stock Markets and Brent Crude Oil Prices')

        st.write('''
            This section presents a heatmap displaying the correlation between major stock markets and Brent Crude Oil prices over different time periods. 
            The results are displayed using a color-coded heatmap, with correlation coefficients ranging from -1(red) to 1(blue).
            ''')


        # Dropdown menu for selecting period
        period = st.selectbox('Select Period:', ['1 Year', '5 Years', '10 Years'])

        # Fetch data and plot correlation matrix
        fetch_and_plot_correlation(period)

    with tab2:

        st.header('U.S. Treasury Yield Curve Analysis')
        st.write('''
            This section provides an analysis of the Treasury yield curve, showcasing both historical time series and recent changes in yield rates. The data is sourced from the **U.S. Department of the Treasury**, covering daily treasury rates for the past three years.

            **What is a Yield Curve?**
            
            A yield curve is a graphical representation of the interest rates (yields) on government bonds of varying maturities, plotted against their respective time to maturity. It shows the relationship between the yield and the time to maturity of debt securities issued by the government.

            **Key Components:**

            - **Yields**: The return investors receive for holding a bond until maturity, expressed as an annual percentage.
            - **Maturities**: The time remaining until the bond’s principal is repaid, ranging from short-term (a few months) to long-term (30 years or more).
                 
                 
            **Use of Yield Curves**:

            - **Economic Indicators**: Yield curves are used to gauge economic expectations. A normal upward-sloping curve suggests economic growth, while an inverted curve may signal a recession.

            - **Interest Rate Predictions**: They help in forecasting future interest rates based on the difference between short-term and long-term rates.

            - **Investment Decisions**: Investors use yield curves to assess the risk and return of different securities. A steep curve can indicate higher returns for long-term investments compared to short-term ones.

            - **Monetary Policy**: Central banks use yield curves to understand market expectations of future economic conditions and to set appropriate monetary policies.
            ''')
        
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
        st.header('Realtime FX rates')
        st.write('''
            This section displays the latest cross rates and daily percentage change for major currencies, providing real-time exchange rate information for key currency pairs.
            ''')
        col1, col2 = st.columns(2)
        with col1:
            FX_chart = """
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
                                    justify-content: centre;
                                    align-items: centre;
                                    height: 100vh;
                                }

                                .container {
                                    width: 90%;
                                    max-width: 800px; /* Adjust max-width as per your design */
                                    text-align: centre;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <!-- TradingView Widget BEGIN -->
                            <div class="tradingview-widget-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-cross-rates.js" async>
                            {
                            "width": "100%",
                            "height": "100%",
                            "currencies": [
                                "EUR",
                                "USD",
                                "JPY",
                                "GBP",
                                "CAD",
                                "MYR"
                            ],
                            "isTransparent": false,
                            "colorTheme": "dark",
                            "locale": "en",
                            "backgroundColor": "#000000"
                            }
                            </script>
                            </div>
                            <!-- TradingView Widget END -->

                            </div>
                        </body>
                        </html>
                        """

            st.subheader('FX Latest Cross Rates')
            
            components.html(FX_chart, height=500, scrolling=False)

        with col2:
            FX_chart = """
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
                                    justify-content: centre;
                                    align-items: centre;
                                    height: 100vh;
                                }

                                .container {
                                    width: 90%;
                                    max-width: 800px; /* Adjust max-width as per your design */
                                    text-align: centre;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <!-- TradingView Widget BEGIN -->
                            <div class="tradingview-widget-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text"></span></a></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
                            {
                            "width": "100%",
                            "height": "100%",
                            "currencies": [
                                "EUR",
                                "USD",
                                "JPY",
                                "GBP",
                                "CAD",
                                "MYR"
                            ],
                            "isTransparent": false,
                            "colorTheme": "dark",
                            "locale": "en",
                            "backgroundColor": "rgba(0, 0, 0, 1)"
                            }
                            </script>
                            </div>
                            <!-- TradingView Widget END -->

                            </div>
                        </body>
                        </html>
                        """

            st.subheader('FX Daily Percentage Change')
            components.html(FX_chart, height=500, scrolling=False)

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
            correlation_matrix = data.corr().round(2)
            
            # Plot the heatmap using Plotly
            fig = px.imshow(correlation_matrix, 
                            text_auto=True, 
                            aspect="auto", 
                            color_continuous_scale='RdBu',
                            labels={'color': 'Correlation Coefficient'},
                            title=f'Correlation Matrix of FX Pairs ({period} Data)',zmin=-1, zmax=1)
            
            # Update the hover template to display the correlation value rounded to 2 decimal places
            fig.update_traces(hovertemplate='Value: %{z:.2f}')
            
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Streamlit app layout
        st.subheader('Correlation Matrix of FX Pairs')

        st.write('''
            This section presents a heatmap displaying the correlation between major FX and Brent Crude Oil prices over different time periods. 
            The results are displayed using a color-coded heatmap, with correlation coefficients ranging from -1(red) to 1(blue).
            ''')

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
        st.subheader('Time Series of DXY and Brent')

        st.write('''
            This section presents both the time series and the rolling 1-year correlation between Brent crude oil prices and the DXY (U.S. Dollar Index).
                 
            **Key Observations**:
            - **Traditional Correlation**: Historically, a strong inverse correlation existed between Brent crude oil prices and the DXY index—when the dollar strengthened, oil prices typically fell, and vice versa.
            - **Evolving Dynamics**: The rolling correlation plot indicates that this traditional relationship has become less predictable.
            - **Complex Interactions**: The current correlation reflects increased complexity due to various factors impacting the oil market, suggesting that simple historical patterns are no longer as applicable.
            ''')

        # Plot time series and rolling correlation
        plot_time_series()
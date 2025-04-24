import streamlit as st
import datetime
import yfinance as yf
import numpy as np
import plotly.express as px
from scipy.stats import norm
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components



def technical_probability_page():

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


    st.header("Technical and Probability Analysis")

    

    tab1,tab2,tab3 = st.tabs(['Technical Analysis','MonteCarlo Analysis (Daily)','MonteCarlo Analysis (Monthly)'])

    with tab1:
        st.subheader("TradingView Technical Analysis")

        st.write(
            """
            In this section, we have integrated a TradingView advanced chart widget to provide you with a comprehensive technical analysis of Brent crude oil prices. 
            This interactive chart allows you to visualize price movements and apply various technical indicators by hovering over the name of the commodity and clicking the triple dots, aiding in better analysis and decision-making."""
            )

        Brent_chart_Pivot = """
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
                        max-width: 1200px; /* Adjust max-width as per your design */
                        text-align: centre;
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
                "allow_symbol_change": false,
                "calendar": false,
                "studies": [
                    "STD;Pivot%1Points%1Standard"
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
                        justify-content: centre;
                        align-items: centre;
                        height: 100vh;
                    }

                    .container {
                        width: 90%;
                        max-width: 1200px; /* Adjust max-width as per your design */
                        text-align: centre;
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
                    "range":"5D",
                    "timezone": "Asia/Kuala_Lumpur",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "hide_top_toolbar": true,
                    "allow_symbol_change": false,
                    "calendar": false,
                    "studies": [
                        "STD;MACD",
                        "STD;RSI"
            
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
        st.subheader("Daily Price with Pivot Points Indicator (Broker Quoted)")
        st.write(
        """
        The latest broker quoted Brent daily price data, sourced from TradingView, with a difference of USD 0.40 to USD 0.60 compared to the actual ICE Brent price.. The chart includes "Pivot Points," which are commonly used to identify potential support and resistance levels based on historical price data. Pivot points are calculated using the previous period's high, low, and close prices. If the price is trading above the main pivot point, it is generally considered to indicate bullish sentiment, while a price trading below the pivot point suggests bearish sentiment.

        Additionally, traders often look at the first, second, and third support (S1, S2, S3) and resistance levels (R1, R2, R3) derived from pivot points. These levels can serve as potential price targets or areas where reversals may occur. For instance, if the price approaches a resistance level and fails to break through, it may signal a reversal to the downside. Similarly, if the price finds support at a pivot level and holds, it may indicate a potential upward movement.
        """
        )
        components.html(Brent_chart_Pivot, height=800, scrolling=False)
        st.divider()
        st.subheader("Intraday Price with RSI & MACD Indicator (Broker Quoted)")
        st.write(
            """
            The chart includes the "RSI (Relative Strength Index)" and "MACD (Moving Average Convergence Divergence)" studies, which help identify potential market trends and momentum based on historical price data. Typically, if the RSI is above 50 and the MACD is above zero, the asset is considered to have positive momentum, while an RSI below 50 and a MACD below zero indicate negative momentum. However, it's also important to look for RSI divergence, 
            which can signal a potential reversal despite the current momentum.
            """
            )
        components.html(Brent_chart, height=800, scrolling=False)
        # Use the font with right-aligned text
        st.markdown("<p class='left-align'>Source: TradingView</p>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Monte Carlo (Daily Prices)")

        st.write(
            """
            **Predicting Oil Prices with Monte Carlo Simulation**

            Monte Carlo simulation is a method used to estimate the future price of oil by considering various factors that influence its value. It's like guessing the possible outcomes of a game by rolling dice multiple times.

            ### How Does it Work?

            1. **Understanding Oil Prices**: While oil prices are influenced by factors such as supply, demand, geopolitical events, and economic conditions, Monte Carlo simulation does not require direct input of these factors. Instead, it uses statistical properties such as historical price distributions and volatility.

            2. **Simulating Scenarios**: The simulation generates thousands of possible future scenarios for oil prices by applying random variations to the historical price data. This process creates a diverse set of potential future price paths.

            3. **Calculating Probabilities**: Each scenario represents a possible outcome, and the simulation calculates the likelihood of each scenario occurring.

            4. **Analyzing Results**: By analyzing the range of possible outcomes and their probabilities, we can understand the potential risks and make informed decisions about oil-related strategies.
            """
            )
        
        st.divider()

        # Inputs for the simulation
        today = datetime.date.today()
        end_date = st.date_input("Select current date", today - datetime.timedelta(days=1), max_value=today - datetime.timedelta(days=1), key="end_date_input")
        future_end_date = st.date_input("Select forecast date", datetime.date(2025, 12, 31), min_value= end_date + datetime.timedelta(days=1), key="future_date_input")
        # Streamlit slider for selecting the number of years of historical data
        years_of_data = st.slider('Select number of years of historical data:', min_value=1, max_value=10, value=10, key="years_of_data_2") 

        run_simulation = st.button("Run Simulation", key="RUN")

        

        if run_simulation:
            start_date = pd.Timestamp(end_date) - pd.DateOffset(years=years_of_data)
            brent_data = yf.download('BZ=F', start=start_date, end=pd.Timestamp(end_date) + pd.Timedelta(days=1))

            # Extract the 'Close' prices
            new_data = brent_data['Close']

            # Historical log returns
            log_returns = np.log(1 + new_data.pct_change())

            # Drift = Average Daily Return − (Variance / 2)
            u = log_returns.mean()
            var = log_returns.var()
            drift = float(u - (0.5 * var))  # Convert to float scalar

            # Standard deviation of historic log returns
            stdev = float(log_returns.std())  # Convert to float scalar

            # Price predictions for the specified future period with iterations
            last_date = new_data.index[-1]
            t_intervals = (pd.Timestamp(future_end_date) - last_date).days
            iterations = 10000
            daily_returns = np.exp(drift + stdev * norm.ppf(np.random.rand(t_intervals, iterations)))

            # Initial stock price
            S0 = new_data.iloc[-1]
            price_list = np.zeros_like(daily_returns)
            price_list[0] = S0

            # Simulate price series
            for t in range(1, t_intervals):
                price_list[t] = price_list[t - 1] * daily_returns[t]

            # Calculate daily, monthly, and annual volatility
            daily_volatility = log_returns.std()
            trading_days_per_month = 21  # Assuming 21 trading days in a month
            monthly_volatility = daily_volatility * np.sqrt(trading_days_per_month)
            trading_days_per_year = 252  # Assuming 252 trading days in a year
            annual_volatility = daily_volatility * np.sqrt(trading_days_per_year)

            # Calculate VaR
            confidence_level = 0.05  # 5% confidence level
            var = np.percentile(price_list, confidence_level * 100)

            # Calculate VaR
            confidence_level_3 = 0.01  # 1% confidence level
            var_3 = np.percentile(price_list, confidence_level_3 * 100)

            confidence_level_2 = 0.95  # 95% confidence level
            var_2 = np.percentile(price_list, confidence_level_2 * 100)

            confidence_level_4 = 0.99  # 95% confidence level
            var_4 = np.percentile(price_list, confidence_level_4 * 100)

            st.subheader("Simulation Details & Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.divider()
                st.metric(label="Current Closing Price", value=round(S0, 2))
                st.metric(label="Number of Iterations", value=iterations)
                st.metric(label="Forecasted Period", value=future_end_date.strftime('%Y-%m-%d') + f" ({t_intervals} days)")
                st.metric(label="Expected Average Price", value=round(np.mean(price_list), 2))
                @st.cache_data
                def convert_df(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv().encode("utf-8")

                # Reverse the DataFrame
                reversed_data = new_data[::-1]
                csv = convert_df(reversed_data)

                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="Brent_Price.csv",
                    mime="text/csv",
    )


            with col2:
                st.divider()
                st.metric(label="Daily Volatility", value=f"{round(daily_volatility * 100, 2)}%")
                st.metric(label="Monthly Volatility (21 trading days)", value=f"{round(monthly_volatility * 100, 2)}%")
                st.metric(label="Annual Volatility (252 trading days)", value=f"{round(annual_volatility * 100, 2)}%")

            with col3:
                st.divider()
                st.metric(label="Quantile (30%)", value=round(np.percentile(price_list, 30), 2))
                st.metric(label="Quantile (80%)", value=round(np.percentile(price_list, 80), 2))
                st.metric(label=f"1% confidence level", value=round(var_3, 2))
                st.metric(label=f"5% confidence level", value=round(var, 2))
                st.metric(label=f"95% confidence level", value=round(var_2, 2))
                st.metric(label=f"99% confidence level", value=round(var_4, 2))
            
            #############################################
            col4, col5 = st.columns(2)
            ##############################

            with col4:
                st.subheader("Monte Carlo Simulation of Brent Oil Prices - Histogram")
                fig = px.histogram(price_list[-1], nbins=500, title='Distribution of Final Prices from Monte Carlo Simulation',
                                labels={'value': 'Price', 'count': 'Frequency'})
                fig.update_layout(
                    xaxis_title='Price',
                    yaxis_title='Frequency',
                    bargap=0.2,
                    template='plotly_dark'
                )
                
                # Add lines for mean and median
                mean_price = np.mean(price_list[-1])
                fig.add_vline(x=mean_price, line_dash="dash", line_color="black", annotation_text="Mean", annotation_position="bottom")

                Q30 =  round(np.percentile(price_list, 30), 2)
                Q80 =  round(np.percentile(price_list, 80), 2)
                
                # Add annotations for VaR
                fig.add_vline(x=Q30, line_dash="dash", line_color="red", annotation_text="Q30", annotation_position="top")
                fig.add_vline(x=Q80, line_dash="dash", line_color="orange", annotation_text="Q80", annotation_position="top")
                
                st.plotly_chart(fig)

                st.subheader("Monte Carlo Simulation of Brent Oil Prices - Key Paths")
                mean_path = np.mean(price_list, axis=1)

                percentile_30_path = np.percentile(price_list, 30, axis=1)
                percentile_80_path = np.percentile(price_list, 80, axis=1)

                fig_key_paths = px.line(title='Monte Carlo Simulation Key Paths', labels={'index': 'Days', 'value': 'Price'})
                fig_key_paths.add_scatter(x=list(range(t_intervals)), y=mean_path, mode='lines', name='Mean Path', line=dict(color='blue'))
                fig_key_paths.add_scatter(x=list(range(t_intervals)), y=percentile_30_path, mode='lines', name='P30', line=dict(color='red', dash='dash'))
                fig_key_paths.add_scatter(x=list(range(t_intervals)), y=percentile_80_path, mode='lines', name='P80', line=dict(color='orange', dash='dash'))

                fig_key_paths.update_layout(template='plotly_dark')
                st.plotly_chart(fig_key_paths)

            ############################################
            with col5:
                st.subheader("Historical Brent Oil Prices and Rolling Historical Volatility")
                fig_combined = go.Figure()
                rolling_volatility = log_returns.rolling(window=252).std() * np.sqrt(252)

                # Add Brent oil prices to the graph
                fig_combined.add_trace(go.Scatter(x=new_data.index, y=new_data.values, mode='lines', name='Brent Oil Prices', line=dict(color='blue')))

                # Create a second y-axis for the volatility
                fig_combined.update_layout(yaxis=dict(title="Brent Oil Prices"), yaxis2=dict(title="Volatility", overlaying="y", side="right"))

                # Add rolling historical volatility to the graph
                fig_combined.add_trace(go.Scatter(x=rolling_volatility.index, y=rolling_volatility.values, mode='lines', name='Rolling Volatility', line=dict(color='red'), yaxis='y2'))

                fig_combined.update_layout(title="Historical Brent Oil Prices and Rolling Historical Volatility", template='plotly_dark')
                st.plotly_chart(fig_combined)
                


            ############################################

    with tab3:
        st.subheader("Monte Carlo (Monthly Average Prices)")

        st.write(
            """
            **Predicting Oil Prices with Monte Carlo Simulation (Monthly Average)**

            Similar to the the daily Monte Carlo Analysis, it uses historical price to predict possible future scenarios but uses average historical price of every month instead of daily historical price. This will typically lead to lower volatility and a smaller Monte Carlo band. 
            """
            )



        # Inputs for the simulation
        today = datetime.date.today()
        end_date = st.date_input("Select current date", today - datetime.timedelta(days=1), max_value=today - datetime.timedelta(days=1), key="end_date_input_2")
        future_end_date = st.date_input("Select forecast date", datetime.date(2025, 12, 31), min_value= end_date + datetime.timedelta(days=1), key="future_date_input_2")
        # Streamlit slider for selecting the number of years of historical data
        years_of_data = st.slider('Select number of years of historical data:', min_value=1, max_value=10, value=10, key="years_of_data") 

        run_simulation = st.button("Run Simulation", key="RUN_2")

        

        if run_simulation:
            start_date = pd.Timestamp(end_date) - pd.DateOffset(years=years_of_data)
            brent_data = yf.download('BZ=F', start=start_date, end=pd.Timestamp(end_date) + pd.Timedelta(days=1))

            # Extract the 'Close' prices
            new_data = brent_data['Close']
            # Resample the data to get monthly closing prices
            monthly_data = brent_data['Close'].resample('M').last()

            # Historical monthly log returns
            log_returns_monthly = np.log(1 + monthly_data.pct_change())

            # Drift = Average Monthly Return − (Variance / 2)
            u_monthly = log_returns_monthly.mean()
            var_monthly = log_returns_monthly.var()
            drift_monthly = u_monthly - (0.5 * var_monthly)

            # Standard deviation of historical monthly log returns
            stdev_monthly = log_returns_monthly.std()           

            # Price predictions for the specified future period with iterations
            last_date = monthly_data.index[-1]
            # Assuming last_date is a datetime.date object
            last_date_timestamp = pd.Timestamp(last_date)

            # Convert future_end_date to Timestamp
            future_end_date_timestamp = pd.Timestamp(future_end_date)

            # Then perform the subtraction
            t_intervals_monthly = (future_end_date_timestamp - last_date_timestamp).days // 30
            iterations = 10000
            monthly_returns = np.exp(drift_monthly + stdev_monthly * norm.ppf(np.random.rand(t_intervals_monthly, iterations)))

            # Initial stock price
            S0 = monthly_data.iloc[-1]
            price_list_monthly = np.zeros_like(monthly_returns)
            price_list_monthly[0] = S0

            # Simulate price series
            for t in range(1, t_intervals_monthly):
                price_list_monthly[t] = price_list_monthly[t - 1] * monthly_returns[t]

            # Calculate monthly and annual volatility
            monthly_volatility = stdev_monthly
            trading_months_per_year = 12  # 12 months in a year
            annual_volatility = monthly_volatility * np.sqrt(trading_months_per_year)

            # Calculate VaR
            confidence_level = 0.05  # 5% confidence level
            var = np.percentile(price_list_monthly, confidence_level * 100)

            # Calculate VaR
            confidence_level_3 = 0.01  # 1% confidence level
            var_3 = np.percentile(price_list_monthly, confidence_level_3 * 100)

            confidence_level_2 = 0.95  # 95% confidence level
            var_2 = np.percentile(price_list_monthly, confidence_level_2 * 100)

            confidence_level_4 = 0.99  # 95% confidence level
            var_4 = np.percentile(price_list_monthly, confidence_level_4 * 100)

            st.subheader("Simulation Details & Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.divider()
                st.metric(label="Current Closing Price", value=round(S0, 2))
                st.metric(label="Number of Iterations", value=iterations)
                st.metric(label="Forecasted Period", value=future_end_date.strftime('%Y-%m-%d') + f" ({t_intervals_monthly} Months)")
                st.metric(label="Expected Average Price", value=round(np.mean(price_list_monthly), 2))
                @st.cache_data
                def convert_df(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv().encode("utf-8")

                # Reverse the DataFrame
                reversed_data = new_data[::-1]
                csv = convert_df(reversed_data)

                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="Brent_Price.csv",
                    mime="text/csv",
    )


            with col2:
                st.divider()
                st.metric(label="Monthly Volatility (21 trading days)", value=f"{round(monthly_volatility * 100, 2)}%")
                st.metric(label="Annual Volatility (252 trading days)", value=f"{round(annual_volatility * 100, 2)}%")

            with col3:
                st.divider()
                st.metric(label="Quantile (30%)", value=round(np.percentile(price_list_monthly, 30), 2))
                st.metric(label="Quantile (80%)", value=round(np.percentile(price_list_monthly, 80), 2))
                st.metric(label=f"1% confidence level", value=round(var_3, 2))
                st.metric(label=f"5% confidence level", value=round(var, 2))
                st.metric(label=f"95% confidence level", value=round(var_2, 2))
                st.metric(label=f"99% confidence level", value=round(var_4, 2))
            
            #############################################
            col4, col5 = st.columns(2)
            ##############################

            with col4:
                st.subheader("Monte Carlo Simulation of Brent Oil Prices - Histogram")
                fig = px.histogram(price_list_monthly[-1], nbins=500, title='Distribution of Final Prices from Monthly Average Monte Carlo Simulation',
                                labels={'value': 'Price', 'count': 'Frequency'})
                fig.update_layout(
                    xaxis_title='Price',
                    yaxis_title='Frequency',
                    bargap=0.2,
                    template='plotly_dark'
                )
                
                # Add lines for mean and median
                mean_price = np.mean(price_list_monthly[-1])
                fig.add_vline(x=mean_price, line_dash="dash", line_color="black", annotation_text="Mean", annotation_position="bottom")

                Q30 =  round(np.percentile(price_list_monthly, 30), 2)
                Q80 =  round(np.percentile(price_list_monthly, 80), 2)
                
                # Add annotations for VaR
                fig.add_vline(x=Q30, line_dash="dash", line_color="red", annotation_text="Q30", annotation_position="top")
                fig.add_vline(x=Q80, line_dash="dash", line_color="orange", annotation_text="Q80", annotation_position="top")
                
                st.plotly_chart(fig)

                st.subheader("Monte Carlo Simulation of Brent Oil Prices for Monthly Average - Key Paths")
                mean_path = np.mean(price_list_monthly, axis=1)

                percentile_30_path = np.percentile(price_list_monthly, 30, axis=1)
                percentile_80_path = np.percentile(price_list_monthly, 80, axis=1)

                fig_key_paths = px.line(title='Monte Carlo Simulation Key Paths', labels={'index': 'Days', 'value': 'Price'})
                fig_key_paths.add_scatter(x=list(range(t_intervals_monthly)), y=mean_path, mode='lines', name='Mean Path', line=dict(color='blue'))
                fig_key_paths.add_scatter(x=list(range(t_intervals_monthly)), y=percentile_30_path, mode='lines', name='P30', line=dict(color='red', dash='dash'))
                fig_key_paths.add_scatter(x=list(range(t_intervals_monthly)), y=percentile_80_path, mode='lines', name='P80', line=dict(color='orange', dash='dash'))

                fig_key_paths.update_layout(template='plotly_dark')
                st.plotly_chart(fig_key_paths)

            ############################################
            with col5:
                st.subheader("Historical Brent Oil Prices and Rolling Historical Volatility")
                fig_combined = go.Figure()
                rolling_volatility = log_returns_monthly.rolling(window=1).std() * np.sqrt(252)

                # Add Brent oil prices to the graph
                fig_combined.add_trace(go.Scatter(x=new_data.index, y=new_data.values, mode='lines', name='Brent Oil Prices', line=dict(color='blue')))

                # Create a second y-axis for the volatility
                fig_combined.update_layout(yaxis=dict(title="Brent Oil Prices"), yaxis2=dict(title="Volatility", overlaying="y", side="right"))

                # Add rolling historical volatility to the graph
                fig_combined.add_trace(go.Scatter(x=rolling_volatility.index, y=rolling_volatility.values, mode='lines', name='Rolling Volatility', line=dict(color='red'), yaxis='y2'))

                fig_combined.update_layout(title="Historical Brent Oil Prices and Rolling Historical Volatility", template='plotly_dark')
                st.plotly_chart(fig_combined)
                


            ############################################


import streamlit as st
import datetime
import yfinance as yf
import numpy as np
import plotly.express as px
from scipy.stats import norm
import pandas as pd
import plotly.graph_objects as go

# Markdown content explaining Monte Carlo simulation
monte_carlo_explanation = """
## Predicting Oil Prices with Monte Carlo Simulation

Monte Carlo simulation is a method used to estimate the future price of oil by considering various factors that influence its value. It's like guessing the possible outcomes of a game by rolling dice multiple times.

### How Does it Work?

1. **Understanding Oil Prices**: Oil prices are influenced by factors like supply, demand, geopolitical events, and economic conditions. Monte Carlo simulation models these factors to predict future prices.

2. **Simulating Scenarios**: Using historical data, the simulation generates thousands of possible future scenarios for oil prices based on random variations in these factors.

3. **Calculating Probabilities**: Each scenario represents a possible outcome, and the simulation calculates the likelihood of each scenario occurring.

4. **Analyzing Results**: By analyzing the range of possible outcomes and their probabilities, we can understand the potential risks and make informed decisions about oil-related strategies.

"""

def technical_probability_page():
    st.header("Technical and Probability Analysis",help= monte_carlo_explanation)

    

    # Inputs for the simulation
    today = datetime.date.today()
    end_date = st.date_input("Select current date", today - datetime.timedelta(days=1), max_value=today - datetime.timedelta(days=1))
    future_end_date = st.date_input("Select future end date", datetime.date(2024, 12, 31), min_value= end_date + datetime.timedelta(days=1))
    # Streamlit slider for selecting the number of years of historical data
    years_of_data = st.slider('Select number of years of historical data:', min_value=1, max_value=10, value=10) 

    run_simulation = st.button("Run Simulation")

       

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
        drift = u - (0.5 * var)

        # Standard deviation of historic log returns
        stdev = log_returns.std()

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
            st.metric(label=f"Lower VaR (1% confidence level)", value=round(var_3, 2))
            st.metric(label=f"Lower VaR (5% confidence level)", value=round(var, 2))
            st.metric(label=f"Upper VaR (95% confidence level)", value=round(var_2, 2))
            st.metric(label=f"Upper VaR (99% confidence level)", value=round(var_4, 2))
        
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


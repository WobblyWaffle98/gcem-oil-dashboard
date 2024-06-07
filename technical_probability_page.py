import streamlit as st
import datetime
import yfinance as yf
import numpy as np
import plotly.express as px
from scipy.stats import norm
import pandas as pd

def technical_probability_page():
    st.header("Technical and Probability Analysis")
    # Inputs for the simulation
    today = datetime.date.today()
    end_date = st.date_input("Select end date", today - datetime.timedelta(days=1), max_value=today - datetime.timedelta(days=1))
    future_end_date = st.date_input("Select future end date", datetime.date(2024, 12, 31), min_value= end_date + datetime.timedelta(days=1))
    run_simulation = st.button("Run Simulation")

    if run_simulation:
        start_date = pd.Timestamp(end_date) - pd.DateOffset(years=10)
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
        iterations = 1000
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

        # Display the forecast results and volatilities
        st.subheader("Forecast Results")
        st.write(f"Current Closing price: {round(S0, 2)}")
        st.write(f"Number of iterations: {iterations}")
        st.write(f"Forecasted period: {future_end_date.strftime('%Y-%m-%d')} consisting of {t_intervals} days")
        st.write(f"Expected average price: {round(np.mean(price_list), 2)}")
        st.write(f"Quantile (30%): {round(np.percentile(price_list, 30), 2)}")
        st.write(f"Quantile (80%): {round(np.percentile(price_list, 80), 2)}")

        st.subheader("Volatilities")
        st.write(f"Daily Volatility: {round(daily_volatility * 100, 2)}%")
        st.write(f"Monthly Volatility (21 trading days): {round(monthly_volatility * 100, 2)}%")
        st.write(f"Annual Volatility (252 trading days): {round(annual_volatility * 100, 2)}%")

        st.subheader("Value at Risk (VaR)")
        st.write(f"Lower Value at Risk (VaR) at {round(confidence_level * 100)}% confidence level: {round(var, 2)}")
        st.write(f"Upper Value at Risk (VaR) at {round(confidence_level_3 * 100)}% confidence level: {round(var_3, 2)}")
        st.write(f"Upper Value at Risk (VaR) at {round(confidence_level_2 * 100)}% confidence level: {round(var_2, 2)}")
        

        st.subheader("Monte Carlo Simulation of Brent Oil Prices - Histogram")
        fig = px.histogram(price_list[-1], nbins=50, title='Distribution of Final Prices from Monte Carlo Simulation')
        fig.update_layout(xaxis_title='Price', yaxis_title='Frequency')
        st.plotly_chart(fig)

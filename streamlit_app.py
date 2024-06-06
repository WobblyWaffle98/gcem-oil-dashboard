import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
from scipy.stats import norm

# Sample data generation
def generate_sample_data():
    dates = pd.date_range(start="2023-01-01", periods=100)
    data = {
        "Price": np.random.rand(100) * 100,
        "Production": np.random.rand(100) * 1000,
        "Consumption": np.random.rand(100) * 800,
        "GDP": np.random.rand(100) * 20,
        "Interest Rate": np.random.rand(100) * 5,
        "Stock Market Index": np.random.rand(100) * 3000,
        "Technical Indicator": np.random.rand(100) * 100,
    }
    return pd.DataFrame(data, index=dates)

# Generate sample data
df = generate_sample_data()

# Streamlit app layout
st.set_page_config(page_title="Oil Indicator Dashboard", layout="wide")

# Styling
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .block-container {
        padding: 1rem 2rem;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .css-1d391kg {
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Oil Indicator Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main", "Macro-economic", "Fundamentals", "Financial Markets", "Technical and Probability Analysis"])

# Main Page
if page == "Main":
    st.header("Main Dashboard")
    fig = px.line(df, x=df.index, y="Price", title="Oil Price Over Time")
    st.plotly_chart(fig)
    st.write(df.describe())

# Macro-economic Page
elif page == "Macro-economic":
    st.header("Macro-economic Indicators")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["GDP"], mode='lines', name='GDP'))
    fig.add_trace(go.Scatter(x=df.index, y=df["Interest Rate"], mode='lines', name='Interest Rate'))
    fig.update_layout(title="Macro-economic Indicators Over Time", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig)
    st.write(df[["GDP", "Interest Rate"]].describe())

# Fundamentals Page
elif page == "Fundamentals":
    st.header("Fundamental Indicators")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Production"], mode='lines', name='Production'))
    fig.add_trace(go.Scatter(x=df.index, y=df["Consumption"], mode='lines', name='Consumption'))
    fig.update_layout(title="Fundamental Indicators Over Time", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig)
    st.write(df[["Production", "Consumption"]].describe())

# Financial Markets Page
elif page == "Financial Markets":
    st.header("Financial Market Indicators")
    fig = px.line(df, x=df.index, y="Stock Market Index", title="Stock Market Index Over Time")
    st.plotly_chart(fig)
    st.write(df["Stock Market Index"].describe())

# Technical and Probability Analysis Page
elif page == "Technical and Probability Analysis":
    st.header("Technical and Probability Analysis")
    # Inputs for the simulation
    today = datetime.date.today()
    end_date = st.date_input("Select end date", today - datetime.timedelta(days=1), max_value=today - datetime.timedelta(days=1))
    future_end_date = st.date_input("Select future end date", datetime.date(2024, 12, 31))
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
        confidence_level = 0.05  # 95% confidence level
        var = np.percentile(price_list, confidence_level * 100)

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
        st.write(f"Upper Value at Risk (VaR) at {round(confidence_level_2 * 100)}% confidence level: {round(var_2, 2)}")


        st.subheader("Monte Carlo Simulation of Brent Oil Prices - Histogram")
        final_prices = price_list[-1]
        quantile_30 = np.percentile(final_prices, 30)
        quantile_80 = np.percentile(final_prices, 80)

        fig = px.histogram(final_prices, nbins=50, title='Distribution of Final Prices from Monte Carlo Simulation')
        fig.update_layout(xaxis_title='Price', yaxis_title='Frequency')

        # Add quantile lines
        fig.add_shape(
            type="line",
            x0=quantile_30,
            y0=0,
            x1=quantile_30,
            y1=max(fig.data[0]['y']),
            line=dict(color="red", width=2, dash="dash"),
        )
        fig.add_shape(
            type="line",
            x0=quantile_80,
            y0=0,
            x1=quantile_80,
            y1=max(fig.data[0]['y']),
            line=dict(color="green", width=2, dash="dash"),
        )

        # Add quantile annotations
        fig.add_annotation(
            x=quantile_30,
            y=max(fig.data[0]['y']),
            text="30% Quantile",
            showarrow=True,
            arrowhead=1,
            ax=-40,
            ay=-40,
        )
        fig.add_annotation(
            x=quantile_80,
            y=max(fig.data[0]['y']),
            text="80% Quantile",
            showarrow=True,
            arrowhead=1,
            ax=-40,
            ay=-40,
        )

        st.plotly_chart(fig)
# Run the app

# Run the app
if __name__ == "__main__":
    st.write("This is a Streamlit application.")

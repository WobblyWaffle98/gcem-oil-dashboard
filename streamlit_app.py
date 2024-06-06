import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

st.title("Oil Indicator Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main", "Macro-economic", "Fundamentals", "Financial Markets", "Technical and Probability Analysis"])

# Main Page
if page == "Main":
    st.header("Main Dashboard")
    st.line_chart(df["Price"])
    st.write(df.describe())

# Macro-economic Page
elif page == "Macro-economic":
    st.header("Macro-economic Indicators")
    fig, ax = plt.subplots()
    ax.plot(df.index, df["GDP"], label="GDP")
    ax.plot(df.index, df["Interest Rate"], label="Interest Rate")
    ax.legend()
    st.pyplot(fig)
    st.write(df[["GDP", "Interest Rate"]].describe())

# Fundamentals Page
elif page == "Fundamentals":
    st.header("Fundamental Indicators")
    fig, ax = plt.subplots()
    ax.plot(df.index, df["Production"], label="Production")
    ax.plot(df.index, df["Consumption"], label="Consumption")
    ax.legend()
    st.pyplot(fig)
    st.write(df[["Production", "Consumption"]].describe())

# Financial Markets Page
elif page == "Financial Markets":
    st.header("Financial Market Indicators")
    st.line_chart(df["Stock Market Index"])
    st.write(df["Stock Market Index"].describe())

# Technical and Probability Analysis Page
elif page == "Technical and Probability Analysis":
    st.header("Technical and Probability Analysis")
    st.line_chart(df["Technical Indicator"])
    st.write(df["Technical Indicator"].describe())

# Run the app
if __name__ == "__main__":
    st.write("This is a Streamlit application.")


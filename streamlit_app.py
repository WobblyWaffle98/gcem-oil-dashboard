import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

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
    fig = px.line(df, x=df.index, y="Technical Indicator", title="Technical Indicator Over Time")
    st.plotly_chart(fig)
    st.write(df["Technical Indicator"].describe())

# Run the app
if __name__ == "__main__":
    st.write("This is a Streamlit application.")

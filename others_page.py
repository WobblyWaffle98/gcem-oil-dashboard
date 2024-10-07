import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from io import BytesIO
import plotly.express as px
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from concurrent.futures import ThreadPoolExecutor, as_completed
from plotly.subplots import make_subplots

# Suppress SSL verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def others_page():
    st.subheader("Geopolitical Risk Daily Index")

    st.write("""

    The Measuring Geopolitical Risk index by [Caldara and Iacoviello](https://www.matteoiacoviello.com/gpr_files/GPR_PAPER.pdf) quantifies geopolitical risk using textual analysis of international news. 
    It constructs a numerical index from news articles, capturing factors like conflicts, diplomatic tensions, terrorism, and key geopolitical events.
    The index can be used to calculate or measure risk premium if the index is above certain threshold.
                
    The specific keywords used in the textual analysis to identify geopolitical risk factors might vary, but they likely include terms related to:
                
    1. **Military conflicts** (e.g., war, conflict, aggression)
    2. **Diplomatic tensions** (e.g., sanctions, negotiations, disputes)
    3. **Security threats** (e.g., terrorism, insurgency, cyberattacks)
    4. **Geopolitical events** (e.g., elections, summits, treaties)
    5. **Regional instability** (e.g., regime change, political unrest, civil unrest)
    6. **Economic sanctions and trade disputes** (e.g., tariffs, embargoes, trade wars)
    7. **Natural disasters with potential geopolitical implications** (e.g., pandemics, environmental disasters, resource scarcity)

    """)
    # Suppress SSL verification warnings
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Fetch the data
    url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
    response = requests.get(url, verify=False)

    
    # Read the Excel file directly into a DataFrame using BytesIO
    df = pd.read_excel(BytesIO(response.content), engine='xlrd')
    
    # Ensure the 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Prepare data for plotting
    df_plot = df[['date', 'GPRD']]
    df_plot['GPRD_smoothed'] = df_plot['GPRD'].rolling(window=7).mean()  # 7-day rolling average
    df_plot['GPRD_1yr_rolling_avg'] = df_plot['GPRD'].rolling(window=180).mean()  # 1-year rolling average
    df_plot['Difference'] = df_plot['GPRD_smoothed'] - df_plot['GPRD_1yr_rolling_avg']  # Difference between smoothed and 1-year average

    # Create subplots: two rows, one column
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,  # Adjusts the vertical spacing between the subplots
        subplot_titles=("Geopolitical Risk Index (Smoothed)", "Difference Between 7-Day Rolling Average and 6-Month Rolling Average")
    )

    # Add smoothed GPRD line to the first subplot
    fig.add_trace(go.Scatter(x=df_plot['date'], y=df_plot['GPRD_smoothed'],
                            mode='lines', name='7-Day Rolling Average'),
                row=1, col=1)

    # Add 1-year rolling average line to the first subplot
    fig.add_trace(go.Scatter(x=df_plot['date'], y=df_plot['GPRD_1yr_rolling_avg'],
                            mode='lines', name='6-Months Rolling Average'),
                row=1, col=1)

    # Add markers for oil and gas industry events in the first subplot
    annotations_warattacks = [
        {'date': '1990-08-02', 'event': 'Iraq Invades Kuwait'},
        {'date': '1991-01-17', 'event': 'Start of Gulf War'},
        {'date': '2001-09-11', 'event': '9/11 Attacks'},
        {'date': '2003-03-20', 'event': 'Iraq War Begins'},
        {'date': '2008-08-08', 'event': 'Russo-Georgian War'},
        {'date': '2011-12-17', 'event': 'Arab Spring'},
        {'date': '2014-02-20', 'event': 'Ukraine Crisis'},
        {'date': '2015-11-13', 'event': 'Paris Attacks'},
        {'date': '2020-01-03', 'event': 'Killing of Qasem Soleimani'},
        {'date': '2022-02-24', 'event': 'Russian Invasion of Ukraine'},
        {'date': '2023-10-07', 'event': 'Hamas-Israel Conflict Escalation'}]

    annotations_financials = [
        {'date': '2016-06-23', 'event': 'Brexit Referendum'},
        {'date': '2008-09-15', 'event': 'Lehman Brothers Collapse (Global Financial Crisis)'},]
    
    annotations_others = [{'date': '2002-11-01', 'event': 'SARS Outbreak'},
        {'date': '2010-01-12', 'event': 'Haiti Earthquake'},
        {'date': '2011-03-11', 'event': 'Fukushima Nuclear Disaster'},
        {'date': '2013-12-28', 'event': 'Ebola Outbreak in West Africa'},
        {'date': '2019-12-31', 'event': 'COVID-19 Pandemic'},]

    
    event_dates_war= [pd.to_datetime(event['date']) for event in annotations_warattacks]
    event_labels_war = [event['event'] for event in annotations_warattacks]
    event_values_war = [df_plot[df_plot['date'] == date]['GPRD_smoothed'].values[0] if not df_plot[df_plot['date'] == date].empty else None for date in event_dates_war]

    fig.add_trace(go.Scatter(
        x=event_dates_war,
        y=event_values_war,
        mode='markers',
        marker=dict(size=10, color='red', symbol='circle'),
        hovertext=event_labels_war,
        hoverinfo='text',
        name='War & Attacks Events'
    ), row=1, col=1)

    event_dates_financials= [pd.to_datetime(event['date']) for event in annotations_financials]
    event_labels_financials = [event['event'] for event in annotations_financials]
    event_values_financials = [df_plot[df_plot['date'] == date]['GPRD_smoothed'].values[0] if not df_plot[df_plot['date'] == date].empty else None for date in event_dates_financials]

    fig.add_trace(go.Scatter(
        x=event_dates_financials,
        y=event_values_financials,
        mode='markers',
        marker=dict(size=10, color='green', symbol='circle'),
        hovertext=event_labels_financials,
        hoverinfo='text',
        name='Financial Events'
    ), row=1, col=1)

    event_dates_others= [pd.to_datetime(event['date']) for event in annotations_others]
    event_labels_others = [event['event'] for event in annotations_others]
    event_values_others= [df_plot[df_plot['date'] == date]['GPRD_smoothed'].values[0] if not df_plot[df_plot['date'] == date].empty else None for date in event_dates_others]

    fig.add_trace(go.Scatter(
        x=event_dates_others,
        y=event_values_others,
        mode='markers',
        marker=dict(size=10, color='orange', symbol='circle'),
        hovertext=event_labels_others,
        hoverinfo='text',
        name='Other Events'
    ), row=1, col=1)


    # Add Difference plot to the second subplot
    fig.add_trace(go.Scatter(x=df_plot['date'], y=df_plot['Difference'],
                            mode='lines', name='Difference', line=dict(color='rgba(0, 0, 0, 0)'),
                            fill='tozeroy', fillcolor='rgba(200, 50, 50, 0.3)'),
                row=2, col=1)

    # Update x-axis range (last 3 years)
    three_years_ago = pd.to_datetime('today') - pd.DateOffset(years=3)
    today = pd.to_datetime('today')
    fig.update_xaxes(range=[three_years_ago, today], title_text="Date", row=2, col=1)

    # Update the layout for the entire figure
    fig.update_layout(
        height=800,
        yaxis_title='Index Value',
        yaxis2_title='Difference'
    )

    # Show the combined plot
    fig.show()


    st.divider()
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p class='left-align'>Source: www.matteoiacoviello.com</p>", unsafe_allow_html=True)

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")


    st.download_button(
        label="Download data as CSV",
        data=convert_df(df_plot),
        file_name="GPR.csv",
        mime="text/csv",
        )
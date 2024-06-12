import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from io import BytesIO
import plotly.express as px

help_GPR = """
## Geopolitical Risk index (GPR)

The Measuring Geopolitical Risk index by [Caldara and Iacoviello](https://www.matteoiacoviello.com/gpr_files/GPR_PAPER.pdf) quantifies geopolitical risk using textual analysis of international news. 

It constructs a numerical index from news articles, capturing factors like conflicts, diplomatic tensions, terrorism, and key geopolitical events.

The specific keywords used in the textual analysis to identify geopolitical risk factors might vary, but they likely include terms related to:
    
1. **Military conflicts** (e.g., war, conflict, aggression)
2. **Diplomatic tensions** (e.g., sanctions, negotiations, disputes)
3. **Security threats** (e.g., terrorism, insurgency, cyberattacks)
4. **Geopolitical events** (e.g., elections, summits, treaties)
5. **Regional instability** (e.g., regime change, political unrest, civil unrest)
6. **Economic sanctions and trade disputes** (e.g., tariffs, embargoes, trade wars)
7. **Natural disasters with potential geopolitical implications** (e.g., pandemics, environmental disasters, resource scarcity)

"""

def macro_economic_page():
    st.header("Macro-economic Indicators")
    # Add macro-economic page specific code here

    tab1, tab2, tab3 = st.tabs(['Global data','US Economic data','Geopolitical Risk'],)

    with tab3:
        
        
        

        st.subheader("Geopolitical Risk Daily Index",help = help_GPR)
        # Suppress SSL verification warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Fetch the data
        url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
        response = requests.get(url, verify=False)

        
        # Read the Excel file directly into a DataFrame using BytesIO
        df = pd.read_excel(BytesIO(response.content), engine='xlrd')
        print("DataFrame created successfully.")
        # Print the headers
        print("Headers: ", df.columns.tolist())
        
        # Ensure the 'date' column is in datetime format
        df['date'] = pd.to_datetime(df['date'])
        
        # Select the relevant columns
        columns_to_plot = ['date', 'GPRD']
        df_plot = df[columns_to_plot]
        
        # Apply a rolling average to smooth the data
        df_plot['GPRD_smoothed'] = df_plot['GPRD'].rolling(window=7).mean()  # 7-day rolling average
        
        # Plot using Plotly
        fig = px.line(df_plot, x='date', y=[ 'GPRD_smoothed'],
                    labels={'value': 'Index Value', 'variable': 'Index Type'}, title='Geopolitical Risk Daily Index')
        
        # Add annotations for known geopolitical threats
        annotations = [
            {'date': '1990-08-02', 'event': 'Iraq Invades Kuwait'},
            {'date': '1991-01-17', 'event': 'Start of Gulf War'},
            {'date': '2001-09-11', 'event': '9/11 Attacks'},
            {'date': '2003-03-20', 'event': 'Iraq War Begins'},
            {'date': '2008-08-08', 'event': 'Russo-Georgian War'},
            {'date': '2011-12-17', 'event': 'Arab Spring'},
            {'date': '2014-02-20', 'event': 'Ukraine Crisis'},
            {'date': '2015-11-13', 'event': 'Paris Attacks'},
            {'date': '2016-06-23', 'event': 'Brexit Referendum'},
            {'date': '2020-01-03', 'event': 'Killing of Qasem Soleimani'},
            {'date': '2022-02-24', 'event': 'Russian Invasion of Ukraine'},
            {'date': '2023-10-07', 'event': 'Hamas-Israel Conflict Escalation'},
        ]

        # Convert the annotations to a DataFrame
        df_annotations = pd.DataFrame(annotations)
        df_annotations['date'] = pd.to_datetime(df_annotations['date'])
        
        # Sort the DataFrame by date to ensure annotations are added in chronological order
        df_annotations = df_annotations.sort_values(by='date')

        # Initialize ay value and toggle flag
        ay = 50
        toggle = True

        for _, row in df_annotations.iterrows():
            fig.add_annotation(
                x=row['date'],
                y=df_plot[df_plot['date'] == row['date']]['GPRD'].values[0],
                text=row['event'],
                showarrow=True,
                ax=0,
                ay=ay,
                arrowhead=2,  # Change arrowhead style
                arrowsize=1,  # Adjust arrow size
                font=dict(color="black", size=12),  # Adjust font properties
                bgcolor="lightyellow",  # Set background color
                bordercolor="black",  # Set border color
                borderwidth=1,  # Set border width
            )
            
            # Toggle between 100 and 50 for ay
            if toggle:
                ay = -50
            else:
                ay = 50
            
            # Toggle the flag
            toggle = not toggle


        st.plotly_chart(fig, use_container_width=True)

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



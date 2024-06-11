import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import yfinance as yf
from datetime import datetime
from collections import defaultdict
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta    


def fundamentals_page():
    st.header("Fundamental Indicators")
    # Add fundamentals page specific code here

    tab1, tab3, tab4, tab2, tab5, tab6 = st.tabs(["Balances", "Production", "Consumption","Seasonality", "EIA Inventory","EIA Inventory+"])

    with tab1:
        st.subheader("Supply demand balances")


        def fetch_data(api_url, params):
            try:
                response = requests.get(api_url, params=params, verify=False)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
            except Exception as err:
                print(f"An error occurred: {err}")
            return None

        api_url = 'https://api.eia.gov/v2/steo/data/'
        api_key = 'gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h'

        params_template = {
            "api_key": api_key,
            "frequency": "annual",
            "data[]": "value",
            "start": "2000",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }

        # Define series IDs for world production and consumption
        production_series_id = "PAPR_WORLD"
        consumption_series_id = "PATC_WORLD"

        # Fetch production data
        params_production = params_template.copy()
        params_production["facets[seriesId][]"] = production_series_id
        production_data = fetch_data(api_url, params_production)

        # Fetch consumption data
        params_consumption = params_template.copy()
        params_consumption["facets[seriesId][]"] = consumption_series_id
        consumption_data = fetch_data(api_url, params_consumption)

        # Extract and organize the data
        periods = sorted(list(set(int(item['period']) for item in production_data['response']['data'])))
        production_values = {int(item['period']): float(item['value']) for item in production_data['response']['data']}
        consumption_values = {int(item['period']): float(item['value']) for item in consumption_data['response']['data']}

        # Calculate oversupply/undersupply
        oversupply_undersupply = {year: production_values.get(year, 0) - consumption_values.get(year, 0) for year in periods}

        # Create a DataFrame
        df = pd.DataFrame({
            'Year': periods,
            'Production': [production_values.get(year, 0) for year in periods],
            'Consumption': [consumption_values.get(year, 0) for year in periods],
            'Oversupply/Undersupply': [oversupply_undersupply.get(year, 0) for year in periods]
        })

        # Create the first plot for Production and Consumption
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['Year'], y=df['Production'], mode='lines+markers', name='Production'))
        fig1.add_trace(go.Scatter(x=df['Year'], y=df['Consumption'], mode='lines+markers', name='Consumption'))

        fig1.update_layout(
            title='World Petroleum Production vs Consumption',
            xaxis_title='Year',
            yaxis_title='Volume (million barrels per day)',
            template='plotly_white'
        )

        # Create the second plot for Oversupply/Undersupply
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df['Year'], y=df['Oversupply/Undersupply'], name='Oversupply/Undersupply', 
                            marker_color=df['Oversupply/Undersupply'].apply(lambda x: 'green' if x >= 0 else 'red')))

        fig2.update_layout(
            title='World Petroleum Oversupply/Undersupply',
            xaxis_title='Year',
            yaxis_title='Volume (million barrels per day)',
        )


        col1, col2= st.columns(2)
        # Show the DataFrame and the plots
        with col1:
            st.plotly_chart(fig1)
        
        with col2:
            st.plotly_chart(fig2)



#####################################
    with tab2:
        st.subheader("Seasonality Analysis")

        col1,col2 = st.columns(2)

        # Define the ticker symbol for Brent Crude Oil
        ticker = 'BZ=F'
        
        # Fetch historical data for the last 10 years
        data = yf.download(ticker, start='2014-01-01', end=datetime.now())
        
        # Resample data to end of month to ensure we have monthly data points
        monthly_data = data['Adj Close'].resample('M').last()
        
        # Calculate month-on-month percentage changes
        monthly_pct_change = monthly_data.pct_change() * 100
        
        # Extract month and year from the date index
        monthly_pct_change = monthly_pct_change.to_frame()
        monthly_pct_change['Month'] = monthly_pct_change.index.month
        monthly_pct_change['Year'] = monthly_pct_change.index.year
        
        # Calculate average month-on-month percentage changes
        monthly_avg_pct_change = monthly_pct_change.groupby(['Year', 'Month'])['Adj Close'].mean().unstack()
        
        # Calculate quarter-on-quarter percentage changes
        quarterly_data = monthly_data.resample('Q').last()
        quarterly_pct_change = quarterly_data.pct_change() * 100
        
        # Extract quarter and year from the date index
        quarterly_pct_change = quarterly_pct_change.to_frame()
        quarterly_pct_change['Quarter'] = quarterly_pct_change.index.quarter
        quarterly_pct_change['Year'] = quarterly_pct_change.index.year
        
        # Calculate average quarter-on-quarter percentage changes
        quarterly_avg_pct_change = quarterly_pct_change.groupby(['Year', 'Quarter'])['Adj Close'].mean().unstack()
        with col1:
            # Plotly heatmap for month-on-month change
            fig_monthly = go.Figure(data=go.Heatmap(
                z=monthly_avg_pct_change.values,
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                y=monthly_avg_pct_change.index,
                
                colorscale='RdYlGn',
                colorbar=dict(title='Percentage Change'),
                zmin=-10,  # Adjust according to your data
                zmax=10,   # Adjust according to your data
                hoverongaps=False
            ))

            fig_monthly.update_layout(
                title='Month-on-Month Percentage Change Seasonality of Brent Crude Oil Prices',
                xaxis_title='Month',
                yaxis_title='Year',
            )
            
            st.plotly_chart(fig_monthly)
        with col2:
            # Plotly heatmap for quarter-on-quarter change
            fig_quarterly = go.Figure(data=go.Heatmap(
                z=quarterly_avg_pct_change.values,
                x=['Q1', 'Q2', 'Q3', 'Q4'],
                y=quarterly_avg_pct_change.index,
                colorscale='RdYlGn',
                colorbar=dict(title='Percentage Change'),
                zmin=-10,  # Adjust according to your data
                zmax=10,   # Adjust according to your data
                hoverongaps=False
            ))

            fig_quarterly.update_layout(
                title='Quarter-on-Quarter Percentage Change Seasonality of Brent Crude Oil Prices',
                xaxis_title='Quarter',
                yaxis_title='Year'
            )
            
            st.plotly_chart(fig_quarterly)

        #####################



        st.divider()
        # Streamlit slider for selecting the period
        period = st.slider("Period (in years)", min_value=1, max_value=len(monthly_avg_pct_change), value=12)

        # Function to update the plot based on the selected period
        def update_plot(period):
            # Calculate the number of years
            num_years = len(monthly_avg_pct_change)
            
            # Calculate the start index for the selected period
            start_index = max(0, num_years - period)
            
            # Select the relevant data for the period
            monthly_data_period = monthly_avg_pct_change.iloc[start_index:]
            
            # Calculate the average percentage change for each month across the selected period
            monthly_avg_pct_change_across_years = monthly_data_period.mean(axis=0)
            
            # Define custom color palette
            colors = ['red' if val < 0 else 'green' for val in monthly_avg_pct_change_across_years.values]
            
            # Create Plotly bar chart for average month-on-month change across all years
            fig = go.Figure(data=[
                go.Bar(x=monthly_avg_pct_change_across_years.index, y=monthly_avg_pct_change_across_years.values, marker_color=colors)
            ])
            fig.update_layout(
                title=f'Average Month-on-Month Percentage Change of Brent Crude Oil Prices (Period: {period} years)',
                xaxis_title='Month',
                yaxis_title='Average Percentage Change',
                xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            )
            st.plotly_chart(fig, use_container_width=True)

        # Call the update plot function with the initial period value
        update_plot(period)


#######################################################################
    with tab3:
        st.subheader("Oil Productions")

        # Suppress SSL verification warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        def fetch_data(api_url, params):
            try:
                response = requests.get(api_url, params=params, verify=False)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
            except Exception as err:
                print(f"An error occurred: {err}")
            return None

        api_url = 'https://api.eia.gov/v2/steo/data/'
        api_key = 'gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h'

        params_template = {
            "api_key": api_key,
            "frequency": "annual",
            "data[]": "value",
            "start": "2000",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }

        # Define the series IDs for each component with new names
        series_ids = {
            "OPEC-13 Petroleum Production": ["COPR_OPEC", "OPEC_NC"],
            "Non-OPEC Petroleum Production": ["COPR_NONOPEC", "NONOPEC_NC"]
        }

        # Function to fetch data for multiple series IDs
        def fetch_multiple_series(api_url, params_template, series_ids):
            data = {}
            for category, sub_series in series_ids.items():
                data[category] = {}
                for sub_series_id in sub_series:
                    params = params_template.copy()
                    params["facets[seriesId][]"] = sub_series_id
                    result = fetch_data(api_url, params)
                    if result:
                        data[category][sub_series_id] = result['response']['data']
                    else:
                        print(f"Failed to fetch data for series {sub_series_id}")
            return data

        # Fetch the data
        data = fetch_multiple_series(api_url, params_template, series_ids)

        # Extract and organize the data
        periods = [int(item['period']) for item in data['OPEC-13 Petroleum Production']['COPR_OPEC']]
        opec_crude = [float(item['value']) for item in data['OPEC-13 Petroleum Production']['COPR_OPEC']]
        opec_other_liquids = [float(item['value']) for item in data['OPEC-13 Petroleum Production']['OPEC_NC']]
        nonopec_crude = [float(item['value']) for item in data['Non-OPEC Petroleum Production']['COPR_NONOPEC']]
        nonopec_other_liquids = [float(item['value']) for item in data['Non-OPEC Petroleum Production']['NONOPEC_NC']]

        # Create a DataFrame
        df = pd.DataFrame({
            'Year': periods,
            'OPEC Crude Oil Production': opec_crude,
            'OPEC Other Liquids Production': opec_other_liquids,
            'Non-OPEC Crude Oil Production': nonopec_crude,
            'Non-OPEC Other Liquids Production': nonopec_other_liquids
        })

        # Calculate total values for stacking
        df['OPEC-13 Petroleum Production'] = df['OPEC Crude Oil Production'] + df['OPEC Other Liquids Production']
        df['Non-OPEC Petroleum Production'] = df['Non-OPEC Crude Oil Production'] + df['Non-OPEC Other Liquids Production']
        df['Total Petroleum Production'] = df['OPEC-13 Petroleum Production'] + df['Non-OPEC Petroleum Production']

        # Create a stacked bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Year'], y=df['OPEC Crude Oil Production'], name='OPEC Crude Oil Production'))
        fig.add_trace(go.Bar(x=df['Year'], y=df['OPEC Other Liquids Production'], name='OPEC Other Liquids Production'))
        fig.add_trace(go.Bar(x=df['Year'], y=df['Non-OPEC Crude Oil Production'], name='Non-OPEC Crude Oil Production'))
        fig.add_trace(go.Bar(x=df['Year'], y=df['Non-OPEC Other Liquids Production'], name='Non-OPEC Other Liquids Production'))

        fig.update_layout(
            title='World Petroleum and Other Liquid Production Components',
            xaxis_title='Year',
            yaxis_title='Volume (million barrels per day)',
            barmode='stack',
            
        )

        st.plotly_chart(fig, use_container_width=True)

        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")


        st.download_button(
            label="Download data as CSV",
            data=convert_df(df),
            file_name="OilAnnualProduction.csv",
            mime="text/csv",
            )


##################################################
    with tab4:
        st.subheader("Oil Consumptions")
        # Suppress SSL verification warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        def fetch_data(api_url, params):
            try:
                response = requests.get(api_url, params=params, verify=False)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as err:
                print(f"HTTP error occurred: {err}")
            except Exception as err:
                print(f"An error occurred: {err}")
            return None

        api_url = 'https://api.eia.gov/v2/steo/data/'
        api_key = 'gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h'

        params_template = {
            "api_key": api_key,
            "frequency": "annual",
            "data[]": "value",
            "start": "2000",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }

        # Define the series IDs for each component with new names
        series_ids = {
            "Total OECD Petroleum Consumption": ["PATC_CA", "PATC_OECD_EUROPE", "PATC_JA", "PATC_US", "PATC_UST", "PATC_OTHER_OECD"],
            "Total non-OECD Petroleum Consumption": ["PATC_CH", "PATC_FSU", "PATC_NONOECD_EUROPE", "PATC_OTHER_ASIA", "PATC_OTHER_NONOECD"]
        }

        # Function to fetch data for multiple series IDs
        def fetch_multiple_series(api_url, params_template, series_ids):
            data = {}
            for category, sub_series in series_ids.items():
                data[category] = {}
                for sub_series_id in sub_series:
                    params = params_template.copy()
                    params["facets[seriesId][]"] = sub_series_id
                    result = fetch_data(api_url, params)
                    if result:
                        data[category][sub_series_id] = result['response']['data']
                    else:
                        print(f"Failed to fetch data for series {sub_series_id}")
            return data

        # Fetch the data
        data = fetch_multiple_series(api_url, params_template, series_ids)

        # Extract and organize the data
        periods = [int(item['period']) for item in next(iter(data['Total OECD Petroleum Consumption'].values()))]

        # Extract sub-component data
        canada_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_CA']]
        europe_oecd_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_OECD_EUROPE']]
        japan_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_JA']]
        us_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_US']]
        us_territories_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_UST']]
        other_oecd_consumption = [float(item['value']) for item in data['Total OECD Petroleum Consumption']['PATC_OTHER_OECD']]

        china_consumption = [float(item['value']) for item in data['Total non-OECD Petroleum Consumption']['PATC_CH']]
        eurasia_consumption = [float(item['value']) for item in data['Total non-OECD Petroleum Consumption']['PATC_FSU']]
        europe_nonoecd_consumption = [float(item['value']) for item in data['Total non-OECD Petroleum Consumption']['PATC_NONOECD_EUROPE']]
        other_asia_consumption = [float(item['value']) for item in data['Total non-OECD Petroleum Consumption']['PATC_OTHER_ASIA']]
        other_nonoecd_consumption = [float(item['value']) for item in data['Total non-OECD Petroleum Consumption']['PATC_OTHER_NONOECD']]

        # Create a DataFrame
        df_annual_consumption = pd.DataFrame({
            'Year': periods,
            'Canada Petroleum Consumption': canada_consumption,
            'Europe OECD Petroleum Consumption': europe_oecd_consumption,
            'Japan Petroleum Consumption': japan_consumption,
            'United States Petroleum Consumption': us_consumption,
            'U.S. Territories Petroleum Consumption': us_territories_consumption,
            'Other OECD Petroleum Consumption': other_oecd_consumption,
            'China Petroleum Consumption': china_consumption,
            'Eurasia Petroleum Consumption': eurasia_consumption,
            'Europe non-OECD Petroleum Consumption': europe_nonoecd_consumption,
            'Other Asia Petroleum Consumption': other_asia_consumption,
            'Other Non-OECD Petroleum Consumption': other_nonoecd_consumption
        })

        # Calculate total values for stacking
        df_annual_consumption['Total OECD Petroleum Consumption'] = (
            df_annual_consumption['Canada Petroleum Consumption'] +
            df_annual_consumption['Europe OECD Petroleum Consumption'] +
            df_annual_consumption['Japan Petroleum Consumption'] +
            df_annual_consumption['United States Petroleum Consumption'] +
            df_annual_consumption['U.S. Territories Petroleum Consumption'] +
            df_annual_consumption['Other OECD Petroleum Consumption']
        )

        df_annual_consumption['Total non-OECD Petroleum Consumption'] = (
            df_annual_consumption['China Petroleum Consumption'] +
            df_annual_consumption['Eurasia Petroleum Consumption'] +
            df_annual_consumption['Europe non-OECD Petroleum Consumption'] +
            df_annual_consumption['Other Asia Petroleum Consumption'] +
            df_annual_consumption['Other Non-OECD Petroleum Consumption']
        )

        df_annual_consumption['Total World Petroleum Consumption'] = df_annual_consumption['Total OECD Petroleum Consumption'] + df_annual_consumption['Total non-OECD Petroleum Consumption']

        # Create a stacked bar chart
        fig = go.Figure()

        # Add sub-component traces
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Canada Petroleum Consumption'], name='Canada Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Europe OECD Petroleum Consumption'], name='Europe OECD Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Japan Petroleum Consumption'], name='Japan Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['United States Petroleum Consumption'], name='United States Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['U.S. Territories Petroleum Consumption'], name='U.S. Territories Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Other OECD Petroleum Consumption'], name='Other OECD Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['China Petroleum Consumption'], name='China Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Eurasia Petroleum Consumption'], name='Eurasia Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Europe non-OECD Petroleum Consumption'], name='Europe non-OECD Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Other Asia Petroleum Consumption'], name='Other Asia Petroleum Consumption', visible=True))
        fig.add_trace(go.Bar(x=df_annual_consumption['Year'], y=df_annual_consumption['Other Non-OECD Petroleum Consumption'], name='Other Non-OECD Petroleum Consumption', visible=True))



        fig.update_layout(
            title='World Petroleum and Other Liquid Consumption Components',
            xaxis_title='Year',
            yaxis_title='Volume (million barrels per day)',
            barmode='stack',
        )

        st.plotly_chart(fig, use_container_width=True)

        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")


        st.download_button(
            label="Download data as CSV",
            data=convert_df(df_annual_consumption),
            file_name="OilAnnualConsumption.csv",
            mime="text/csv",
            )



###########################
    with tab5:
        st.subheader("EIA Weekly Inventory numbers")
        # Suppress SSL verification warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

         # Series to fetch
        series_list = {
            'WGTSTUS1': 'U.S. Ending Stocks of Total Gasoline',
            'WDISTUS1': 'U.S. Ending Stocks of Distillate Fuel Oil',
            'WCESTUS1' : 'U.S. Ending Stocks excluding SPR of Crude Oil',
        }

        # Function to fetch data from the API
        def fetch_data(series):
            url = f"https://api.eia.gov/v2/petroleum/sum/sndw/data/?api_key=gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h&frequency=weekly&data[0]=value&facets[series][]={series}&start=2024-01-01&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                return response.json().get('response', {}).get('data', [])
            else:
                print(f"Failed to fetch data for series {series}: {response.status_code} {response.reason}")
                return []

        # Function to calculate W-o-W changes
        def calculate_wow_changes(data):
            dates = [entry['period'] for entry in data]
            values = [float(entry['value']) for entry in data]
            changes = [values[i] - values[i+1] for i in range(len(values)-1)]
            return dates[:-1], changes


        # Fetch data for each series
        series_data = {series: fetch_data(series) for series in series_list}

        def plot_series(series_key, series_name):
            # Fetch data for the series
            data = fetch_data(series_key)

            # Check if data is available
            if data:
                # Calculate week-over-week changes
                wow_dates, wow_changes = calculate_wow_changes(data)

                # Create a bar plot
                fig = go.Figure(go.Bar(
                    x=wow_dates,
                    y=wow_changes,
                    marker_color=['green' if change > 0 else 'red' for change in wow_changes]
                ))

                # Customize layout for the bar plot
                fig.update_layout(
                    title=f'Week-over-Week Changes in {series_name}',
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='W-o-W Change (Thousand Barrels)'),
                    plot_bgcolor='rgba(0,0,0,0)'
                )

                # Show plot
                st.plotly_chart(fig, use_container_width=True)
                
        def calculate_latest_and_wow_percentage(data):
            if len(data) >= 2:
                latest_value = float(data[0]['value'])
                previous_value = float(data[1]['value'])
                wow_percentage_change = ((latest_value - previous_value) / previous_value) * 100
                wow_change = (latest_value - previous_value) 
                return latest_value, wow_percentage_change, wow_change
            else:
                return None, None

        def plot_inventory_levels(series_key, series_name):
            data = series_data.get(series_key, [])
            if data:
                dates = [entry['period'] for entry in data]
                values = [float(entry['value']) for entry in data]
                fig = go.Figure(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    line=dict(color='blue', width=2)
                ))
                fig.update_layout(
                    title=f'{series_name} Levels Over Time',
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Inventory Levels (Thousand Barrels)'),
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)


        # Function to fetch data from the API
        def fetch_data_2(series, start_date):
            url = f"https://api.eia.gov/v2/petroleum/sum/sndw/data/?api_key=gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h&frequency=weekly&data[0]=value&facets[series][]={series}&start={start_date}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                return response.json().get('response', {}).get('data', [])
            else:
                st.error(f"Failed to fetch data for series {series}: {response.status_code} {response.reason}")
                return []
            
        # Function to calculate 5-year range and average
        def calculate_five_year_stats(data):
            weekly_values = defaultdict(list)
            for entry in data:
                week = datetime.strptime(entry['period'], "%Y-%m-%d").strftime("%U")
                weekly_values[week].append(float(entry['value']))
            
            five_year_min = {week: min(values) for week, values in weekly_values.items()}
            five_year_max = {week: max(values) for week, values in weekly_values.items()}
            five_year_avg = {week: sum(values) / len(values) for week, values in weekly_values.items()}
            return five_year_min, five_year_max, five_year_avg

        # Series to fetch
        series_list = {
            'WCESTUS1': 'U.S. Ending Stocks excluding SPR of Crude Oil',
            'WGTSTUS1': 'U.S. Ending Stocks of Total Gasoline',
            'WDISTUS1': 'U.S. Ending Stocks of Distillate Fuel Oil',
        }


        # Calculate the start date for 5 years of historical data
        start_date_2 = (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")

        # Fetch data for each series
        series_data_2 = {series: fetch_data_2(series, start_date_2) for series in series_list}


        # Create separate plots for each series
        figs = {}
        for i, (series, data) in enumerate(series_data_2.items(), start=1):
            if data:
                # Extract dates and values
                dates = [entry['period'] for entry in data]
                values = [float(entry['value']) for entry in data]
                
                # Calculate 5-year range and average
                five_year_min, five_year_max, five_year_avg = calculate_five_year_stats(data)
                weeks = [datetime.strptime(date, "%Y-%m-%d").strftime("%U") for date in dates]
                min_values = [five_year_min[week] for week in weeks]
                max_values = [five_year_max[week] for week in weeks]
                avg_values = [five_year_avg[week] for week in weeks]
                
                # Create a plot
                fig = go.Figure()

                # Add actual values line plot
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=values, 
                    mode='lines',
                    name='Actual Values',
                    marker=dict(color='blue'),
                    line=dict(color='blue')
                ))
                
                # Add 5-year range as a filled area
                fig.add_trace(go.Scatter(
                    x=dates + dates[::-1],
                    y=max_values + min_values[::-1],
                    fill='toself',
                    fillcolor='rgba(0,100,80,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    showlegend=True,
                    name='5-Year Range'
                ))

                # Add 5-year average line plot
                fig.add_trace(go.Scatter(
                    x=dates, 
                    y=avg_values, 
                    mode='lines',
                    name='5-Year Average',
                    line=dict(color='orange', dash='dash')
                ))

                # Customize layout
                fig.update_layout(
                    title=f'{series_list[series]}',
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Value (Thousand Barrels)'),
                    plot_bgcolor='rgba(0,0,0,0)'
                )

                # Store plot in dictionary
                figs[f'fig{i}'] = fig



        col3,col4,col5 = st.columns(3)

        with col3:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WCESTUS1'])
            st.metric(label="U.S. Crude Oil Inventory", value=str(f"Δ {wow_change:,.0f} k barrels"), delta=str(f"{wow_percentage_change:,.02f}")+"%")
            # Plot for 'U.S. Ending Stocks excluding SPR of Crude Oil'
            plot_series('WCESTUS1', 'U.S. Crude Oil Inventory')
            plot_inventory_levels('WCESTUS1', 'U.S. Crude Oil Inventory')
            st.plotly_chart(figs['fig1'], use_container_width=True)

        with col4:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WGTSTUS1'])
            st.metric(label="U.S. Gasoline Inventory", value=str(f"Δ {wow_change:,.0f} k barrels"), delta=str(f"{wow_percentage_change:,.02f}")+"%")
            # Plot for 'U.S. Ending Stocks of Total Gasoline'
            plot_series('WGTSTUS1', 'U.S. Gasoline Inventory')
            plot_inventory_levels('WGTSTUS1', 'U.S. Gasoline Inventory')
            st.plotly_chart(figs['fig2'], use_container_width=True)

        with col5:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WDISTUS1'])
            st.metric(label="U.S. Distillate Inventory", value=str(f"Δ {wow_change:,.0f} k barrels"), delta=str(f"{wow_percentage_change:,.02f}")+"%")
            # Plot for 'U.S. Ending Stocks of Distillate Fuel Oil'
            plot_series('WDISTUS1', 'U.S. Distillate Inventory')
            plot_inventory_levels('WDISTUS1', 'U.S. Distillate Inventory')
            st.plotly_chart(figs['fig3'], use_container_width=True)


        with tab6:

            st.subheader("EIA Weekly Inventory numbers")

            
                # Function to fetch data from the API
            def fetch_data(series,start_date):
                url = f"https://api.eia.gov/v2/petroleum/sum/sndw/data/?api_key=gcp5ZkcZhaL5aCVvviD38eMtVEZXEyP28KqMHh4h&frequency=weekly&data[0]=value&facets[series][]={series}&start={start_date}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
                response = requests.get(url, verify=False)
                if response.status_code == 200:
                    return response.json()['response']['data']
                else:
                    print(f"Failed to fetch data for series {series}")
                    return []

            # Series to fetch
            series_list = {
                'WTTSTUS1': 'U.S. Ending Stocks of Crude Oil and Petroleum Products',
                'WTESTUS1': 'U.S. Ending Stocks excluding SPR of Crude Oil and Petroleum Products',
                'WCSSTUS1': 'U.S. Ending Stocks of Crude Oil in SPR',
                'WGTSTUS1': 'U.S. Ending Stocks of Total Gasoline',
                'WKJSTUS1': 'U.S. Ending Stocks of Kerosene-Type Jet Fuel',
                'WDISTUS1': 'U.S. Ending Stocks of Distillate Fuel Oil',
                'WCESTUS1' : 'U.S. Ending Stocks excluding SPR of Crude Oil',
            }

            # Calculate the default date (today minus three months)
            default_date = date.today() - relativedelta(months=12)

            # Date input widget to select the start date
            start_date = st.date_input("Choose start date", default_date)

            # Convert the date to a string in the format 'YYYY-MM-DD'
            start_date_str = start_date.strftime('%Y-%m-%d')

            # Fetch data for each series
            series_data = {series: fetch_data(series, start_date_str) for series in series_list}

            # Function to calculate W-o-W changes
            def calculate_wow_changes(data):
                dates = [entry['period'] for entry in data]
                values = [int(entry['value']) for entry in data]
                changes = [values[i] - values[i+1] for i in range(len(values)-1)]
                return dates[:-1], changes

            # Initialize Plotly figure for the original data
            fig_original = go.Figure()

            # Initialize Plotly figure for the W-o-W changes
            fig_wow = go.Figure()

            # Add data to the figures
            for series, data in series_data.items():
                if data:
                    dates = [entry['period'] for entry in data]
                    values = [int(entry['value']) for entry in data]
                    fig_original.add_trace(go.Scatter(x=dates, y=values, mode='lines', name=series_list[series]))
                    
                    wow_dates, wow_changes = calculate_wow_changes(data)
                    fig_wow.add_trace(go.Scatter(x=wow_dates, y=wow_changes, mode='lines', name=series_list[series]))

            # Customize layout for the original data plot
            fig_original.update_layout(
                title='U.S. Ending Stocks of Various Petroleum Products',
                xaxis=dict(title='Date'),
                yaxis=dict(title='Ending Stocks (Thousand Barrels)'),
                plot_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            )

            # Customize layout for the W-o-W changes plot
            fig_wow.update_layout(
                title='Week-over-Week Changes in U.S. Ending Stocks of Various Petroleum Products',
                xaxis=dict(title='Date'),
                yaxis=dict(title='W-o-W Change (Thousand Barrels)'),
                plot_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            )

            # Show plots
            st.plotly_chart(fig_original, use_container_width=True)
            st.plotly_chart(fig_wow, use_container_width=True)


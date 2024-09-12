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

    st.header("Fundamental Indicators")
    # Add fundamentals page specific code here

    tab1, tabx, tab4, tab2, tab5, tab6  = st.tabs(["Balances", "Production", "Consumption","Seasonality", "EIA Inventory","EIA Inventory (SPR)"])

    with tab1:
        st.subheader("Supply-Demand balances")
        st.write("""
            The Supply-Demand balances provides an analysis of global petroleum production and consumption over time.
            The following charts display trends in production and consumption, as well as oversupply or undersupply.
            Please note that some of the numbers presented are forecasts and may be subject to change.
            
            Detailed breakdowns of consumption and production can be found in their respective tabs.
            Data is sourced from the [U.S. Energy Information Administration (EIA)](https://www.eia.gov/).
        """)

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


        params_template = {
        "api_key": api_key,
        "frequency": "quarterly",
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
        production_periods = [item['period'] for item in production_data['response']['data']]
        production_values = {item['period']: float(item['value']) for item in production_data['response']['data']}
        consumption_values = {item['period']: float(item['value']) for item in consumption_data['response']['data']}

        # Calculate oversupply/undersupply
        all_periods = sorted(set(production_periods + list(consumption_values.keys())), reverse=False)
        oversupply_undersupply = {period: production_values.get(period, 0) - consumption_values.get(period, 0) for period in all_periods}

        # Create a DataFrame
        df = pd.DataFrame({
            'Period': all_periods,
            'Production': [production_values.get(period, 0) for period in all_periods],
            'Consumption': [consumption_values.get(period, 0) for period in all_periods],
            'Oversupply/Undersupply': [oversupply_undersupply.get(period, 0) for period in all_periods]
        })

        # Create the first plot for Production and Consumption
        fig1q = go.Figure()
        fig1q.add_trace(go.Scatter(x=df['Period'], y=df['Production'], mode='lines+markers', name='Production'))
        fig1q.add_trace(go.Scatter(x=df['Period'], y=df['Consumption'], mode='lines+markers', name='Consumption'))

        fig1q.update_layout(
            title='World Petroleum Quarterly Production vs Consumption ',
            xaxis_title='Quarter',
            yaxis_title='Volume (million barrels per day)',
            template='plotly_white'
        )


        # Create the second plot for Oversupply/Undersupply
        fig2q = go.Figure()
        fig2q.add_trace(go.Bar(x=df['Period'], y=df['Oversupply/Undersupply'], name='Oversupply/Undersupply',
                            marker_color=df['Oversupply/Undersupply'].apply(lambda x: 'green' if x >= 0 else 'red')))

        fig2q.update_layout(
            title='World Petroleum Quarterly Oversupply/Undersupply',
            xaxis_title='Quarter',
            yaxis_title='Volume (million barrels per day)',
        )


        col1, col2= st.columns(2)
        # Show the DataFrame and the plots
        with col1:
            st.plotly_chart(fig1,use_container_width=True)
            # Use the font with right-aligned text
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            st.plotly_chart(fig1q,use_container_width=True)
            # Use the font with right-aligned text
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
        
        with col2:
            st.plotly_chart(fig2,use_container_width=True)
            # Use the font with right-aligned text
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            st.plotly_chart(fig2q,use_container_width=True)
            # Use the font with right-aligned text
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

        st.subheader("Other sources of Supply-Demand Balances")
        st.write("""
        1. The [OPEC Monthly Oil Market Report (MOMR)](https://www.opec.org/opec_web/en/publications/338.htm) covers major issues affecting the world oil market and provides an outlook for crude oil market developments for the coming year. 
        The report provides a detailed analysis of key developments impacting oil market trends in world oil demand, supply as well as the oil market balance.
        
        2. The [IEA Oil Market Report (OMR)](https://www.iea.org/energy-system/fossil-fuels/oil)is one of the world's most authoritative and timely sources of data, forecasts and analysis on the global oil market – 
        including detailed statistics and commentary on oil supply, demand, inventories, prices and refining activity, as well as oil trade for IEA and selected non-IEA countries.
                 
        3. The [Wood Mackenzie Portal](https://my.woodmac.com/) provides comprehensive data, forecasts, and expert analysis on global oil markets. It offers in-depth insights into oil supply and demand dynamics, pricing trends, 
        refining activities, and trade flows. Covering key regions and major players, the report delivers detailed statistics and commentary, 
        helping industry stakeholders make informed decisions with timely and authoritative information on oil market developments.

        """)

    with tabx:
        st.subheader("World Petroleum and Other Liquid Production Components")


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

        params = {
            "api_key": api_key,
            "frequency": "annual",
            "data[]": "value",
            "start": "2000",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }

        # Fetch OPEC production data
        params["facets[seriesId][]"] = "PAPR_OPECPLUS_OPEC"
        data_production_OPEC = fetch_data(api_url, params)

        # Fetch Non-OPEC production data
        params["facets[seriesId][]"] = "PAPR_OPECPLUS_OTHER"
        data_production_OPECP = fetch_data(api_url, params)

        # Fetch Non-OPEC production data
        params["facets[seriesId][]"] = "PAPR_WORLD"
        data_production_WORLD = fetch_data(api_url, params)




        # Extract production data
        periods = [int(item['period']) for item in data_production_OPEC['response']['data']]
        production_values_OPEC = [float(item['value']) for item in data_production_OPEC['response']['data']]
        production_values_OPECP = [float(item['value']) for item in data_production_OPECP['response']['data']]
        production_values_WORLD = [float(item['value']) for item in data_production_WORLD['response']['data']]

        # Correct calculation of world production values (element-wise subtraction)
        production_values_others = [
            world - opecp - opec
            for world, opecp, opec in zip(production_values_WORLD, production_values_OPECP, production_values_OPEC)
        ]


        # Create a stacked bar chart
        fig = go.Figure()
        # Add traces with raw values for the text
        fig.add_trace(go.Bar(x=periods, y=production_values_OPEC, name='OPEC Members Production', text=production_values_OPEC, textposition='auto'))
        fig.add_trace(go.Bar(x=periods, y=production_values_OPECP, name='OPEC+ Additional Members Production', text=production_values_OPECP, textposition='auto'))
        fig.add_trace(go.Bar(x=periods, y=production_values_others, name='Other Production', text=production_values_others, textposition='auto'))


        # Update traces to format the text as x.x M
        fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',textfont_color="white")

        fig.update_layout(
            title='Total World Petroleum and Other Liquid Production Breakdown',
            xaxis_title='Year',
            yaxis_title='Volume (million barrels per day)',
            barmode='stack',
        )

        st.plotly_chart(fig,use_container_width=True)

        st.divider()

        col_OPEC,col_OPECPLUS,col_NON = st.columns(3)

        with col_OPEC:
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



            params = {
                "api_key": api_key,
                "frequency": "annual",
                "data[]": "value",
                "start": "2000",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": 0,
                "length": 5000
            }

            # Algeria
            params["facets[seriesId][]"] = "PAPR_AG"
            data_production_Algeria = fetch_data(api_url, params)

            # Congo (Brazzaville)
            params["facets[seriesId][]"] = "PAPR_CF"
            data_production_Congo_Brazzaville = fetch_data(api_url, params)

            # Equatorial Guinea
            params["facets[seriesId][]"] = "PAPR_EK"
            data_production_Equatorial_Guinea = fetch_data(api_url, params)

            # Gabon
            params["facets[seriesId][]"] = "PAPR_GB"
            data_production_Gabon = fetch_data(api_url, params)

            # Iran
            params["facets[seriesId][]"] = "PAPR_IR"
            data_production_Iran = fetch_data(api_url, params)

            # Iraq
            params["facets[seriesId][]"] = "PAPR_IZ"
            data_production_Iraq = fetch_data(api_url, params)

            # Kuwait
            params["facets[seriesId][]"] = "PAPR_KU"
            data_production_Kuwait = fetch_data(api_url, params)

            # Libya
            params["facets[seriesId][]"] = "PAPR_LY"
            data_production_Libya = fetch_data(api_url, params)

            # Nigeria
            params["facets[seriesId][]"] = "PAPR_NI"
            data_production_Nigeria = fetch_data(api_url, params)

            # Saudi Arabia
            params["facets[seriesId][]"] = "PAPR_SA"
            data_production_Saudi_Arabia = fetch_data(api_url, params)

            # United Arab Emirates
            params["facets[seriesId][]"] = "PAPR_TC"
            data_production_UAE = fetch_data(api_url, params)

            # Venezuela
            params["facets[seriesId][]"] = "PAPR_VE"
            data_production_Venezuela = fetch_data(api_url, params)




            # Extract production data
            periods = [int(item['period']) for item in data_production_Saudi_Arabia['response']['data']]

            def extract_production_values(data):
                return [float(item['value']) for item in data['response']['data']]

            # Extract production values for each country
            production_values_Algeria = extract_production_values(data_production_Algeria)
            production_values_Congo_Brazzaville = extract_production_values(data_production_Congo_Brazzaville)
            production_values_Equatorial_Guinea = extract_production_values(data_production_Equatorial_Guinea)
            production_values_Gabon = extract_production_values(data_production_Gabon)
            production_values_Iran = extract_production_values(data_production_Iran)
            production_values_Iraq = extract_production_values(data_production_Iraq)
            production_values_Kuwait = extract_production_values(data_production_Kuwait)
            production_values_Libya = extract_production_values(data_production_Libya)
            production_values_Nigeria = extract_production_values(data_production_Nigeria)
            production_values_Saudi_Arabia = extract_production_values(data_production_Saudi_Arabia)
            production_values_UAE = extract_production_values(data_production_UAE)
            production_values_Venezuela = extract_production_values(data_production_Venezuela)



            # Create a stacked bar chart
            fig = go.Figure()

            # Add traces for each country
            fig.add_trace(go.Bar(x=periods, y=production_values_Algeria, name='Algeria', text=production_values_Algeria))
            fig.add_trace(go.Bar(x=periods, y=production_values_Congo_Brazzaville, name='Congo (Brazzaville)', text=production_values_Congo_Brazzaville))
            fig.add_trace(go.Bar(x=periods, y=production_values_Equatorial_Guinea, name='Equatorial Guinea', text=production_values_Equatorial_Guinea))
            fig.add_trace(go.Bar(x=periods, y=production_values_Gabon, name='Gabon', text=production_values_Gabon))
            fig.add_trace(go.Bar(x=periods, y=production_values_Iran, name='Iran', text=production_values_Iran))
            fig.add_trace(go.Bar(x=periods, y=production_values_Iraq, name='Iraq', text=production_values_Iraq))
            fig.add_trace(go.Bar(x=periods, y=production_values_Kuwait, name='Kuwait', text=production_values_Kuwait))
            fig.add_trace(go.Bar(x=periods, y=production_values_Libya, name='Libya', text=production_values_Libya))
            fig.add_trace(go.Bar(x=periods, y=production_values_Nigeria, name='Nigeria', text=production_values_Nigeria))
            fig.add_trace(go.Bar(x=periods, y=production_values_Saudi_Arabia, name='Saudi Arabia', text=production_values_Saudi_Arabia))
            fig.add_trace(go.Bar(x=periods, y=production_values_UAE, name='United Arab Emirates', text=production_values_UAE))
            fig.add_trace(go.Bar(x=periods, y=production_values_Venezuela, name='Venezuela', text=production_values_Venezuela))


            # Update traces to format the text as x.x M
            fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',textfont_color="white")

            fig.update_layout(
                title='Total OPEC Member Production Breakdown',
                xaxis_title='Year',
                yaxis_title='Volume (million barrels per day)',
                barmode='stack',
            )


            st.plotly_chart(fig,use_container_width=True)
        with col_OPECPLUS:
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



            params = {
                "api_key": api_key,
                "frequency": "annual",
                "data[]": "value",
                "start": "2000",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": 0,
                "length": 5000
            }

            params["facets[seriesId][]"] = "PAPR_AJ"
            data_production_Azerbaijan = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_BA"
            data_production_Bahrain = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_BX"
            data_production_Brunei = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_KZ"
            data_production_Kazakhstan = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_MY"
            data_production_Malaysia = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_MX"
            data_production_Mexico = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_MU"
            data_production_Oman = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_RS"
            data_production_Russia = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_OD"
            data_production_South_Sudan = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_SU"
            data_production_Sudan = fetch_data(api_url, params)




            # Extract production data
            periods = [int(item['period']) for item in data_production_Sudan['response']['data']]

            def extract_production_values(data):
                return [float(item['value']) for item in data['response']['data']]

            # Extract production values for each country
            production_values_Azerbaijan = extract_production_values(data_production_Azerbaijan)
            production_values_Bahrain = extract_production_values(data_production_Bahrain)
            production_values_Brunei = extract_production_values(data_production_Brunei)
            production_values_Kazakhstan = extract_production_values(data_production_Kazakhstan)
            production_values_Malaysia = extract_production_values(data_production_Malaysia)
            production_values_Mexico = extract_production_values(data_production_Mexico)
            production_values_Oman = extract_production_values(data_production_Oman)
            production_values_Russia = extract_production_values(data_production_Russia)
            production_values_South_Sudan = extract_production_values(data_production_South_Sudan)
            production_values_Sudan = extract_production_values(data_production_Sudan)



            # Create a stacked bar chart
            fig = go.Figure()
            # Add a trace for each country
            fig.add_trace(go.Bar(x=periods, y=production_values_Azerbaijan, name='Algeria', text=production_values_Azerbaijan))
            fig.add_trace(go.Bar(x=periods, y=production_values_Bahrain, name='Bahrain', text=production_values_Bahrain))
            fig.add_trace(go.Bar(x=periods, y=production_values_Brunei, name='Brunei', text=production_values_Brunei))
            fig.add_trace(go.Bar(x=periods, y=production_values_Kazakhstan, name='Kazakhstan', text=production_values_Kazakhstan))
            fig.add_trace(go.Bar(x=periods, y=production_values_Malaysia, name='Malaysia', text=production_values_Malaysia))
            fig.add_trace(go.Bar(x=periods, y=production_values_Mexico, name='Mexico', text=production_values_Mexico))
            fig.add_trace(go.Bar(x=periods, y=production_values_Oman, name='Oman', text=production_values_Oman))
            fig.add_trace(go.Bar(x=periods, y=production_values_Russia, name='Russia', text=production_values_Russia))
            fig.add_trace(go.Bar(x=periods, y=production_values_South_Sudan, name='South Sudan', text=production_values_South_Sudan))
            fig.add_trace(go.Bar(x=periods, y=production_values_Sudan, name='Sudan', text=production_values_Sudan))


            # Update traces to format the text as x.x M
            fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',textfont_color="white")

            fig.update_layout(
                title='Additional OPEC+ Members Production Breakdown',
                xaxis_title='Year',
                yaxis_title='Volume (million barrels per day)',
                barmode='stack',
            )


            st.plotly_chart(fig,use_container_width=True)
        with col_NON:
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



            params = {
                "api_key": api_key,
                "frequency": "annual",
                "data[]": "value",
                "start": "2000",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": 0,
                "length": 5000
            }

            # Fetch data for each country
            params["facets[seriesId][]"] = "PAPR_CA"
            data_production_Canada = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_US"
            data_production_United_States = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_AR"
            data_production_Argentina = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_BR"
            data_production_Brazil = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_CO"
            data_production_Colombia = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_GY"
            data_production_Guyana = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_NO"
            data_production_Norway = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_UK"
            data_production_United_Kingdom = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_QA"
            data_production_Qatar = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_AO"
            data_production_Angola = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_EG"
            data_production_Egypt = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_CH"
            data_production_China = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_IN"
            data_production_India = fetch_data(api_url, params)

            params["facets[seriesId][]"] = "PAPR_ID"
            data_production_Indonesia = fetch_data(api_url, params)

            # Fetch data for extras
            params["facets[seriesId][]"] = "PAPR_NONOPECPLUS_XUS"
            data_production_others = fetch_data(api_url, params)




            # Extract production data
            periods = [int(item['period']) for item in data_production_Indonesia['response']['data']]

            def extract_production_values(data):
                return [float(item['value']) for item in data['response']['data']]

            # Extract production values for each country
            production_values_Canada = extract_production_values(data_production_Canada)
            production_values_United_States = extract_production_values(data_production_United_States)
            production_values_Argentina = extract_production_values(data_production_Argentina)
            production_values_Brazil = extract_production_values(data_production_Brazil)
            production_values_Colombia = extract_production_values(data_production_Colombia)
            production_values_Guyana = extract_production_values(data_production_Guyana)
            production_values_Norway = extract_production_values(data_production_Norway)
            production_values_United_Kingdom = extract_production_values(data_production_United_Kingdom)
            production_values_Qatar = extract_production_values(data_production_Qatar)
            production_values_Angola = extract_production_values(data_production_Angola)
            production_values_Egypt = extract_production_values(data_production_Egypt)
            production_values_China = extract_production_values(data_production_China)
            production_values_India = extract_production_values(data_production_India)
            production_values_Indonesia = extract_production_values(data_production_Indonesia)

            production_values_others = extract_production_values(data_production_others)

            # Correct calculation of other production values (element-wise subtraction)
            other_production_values = [
                others - (canada + argentina + brazil + colombia + guyana +
                        norway + uk + qatar + angola + egypt +
                        china + india + indonesia)
                for others, canada, argentina, brazil, colombia, guyana,
                    norway, uk, qatar, angola, egypt, china, india, indonesia
                in zip(production_values_others, production_values_Canada,
                    production_values_Argentina, production_values_Brazil,
                    production_values_Colombia, production_values_Guyana,
                    production_values_Norway, production_values_United_Kingdom,
                    production_values_Qatar, production_values_Angola,
                    production_values_Egypt, production_values_China,
                    production_values_India, production_values_Indonesia)
            ]



            # Create a stacked bar chart
            fig = go.Figure()

            # Add traces for each country
            fig.add_trace(go.Bar(x=periods, y=other_production_values, name='Others', text=other_production_values))
            fig.add_trace(go.Bar(x=periods, y=production_values_Canada, name='Canada', text=production_values_Canada))
            fig.add_trace(go.Bar(x=periods, y=production_values_United_States, name='United States', text=production_values_United_States))
            fig.add_trace(go.Bar(x=periods, y=production_values_Argentina, name='Argentina', text=production_values_Argentina))
            fig.add_trace(go.Bar(x=periods, y=production_values_Brazil, name='Brazil', text=production_values_Brazil))
            fig.add_trace(go.Bar(x=periods, y=production_values_Colombia, name='Colombia', text=production_values_Colombia))
            fig.add_trace(go.Bar(x=periods, y=production_values_Guyana, name='Guyana', text=production_values_Guyana))
            fig.add_trace(go.Bar(x=periods, y=production_values_Norway, name='Norway', text=production_values_Norway))
            fig.add_trace(go.Bar(x=periods, y=production_values_United_Kingdom, name='United Kingdom', text=production_values_United_Kingdom))
            fig.add_trace(go.Bar(x=periods, y=production_values_Qatar, name='Qatar', text=production_values_Qatar))
            fig.add_trace(go.Bar(x=periods, y=production_values_Angola, name='Angola', text=production_values_Angola))
            fig.add_trace(go.Bar(x=periods, y=production_values_Egypt, name='Egypt', text=production_values_Egypt))
            fig.add_trace(go.Bar(x=periods, y=production_values_China, name='China', text=production_values_China))
            fig.add_trace(go.Bar(x=periods, y=production_values_India, name='India', text=production_values_India))
            fig.add_trace(go.Bar(x=periods, y=production_values_Indonesia, name='Indonesia', text=production_values_Indonesia))



            # Update traces to format the text as x.x M
            fig.update_traces(texttemplate='%{text:.2f}', textposition='inside',textfont_color="white")

            fig.update_layout(
                title='Non-OPEC Member Production Breakdown',
                xaxis_title='Year',
                yaxis_title='Volume (million barrels per day)',
                barmode='stack',
            )


            st.plotly_chart(fig,use_container_width=True)

        st.divider()

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

        params = {
            "api_key": api_key,
            "frequency": "monthly",
            "data[]": "value",
            "start": "1998",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }

        # Fetch OPEC+ production data
        params["facets[seriesId][]"] = "COPR_OPECPLUS"
        data_production_OPECPLUS = fetch_data(api_url, params)

        # Fetch US production data
        params["facets[seriesId][]"] = "COPRPUS"
        data_production_US = fetch_data(api_url, params)

        # Fetch US production data
        params["facets[seriesId][]"] = "COPR_NONOPECPLUS_XUS"
        data_production_NONOPECxUS = fetch_data(api_url, params)

        # Extract production data
        periods = [item['period'] for item in data_production_OPECPLUS['response']['data']]
        production_values_OPECPLUS = [float(item['value']) for item in data_production_OPECPLUS['response']['data']]
        production_values_US = [float(item['value']) for item in data_production_US['response']['data']]
        production_values_NONOPECxUS = [float(item['value']) for item in data_production_NONOPECxUS['response']['data']]

        # Calculate market share percentage of OPEC+ over total volume
        total_volume = [p + c + d for p, c , d in zip(production_values_OPECPLUS, production_values_US, production_values_NONOPECxUS)]
        opec_plus_market_share = [(p / t) * 100 for p, t in zip(production_values_OPECPLUS, total_volume)]

        # Create a stacked bar chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=periods, y=production_values_OPECPLUS, name='OPEC+ Production'))
        fig.add_trace(go.Scatter(x=periods, y=production_values_US, name='US Production'))
        fig.add_trace(go.Scatter(x=periods, y=production_values_NONOPECxUS, name='Non OPEC+ exUS Production'))


        fig.update_layout(
            title='Total World Petroleum and Other Liquid Production by OPEC+ and Non-OPEC',
            xaxis_title='Month',
            yaxis_title='Volume (million barrels per day)',
        )

        # Print the DataFrame
        df = pd.DataFrame({
            'Month': periods,
            'OPEC+ Production': production_values_OPECPLUS,
            'US Production': production_values_US,
            'Non OPEC+ exUS Production': production_values_NONOPECxUS,
            'OPEC+ Market Share (%)': opec_plus_market_share
        })

        
        
        # Create a line plot for OPEC+ market share
        fig_market_share = go.Figure()
        fig_market_share.add_trace(go.Scatter(x=periods, y=opec_plus_market_share, mode='lines', name='OPEC+ Market Share'))

        fig_market_share.update_layout(
            title='OPEC+ Market Share Over Time',
            xaxis_title='Month',
            yaxis_title='Market Share (%)',
            template='plotly_white'
        )

        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")
        
        st.divider()

        st.subheader("Total World Petroleum and Other Liquid Production by OPEC+, US, and Non-OPEC (ex-US)")
        
        st.write("""
                 This line chart tracks the production volumes of petroleum and other liquids by major global players: OPEC+, the US, and non-OPEC countries excluding the US. 
                 
                 OPEC+ includes the OPEC member countries plus additional producers such as Russia, Kazakhstan, Azerbaijan, Mexico, and Oman.Each line 
                 represents the production trends of these groups, highlighting their contributions to global supply.   """)
        

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

        st.divider()

        st.subheader("OPEC+ Market Share")

        st.write("""
                 The OPEC+ Market Share chart illustrates the percentage of global petroleum production attributed to OPEC+ over time. It captures fluctuations in OPEC+’s share of the global market, reflecting its influence on global supply relative to other producers. 
                 
                 This chart highlights how OPEC+’s market share evolves, potentially due to changes in production levels, global demand, or competition from other major producers. By tracking these changes, the chart provides valuable insights into the shifting balance of power within the global oil market.   """)
        
        
        
        st.plotly_chart(fig_market_share, use_container_width=True)
        st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

        st.download_button(
            label="Download data as CSV",
            data=convert_df(df),
            file_name="OilMonthlyProduction.csv",
            mime="text/csv",
            )


#####################################
    with tab2:
        st.subheader("Monthly and Quarterly Seasonality Analysis")

        st.write(
            """
            This heatmap illustrates the month-on-month (left) or quarter-on-quarter(right) percentage 
            change in Brent Crude Oil prices over the past decade. Each cell represents the average 
            percentage change for a specific month or quarter of each year. The color gradient ranges from red (indicating a decrease) to green (indicating an increase), providing a visual overview of seasonal trends and fluctuations in oil prices.
            
            Key Insights:

            - Observe the seasonal patterns where certain months consistently show higher or lower changes.
            - Identify trends and anomalies in the price changes month by month.

            """
        )

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
            
            st.plotly_chart(fig_monthly,use_container_width=True)
            st.markdown("<p class='left-align'>Source: Yahoo Finance</p>", unsafe_allow_html=True)
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
            
            st.plotly_chart(fig_quarterly,use_container_width=True)
            st.markdown("<p class='left-align'>Source: Yahoo Finance</p>", unsafe_allow_html=True)

        #####################



        st.divider()
        st.subheader("Interactive Period Analysis")

        st.write(
            """
            Use the slider to select different periods and observe the average month-on-month percentage change in Brent Crude Oil prices. This bar chart aggregates the average changes over the selected years, helping you understand longer-term trends and variations in seasonal patterns.
            
            Key Insights:

            - The color-coded bars indicate positive (green) and negative (red) average changes.
            - Customize the period to examine how seasonality and trends evolve over different time frames.

            """
        )
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
            st.markdown("<p class='left-align'>Source: Yahoo Finance</p>", unsafe_allow_html=True)

        # Call the update plot function with the initial period value
        update_plot(period)




##################################################
    with tab4:
        st.subheader("World Petroleum and Other Liquid Consumption ")
        st.write("""
                This chart offers a comprehensive overview of global petroleum consumption, segmented into various categories. 
                 
                 It includes total consumption figures for OECD countries, which are further divided into specific regions such as 
                 Canada, Europe OECD, Japan, the United States, U.S. Territories, and Other OECD 
                 members. Additionally, it captures total consumption by non-OECD countries, 
                 including China, Eurasia, Europe non-OECD, Other Asia, and Other Non-OECD regions. 
                 
                 The stacked bar chart displays these components to show how each region’s consumption contributes to the overall global demand.
                """)
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
        st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

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

        st.write(
            """
            The metrics provide a quick overview of the most recent changes in U.S. inventory levels for crude oil, gasoline, and distillates. 
            """
        )

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
                    title=f'{series_name} Absolute Levels Over Time',
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
            

        with col4:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WGTSTUS1'])
            st.metric(label="U.S. Gasoline Inventory", value=str(f"Δ {wow_change:,.0f} k barrels"), delta=str(f"{wow_percentage_change:,.02f}")+"%")
            

        with col5:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WDISTUS1'])
            st.metric(label="U.S. Distillate Inventory", value=str(f"Δ {wow_change:,.0f} k barrels"), delta=str(f"{wow_percentage_change:,.02f}")+"%")
            

        st.divider()

        st.subheader('Week-on-Week inventory changes and absoulte inventory levels')

        st.write(
            """
            The upper bar plots below displays the week-over-week changes in U.S. inventory levels while the line plot below instead shows absolute inventory levels. Each plot shows the fluctuations in inventory levels, with
            inventory buildups indicated in green and inventory drawdowns in red.
            """
        )

        col6,col7,col8 = st.columns(3)

        with col6:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WCESTUS1'])
            # Plot for 'U.S. Ending Stocks excluding SPR of Crude Oil'
            plot_series('WCESTUS1', 'U.S. Crude Oil Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            plot_inventory_levels('WCESTUS1', 'U.S. Crude Oil Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            

        with col7:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WGTSTUS1'])
            
            # Plot for 'U.S. Ending Stocks of Total Gasoline'
            plot_series('WGTSTUS1', 'U.S. Gasoline Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            plot_inventory_levels('WGTSTUS1', 'U.S. Gasoline Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            

        with col8:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WDISTUS1'])
           
            # Plot for 'U.S. Ending Stocks of Distillate Fuel Oil'
            plot_series('WDISTUS1', 'U.S. Distillate Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
            plot_inventory_levels('WDISTUS1', 'U.S. Distillate Inventory')
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)
        
        st.divider()

        st.subheader('Historical inventory levels and range')

        st.write(
            """
            The line graph illustrate the historical inventory levels over time. The plots include actual values, a 5-year range, and a 5-year average, offering a comprehensive view of long-term trends and seasonal patterns.
            """
        )

        col9,col10,col11 = st.columns(3)

        with col9:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WCESTUS1'])
            st.plotly_chart(figs['fig1'], use_container_width=True)
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

        with col10:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WGTSTUS1'])
            st.plotly_chart(figs['fig2'], use_container_width=True)
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)

        with col11:
            latest_value, wow_percentage_change, wow_change = calculate_latest_and_wow_percentage(series_data['WDISTUS1'])

            st.plotly_chart(figs['fig3'], use_container_width=True)
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)


    with tab6:

            st.subheader("EIA Strategic Petroleum Reserve (SPR)")

            st.write(
            """
            The Strategic Petroleum Reserve (SPR) is the world's largest supply of emergency crude oil, maintained by the U.S. Department of Energy. It was established to mitigate the impact of disruptions in the supply of petroleum products and ensure energy security. The SPR provides a critical buffer against unforeseen events that could affect the availability of crude oil, such as natural disasters, geopolitical conflicts, or significant market fluctuations.

            **Strategic Petroleum Reserve (SPR) Inventory Levels Over Time**
            
            This line plot illustrates the historical levels of crude oil in the U.S. Strategic Petroleum Reserve (SPR) over time. 
            The plot includes actual values and a 5-year range offering a comprehensive view of US government usage of the SPR inventory.
            """
            )


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


            series_list = {
                'WCSSTUS1': 'U.S. Ending Stocks of Crude Oil in SPR',
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


                    # Customize layout
                    fig.update_layout(
                        title=f'{series_list[series]}',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Value (Thousand Barrels)'),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )

                    # Store plot in dictionary
                    figs[f'fig{i}'] = fig



            st.plotly_chart(figs['fig1'], use_container_width=True)
            st.markdown("<p class='left-align'>Source: EIA</p>", unsafe_allow_html=True)






            

            


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



def macro_economic_page():
    st.header("Macro-economic Indicators")
    # Add macro-economic page specific code hedre

    tab1, tab2, tab3 = st.tabs(['Global data','HOPE Analysis','Geopolitical Risk'],)

    with tab1:
        def news_verification():
            url = "https://tradingeconomics.com/matrix?g=top"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            

            try:
                # Open the URL and read the content
                session = requests.Session()
                response = session.get(url, headers=headers)
                
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response.content, "html.parser")
                # Find the table rows containing the data
                rows = soup.select('tr')
                
                # Extract data from each row
                data = []
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) > 0:
                        country_data = {
                            'Country': columns[0].get_text(strip=True),
                            'GDP': columns[1].get_text(strip=True),
                            'GDP Growth': columns[2].get_text(strip=True),
                            'Interest Rate': columns[3].get_text(strip=True),
                            'Inflation Rate': columns[4].get_text(strip=True),
                            'Jobless Rate': columns[5].get_text(strip=True),
                            'Gov. Budget': columns[6].get_text(strip=True),
                            'Debt/GDP': columns[7].get_text(strip=True),
                            'Current Account': columns[8].get_text(strip=True),
                            'Population': columns[9].get_text(strip=True),
                        }
                        data.append(country_data)
                
                return data
            
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        def format_number(num_str):
            try:
                num_str = num_str.replace(',', '').replace('%', '').strip()  # Remove commas and percentage signs
                return float(num_str) if num_str else None
            except ValueError:
                return num_str

        def highlight_extremes(s, n=3):
            is_max = s.nlargest(n).index
            is_min = s.nsmallest(n).index
            return ['background-color: lightgreen' if i in is_max else 'background-color: salmon' if i in is_min else '' for i in range(len(s))]

        # Streamlit layout
        st.subheader("Economic Indicators Snapshot")

        st.write("""
            This section provides a detailed snapshot of key economic indicators for various countries to give insights into the economic health and performance of a country. The table below presents the following data:

            - **GDP (USD Billion):** The total market value of all final goods and services produced in a country in a given year, measured in billions of US dollars. *Source: World Bank*
            - **GDP Annualized QoQ Growth (%):** The quarter-over-quarter growth rate of GDP, expressed as an annualized percentage. *Source: Central Bank of each country*
            - **Interest Rate (%):** The central bank's policy rate, which influences the cost of borrowing and saving in the economy. *Source: Central Bank of each country*
            - **Inflation Rate (%):** The percentage change in the general price level of goods and services, typically over a year. *Source: Central Bank of each country*
            - **Jobless Rate (%):** The percentage of the labor force that is unemployed and actively seeking employment. *Source: Central Bank of each country*
            - **Gov. Budget (%):** The government budget balance as a percentage of GDP, indicating surplus or deficit. *Source: Central Bank of each country*
            - **Debt/GDP (%):** The ratio of a country's national debt to its GDP, expressed as a percentage. *Source: Central Bank of each country*
            - **Current Account (%):** The current account balance as a percentage of GDP, showing net exports and income flows. *Source: Central Bank of each country*
            - **Population (Million):** The total number of people living in the country, measured in millions. *Source: World Bank*

            In the table, the top three highest values for each indicator are highlighted in green, and the top three lowest values are highlighted in red. This color coding does not signify whether the values are good or bad; it is simply to visually distinguish the extremes.
        """)

        news_data = news_verification()

        if news_data:
            # Create DataFrame
            df = pd.DataFrame(news_data)

            # Define a mapping from original column names to new header names
            column_mapping = {
                'Country': 'Country',
                'GDP': 'GDP (USD Bil)',
                'GDP Growth': 'GDP Annualized QoQ Growth (%)',
                'Interest Rate': 'Interest Rate (%)',
                'Inflation Rate': 'Inflation Rate (%)',
                'Jobless Rate': 'Jobless Rate (%)',
                'Gov. Budget': 'Gov. Budget (%)',
                'Debt/GDP': 'Debt/GDP (%)',
                'Current Account': 'Current Account (%)',
                'Population': 'Population (mil)'
            }
            
            # Rename columns in the DataFrame
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert numerical columns to floats
            numeric_columns = ['GDP (USD Bil)', 'GDP Annualized QoQ Growth (%)', 'Interest Rate (%)', 'Inflation Rate (%)', 
                            'Jobless Rate (%)', 'Gov. Budget (%)', 'Debt/GDP (%)', 'Current Account (%)', 'Population (mil)']
            
            for column in numeric_columns:
                df[column] = df[column].apply(format_number)
                df[column] = pd.to_numeric(df[column], errors='coerce')

            # Apply highlighting
            df_styled = df.style.apply(highlight_extremes, subset=numeric_columns, axis=0)
            
            # Display DataFrame with formatting
            st.dataframe(df_styled.format({
                'GDP (USD Bil)': "{:,.0f}",
                'GDP Annualized QoQ Growth (%)': "{:,.2f}",
                'Interest Rate (%)': "{:,.2f}",
                'Inflation Rate (%)': "{:,.2f}",
                'Jobless Rate (%)': "{:,.2f}",
                'Gov. Budget (%)': "{:,.2f}",
                'Debt/GDP (%)': "{:,.2f}",
                'Current Account (%)': "{:,.2f}",
                'Population (mil)': "{:,.0f}",
            }), height=800, hide_index=True, use_container_width=True)


            st.subheader('Bubble Chart')
            st.write("""
            A bubble chart showing the relationship between GDP, GDP Growth, and Population for each country.
            """)

            fig = px.scatter(df, y='GDP (USD Bil)', x='GDP Annualized QoQ Growth (%)', size='Population (mil)', color='Country',
                            title='GDP, GDP Growth, and Population by Country',
                            labels={'GDP (USD Bil)': 'GDP (USD Billion)', 'GDP Annualized QoQ Growth (%)': 'GDP Growth (%)', 'Population (mil)': 'Population (Million)'})
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Failed to extract data")

        st.subheader("GDP time series chart")

        # Define the base URL and endpoint format
        base_url = "https://api.db.nomics.world/v22/series/WB/WDI/A-NY.GDP.MKTP.CD-{country_code}?&observations=1"

        # List of top 20 countries with their DBnomics country codes
        country_codes = {
            "United States": "USA",
            "China": "CHN",
            "Japan": "JPN",
            "Eurozone": "EMU",
            "India": "IND",
            "United Kingdom": "GBR",
            "Italy": "ITA",
            "Canada": "CAN",

        }

        # Prepare a dictionary to hold GDP data
        gdp_data = {}

        # Function to fetch and process data for a single country
        def fetch_country_data(country, code):
            url = base_url.format(country_code=code)
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            
            json_data = response.json()
            series = json_data.get("series", {}).get("docs", [])[0]
            
            # Extract relevant information
            if series:
                years = series.get("period", [])
                values = series.get("value", [])
                
                # Filter data from 2000 onwards
                filtered_data = {year: value for year, value in zip(years, values) if int(year) >= 2000}
                return country, filtered_data
            return country, {}

        # Use ThreadPoolExecutor to parallelize requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_country = {executor.submit(fetch_country_data, country, code): country for country, code in country_codes.items()}
            
            for future in as_completed(future_to_country):
                country, data = future.result()
                gdp_data[country] = data

        # Convert the filtered data to a pandas DataFrame
        df = pd.DataFrame(gdp_data).T  # Transpose to have countries as rows and years as columns

        # Reset index to have country names as a column
        df = df.reset_index()
        df = df.melt(id_vars="index", var_name="Year", value_name="GDP")
        df.columns = ["Country", "Year", "GDP"]

        # Plot using Plotly Express
        fig = px.line(df, x="Year", y="GDP", color="Country",
                    title="GDP of Top Countries (2000 onwards)",
                    labels={"GDP": "GDP (Current US$)", "Year": "Year"},
                    markers=True)

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Define your FRED API key (replace with your actual API key)
        api_key = "0ba1761f1d82d23194c202620bb7d7f9"
        # Define the URL for the FRED API
        url = f"https://api.stlouisfed.org/fred/series/observations"

        st.subheader("HOPE Analysis")
        st.write("""
            The HOPE model, developed by [Michael Kantrowitz](https://www.advisorperspectives.com/articles/2023/02/15/the-leading-indicators-are-signaling-recession) of Piper Sandler, is an economic indicator model that focuses on four key components. HOPE is an acronym describing the sequence in which economic activity weakens due to a FED tightening cycle before a recession namely Housing, New Orders, Corporate Profits and Employment which typically happen in sequence. 
            Economically speaking, the HOPE framework is driven by the realization that the most interest rate sensitive sectors are the first to feel the effects of tightening monetary policy.
                 
            These sectors often act as leading economic indicators. Consequently, as tightening monetary policy slows down economic activity in interest rate sensitive sectors, other sectors of the economy start to feel the impact of higher rates. 
            HOPE sequences the lags between rate hikes and their effect on economic activity for each sector.                 
                 """)


        st.subheader("1. Housing")
        st.write("""
                    The housing market is a crucial component of the economy, as it impacts consumer spending, construction activity, and overall economic sentiment. 
                    The Case-Shiller Home Price Index is a widely recognized U.S. housing market indicator that tracks changes in residential real estate prices.

                    Within the HOPE framework, it tends to be the earliest indicator to turn negative hence serves as a leading indicator. 
                    """)
        
        series_id = "CSUSHPINSA"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": "2004-01-01", 
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            
            # Extract the data and create a DataFrame
            data = data["observations"]
            df = pd.DataFrame(data)
            
            df["date"] = pd.to_datetime(df["date"])
            
            df["value"] = pd.to_numeric(df["value"], errors="coerce").round(2)
            
            df["percent_change"] = df["value"].pct_change(periods=12) * 100
            
            # Calculate the 2 standard deviation confidence interval
            std_dev = df["percent_change"].std()
            df["upper_std_dev"] = df["percent_change"] + 2 * std_dev
            df["lower_std_dev"] = df["percent_change"] - 2 * std_dev 

            # Create a Plotly figure
            fig = go.Figure()
            
            # Add the percent change line
            fig.add_trace(go.Scatter(x=df["date"], y=df["percent_change"], mode='lines', name='Percent Change'))
            
            # Add the confidence interval as a shaded region
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["upper_std_dev"],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["lower_std_dev"],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.2)',
                line=dict(width=0),
                name='2 Standard Deviation Confidence Interval'
            ))
            
            # Add a zero line
            fig.add_trace(go.Scatter(
                x=[df["date"].min(), df["date"].max()],
                y=[0, 0],
                mode='lines',
                line=dict(color='orange', dash='dash'),
                name='Zero Line'
            ))

            # Add shaded regions for recession periods
            recession_periods = [
                ('2007-12-01', '2009-06-30'),  # Great Recession
                ('2020-02-01', '2020-11-30'),  # COVID-19 Recession
            ]
            for start, end in recession_periods:
                fig.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    name="Recession Period"
                )

            fig.update_layout(
                title="Case-Shiller Home Price Index - Percent Change from Last Year",
                xaxis_title="Date",
                yaxis_title="Percent Change",
                xaxis_rangeslider_visible=False,
                legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",    # Position at the top
            y=-0.2,           # Move below the plot
            xanchor="center", # Center horizontally
            x=0.5             # Center horizontally
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.2)',    # Color of the grid lines
            gridwidth=1,              # Width of the major grid lines
            tickmode='linear',        # Mode for tick placement
            tick0=df["date"].min(),   # Start tick at the minimum date
            dtick='M12',              # Major tick every year (12 months)
            )
        
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
        
        st.divider()
        st.subheader("2. Orders")
        st.write("""
                    New orders for durable goods and manufacturing indicate future production activity. 
                    An increase in new orders suggests that businesses are experiencing higher demand and are preparing to increase production, which is a positive sign for economic growth.
                    Manufacturers’ New Orders is a key economic indicator and measures the total value of new orders placed with manufacturers. It reflects the demand for goods produced by the manufacturing sector and serves as a gauge of economic health and future industrial activity. 

                    The HOPE framework indicates that it will be the next indicator to show a downturn after housing.
                    """)

        series_id = "AMTMNO"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": "2004-01-01", 
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            
            # Extract the data and create a DataFrame
            data = data["observations"]
            df = pd.DataFrame(data)
            
            df["date"] = pd.to_datetime(df["date"])
            
            df["value"] = pd.to_numeric(df["value"], errors="coerce").round(2)
            
            df["percent_change"] = df["value"].pct_change(periods=12) * 100
            
            # Calculate the 2 standard deviation confidence interval
            std_dev = df["percent_change"].std()
            df["upper_std_dev"] = df["percent_change"] + 2 * std_dev
            df["lower_std_dev"] = df["percent_change"] - 2 * std_dev 

            # Create a Plotly figure
            fig = go.Figure()
            
            # Add the percent change line
            fig.add_trace(go.Scatter(x=df["date"], y=df["percent_change"], mode='lines', name='Percent Change'))
            
            # Add the confidence interval as a shaded region
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["upper_std_dev"],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["lower_std_dev"],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.2)',
                line=dict(width=0),
                name='2 Standard Deviation Confidence Interval'
            ))
            
            # Add a zero line
            fig.add_trace(go.Scatter(
                x=[df["date"].min(), df["date"].max()],
                y=[0, 0],
                mode='lines',
                line=dict(color='orange', dash='dash'),
                name='Zero Line'
            ))

            # Add shaded regions for recession periods
            recession_periods = [
                ('2007-12-01', '2009-06-30'),  # Great Recession
                ('2020-02-01', '2020-11-30'),  # COVID-19 Recession
            ]
            for start, end in recession_periods:
                fig.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    name="Recession Period"
                )

            fig.update_layout(
                title="Manufacturers' New Orders: Total Manufacturing - Percent Change from Last Year",
                xaxis_title="Date",
                yaxis_title="Percent Change",
                xaxis_rangeslider_visible=False,
                legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",    # Position at the top
            y=-0.2,           # Move below the plot
            xanchor="center", # Center horizontally
            x=0.5             # Center horizontally
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.2)',    # Color of the grid lines
            gridwidth=1,              # Width of the major grid lines
            tickmode='linear',        # Mode for tick placement
            tick0=df["date"].min(),   # Start tick at the minimum date
            dtick='M12',              # Major tick every year (12 months)
            )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")        




        st.divider()
        st.subheader("3. Profits")
        st.write("""
                    Corporate profits reflect the financial health of companies and their ability to invest, hire, and expand. Rising profits typically lead to increased business investment and hiring, supporting economic growth.
                    Corporate Profits After Tax is a critical economic metric provided by the U.S. Federal Reserve. It quantifies the net profits of corporations after deducting taxes with some adjustments. 

                    It serves as a significant indicator of corporate financial performance, economic vitality, and investment potential and is the third economic indicator in the HOPE indicator sequence
                    """)
        
        series_id = "CP"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": "2004-01-01", 
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            
            # Extract the data and create a DataFrame
            data = data["observations"]
            df = pd.DataFrame(data)
            
            df["date"] = pd.to_datetime(df["date"])
            
            df["value"] = pd.to_numeric(df["value"], errors="coerce").round(2)
            
            df["percent_change"] = df["value"].pct_change() * 100
            
            # Calculate the 2 standard deviation confidence interval
            std_dev = df["percent_change"].std()
            df["upper_std_dev"] = df["percent_change"] + 2 * std_dev
            df["lower_std_dev"] = df["percent_change"] - 2 * std_dev 

            # Create a Plotly figure
            fig = go.Figure()
            
            # Add the percent change line
            fig.add_trace(go.Scatter(x=df["date"], y=df["percent_change"], mode='lines', name='Percent Change'))
            
            
            # Add a zero line
            fig.add_trace(go.Scatter(
                x=[df["date"].min(), df["date"].max()],
                y=[0, 0],
                mode='lines',
                line=dict(color='orange', dash='dash'),
                name='Zero Line'
            ))

            # Add shaded regions for recession periods
            recession_periods = [
                ('2007-12-01', '2009-06-30'),  # Great Recession
                ('2020-02-01', '2020-11-30'),  # COVID-19 Recession
            ]
            for start, end in recession_periods:
                fig.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    name="Recession Period"
                )

            fig.update_layout(
                title="Corporate Profits After Tax (without IVA and CCAdj) - Percent Change from Previous Data Point",
                xaxis_title="Date",
                yaxis_title="Percent Change",
                xaxis_rangeslider_visible=False,
                legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",    # Position at the top
            y=-0.2,           # Move below the plot
            xanchor="center", # Center horizontally
            x=0.5             # Center horizontally
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.2)',    # Color of the grid lines
            gridwidth=1,              # Width of the major grid lines
            tickmode='linear',        # Mode for tick placement
            tick0=df["date"].min(),   # Start tick at the minimum date
            dtick='M12',              # Major tick every year (12 months)
            )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}") 



        st.divider()
        st.subheader("4. Employment")
        st.write("""
                Employment levels are a direct measure of economic health. High employment means more people have income to spend, which drives consumer demand and overall economic activity. Conversely, rising unemployment can signal economic distress.
                The Unemployment Rate is a key economic indicator that measures the percentage of the labor force that is unemployed and actively seeking employment. It provides insights into a country’s economic health and labor market conditions. 

                The HOPE framework suggests that this is the last indicator to show weakness, and sometimes shows weakness only after the recession has started in earnest.
                    """)
        
        series_id = "UNRATE"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": "2004-01-01", 
        }

        # Make the API request
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            
            # Extract the data and create a DataFrame
            data = data["observations"]
            df = pd.DataFrame(data)
            
            df["date"] = pd.to_datetime(df["date"])
            
            df["value"] = pd.to_numeric(df["value"], errors="coerce").round(2)
            
            

            # Create a Plotly figure
            fig = go.Figure()
            
            # Add the percent change line
            fig.add_trace(go.Scatter(x=df["date"], y=df["value"], mode='lines', name='Unemployment Rate'))
            
            

            # Add shaded regions for recession periods
            recession_periods = [
                ('2007-12-01', '2009-06-30'),  # Great Recession
                ('2020-02-01', '2020-11-30'),  # COVID-19 Recession
            ]
            for start, end in recession_periods:
                fig.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    name="Recession Period"
                )

            fig.update_layout(
                title="Corporate Profits After Tax (without IVA and CCAdj) - Percent Change from Previous Data Point",
                xaxis_title="Date",
                yaxis_title='Unemployment Rate',
                xaxis_rangeslider_visible=False,
                legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",    # Position at the top
            y=-0.2,           # Move below the plot
            xanchor="center", # Center horizontally
            x=0.5             # Center horizontally
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.2)',    # Color of the grid lines
            gridwidth=1,              # Width of the major grid lines
            tickmode='linear',        # Mode for tick placement
            tick0=df["date"].min(),   # Start tick at the minimum date
            dtick='M12',              # Major tick every year (12 months)
            )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}") 






        st.divider()
        st.subheader("PMI")
        # Define the ISM PMI data URL
        pmi_url = "https://api.db.nomics.world/v22/series/ISM/pmi?facets=1&format=json&limit=1000&observations=1"

        # Fetch the PMI data
        response = requests.get(pmi_url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the JSON response
        json_data = response.json()
        series = json_data.get("series", {}).get("docs", [])

        # Prepare a list to hold PMI data
        pmi_data = []

        # Extract relevant information
        if series:
            entry = series[0]  # Since we have only one series in this response
            years = entry.get("period", [])
            values = entry.get("value", [])
            
            # Organize data into a list of dictionaries
            for year, value in zip(years, values):
                pmi_data.append({
                    "Date": year,
                    "PMI": value
                })

        # Convert the data to a pandas DataFrame
        df_pmi = pd.DataFrame(pmi_data)

        # Convert 'Date' to datetime
        df_pmi['Date'] = pd.to_datetime(df_pmi['Date'], format='%Y-%m')

        # Plot using Plotly Express
        fig_pmi = px.line(df_pmi, x="Date", y="PMI",
                        title="ISM PMI Data",
                        labels={"PMI": "PMI", "Date": "Date"},
                        markers=True)


        st.plotly_chart(fig_pmi, use_container_width=True)
        # Show the plot 

    with tab3:

        
        

        st.subheader("Geopolitical Risk Daily Index")

        st.write("""
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

        """)
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

        st.divider()
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




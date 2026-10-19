"""Explanatory copy for the macro page, carried over unchanged from the original page."""

TEXT = {
    "indicators": """
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

The checkbox below highlights the top three highest values in green and the top three lowest values in red for each indicator. This color coding is purely for visual distinction and does not indicate whether the values are favorable or unfavorable.
""",
    "bubble": """
A bubble chart showing the relationship between GDP, GDP Growth, and Population for each country.
""",
    "hope_intro": """
The HOPE model, developed by [Michael Kantrowitz](https://www.advisorperspectives.com/articles/2023/02/15/the-leading-indicators-are-signaling-recession) of Piper Sandler, is an economic indicator model that focuses on four key components. HOPE is an acronym describing the sequence in which the US economic activity weakens due to a FED tightening cycle before a recession namely Housing, New Orders, Corporate Profits and Employment which typically happen in sequence. 
Economically speaking, the HOPE framework is driven by the realization that the most interest rate sensitive sectors are the first to feel the effects of tightening monetary policy.

These sectors often act as leading economic indicators. Consequently, as tightening monetary policy slows down economic activity in interest rate sensitive sectors, other sectors of the economy start to feel the impact of higher rates. 
HOPE sequences the lags between rate hikes and their effect on economic activity for each sector.
""",
    "housing": """
The housing market is a crucial component of the economy, as it impacts consumer spending, construction activity, and overall economic sentiment. 
The Case-Shiller Home Price Index is a widely recognized U.S. housing market indicator that tracks changes in residential real estate prices. On the other hand, the National Association of Home Builders (NAHB) Housing Market Index (HMI) rates the relative level of current and 
future single-family home sales compiled from a survey of around 900 home builders while Single-Family Starts count the number of new single-family homes under construction.
A reading above 50 for the HMI indicates a favorable outlook on home sales; below indicates a negative outlook.

Within the HOPE framework, it tends to be the earliest indicator to turn negative hence serves as a leading indicator.
""",
    "orders": """
New orders for durable goods and manufacturing indicate future production activity. 
An increase in new orders suggests that businesses are experiencing higher demand and are preparing to increase production, which is a positive sign for economic growth.
Manufacturers’ New Orders is a key economic indicator and measures the total value of new orders placed with manufacturers. It reflects the demand for goods produced by the manufacturing sector and serves as a gauge of economic health and future industrial activity. 

Another indicator would be the US Manufacturing ISM Report On Business based on data compiled from purchasing and supply executives in the US. A PMI reading above 50 percent indicates that the manufacturing economy is generally expanding; below 50 percent indicates that it is generally declining.

The HOPE framework indicates that it will be the next indicator to show a downturn after housing.
""",
    "profits": """
Corporate profits reflect the financial health of companies and their ability to invest, hire, and expand. Rising profits typically lead to increased business investment and hiring, supporting economic growth.
Corporate Profits After Tax is a critical economic metric provided by the U.S. Federal Reserve. It quantifies the net profits of corporations after deducting taxes with some adjustments. 

It serves as a significant indicator of corporate financial performance, economic vitality, and investment potential and is the third economic indicator in the HOPE indicator sequence
""",
    "employment": """
Employment levels are a direct measure of economic health. High employment means more people have income to spend, which drives consumer demand and overall economic activity. Conversely, rising unemployment can signal economic distress.
The Unemployment Rate is a key economic indicator that measures the percentage of the labor force that is unemployed and actively seeking employment. It provides insights into a country’s economic health and labor market conditions. 

The HOPE framework suggests that this is the last indicator to show weakness, and sometimes shows weakness only after the recession has started in earnest.
""",
    "sahm": """
Sahm Recession Indicator signals the start of a recession when the three-month moving average of the national unemployment rate (U3) rises by 0.50 percentage points or more relative to the minimum of the three-month averages from the previous 12 months.
This indicator aims to provide timely warnings of economic downturns, offering a more immediate gauge of recession risk compared to traditional methods.
""",
}

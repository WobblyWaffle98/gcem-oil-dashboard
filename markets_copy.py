"""Explanatory copy for the Financial Markets page, carried over from the original page.
The S&P 500 heatmap and FX intro text were reworded because those widgets now use Yahoo Finance data."""

TEXT = {
    "heatmap": """
The interactive heatmap shows the largest companies in the S&P 500 index. Each block is coloured by its performance over the selected window, with block sizes proportional to market capitalisation.
Grouped by sector, it lets you identify trends and performance across industries. Hover over a sector or company for details.
It covers about 140 of the largest constituents rather than all 500; see the note below the chart for how to extend it.
""",
    "vix": """
The VIX Index, often referred to as the "Fear Gauge," is a measure of market volatility and investor sentiment. Officially known as the CBOE Volatility Index, it is calculated and published by the Chicago Board Options Exchange (CBOE).
The VIX Index represents the market's expectations of 30-day future volatility based on options prices for the S&P 500 Index (SPX).
""",
    "corr_eq": """
This section presents a heatmap displaying the correlation between major stock markets and Brent Crude Oil prices over different time periods.
The results are displayed using a color-coded heatmap, with correlation coefficients ranging from -1(red) to 1(blue).
""",
    "treasury": """
This section provides an analysis of the Treasury yield curve, showcasing both historical time series and recent changes in yield rates. The data is sourced from the **U.S. Department of the Treasury**, covering daily treasury rates for the past three years.

**What is a Yield Curve?**

A yield curve is a graphical representation of the interest rates (yields) on government bonds of varying maturities, plotted against their respective time to maturity. It shows the relationship between the yield and the time to maturity of debt securities issued by the government.

**Key Components:**

- **Yields**: The return investors receive for holding a bond until maturity, expressed as an annual percentage.
- **Maturities**: The time remaining until the bond’s principal is repaid, ranging from short-term (a few months) to long-term (30 years or more).


**Use of Yield Curves**:

- **Economic Indicators**: Yield curves are used to gauge economic expectations. A normal upward-sloping curve suggests economic growth, while an inverted curve may signal a recession.

- **Interest Rate Predictions**: They help in forecasting future interest rates based on the difference between short-term and long-term rates.

- **Investment Decisions**: Investors use yield curves to assess the risk and return of different securities. A steep curve can indicate higher returns for long-term investments compared to short-term ones.

- **Monetary Policy**: Central banks use yield curves to understand market expectations of future economic conditions and to set appropriate monetary policies.
""",
    "fx_intro": """
This section displays the latest cross rates and the daily percentage change for major currencies, calculated from Yahoo Finance quotes.
""",
    "corr_fx": """
This section presents a heatmap displaying the correlation between major FX and Brent Crude Oil prices over different time periods.
The results are displayed using a color-coded heatmap, with correlation coefficients ranging from -1(red) to 1(blue).
""",
    "dxy": """
This section presents both the time series and the rolling 1-year correlation between Brent crude oil prices and the DXY (U.S. Dollar Index).

**Key Observations**:
- **Traditional Correlation**: Historically, a strong inverse correlation existed between Brent crude oil prices and the DXY index—when the dollar strengthened, oil prices typically fell, and vice versa.
- **Evolving Dynamics**: The rolling correlation plot indicates that this traditional relationship has become less predictable.
- **Complex Interactions**: The current correlation reflects increased complexity due to various factors impacting the oil market, suggesting that simple historical patterns are no longer as applicable.
""",
}

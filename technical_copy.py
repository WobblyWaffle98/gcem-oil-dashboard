"""Explanatory copy for the technical and probability page. The Monte Carlo and indicator text is carried over from the original page;
only the sentences that referred to TradingView were rewritten for Yahoo Finance."""

TEXT = {
    "tech_intro": """
Interactive candlestick charts of Brent crude (ICE front-month futures, BZ=F) from Yahoo Finance. The daily chart carries standard pivot points and the intraday chart carries RSI and MACD, all calculated from the price data. Hover for prices, drag to pan and scroll to zoom.
""",
    "pivot": """
The latest Brent daily price data comes from Yahoo Finance (ICE Brent front-month futures, BZ=F). The chart includes "Pivot Points," which are commonly used to identify potential support and resistance levels based on historical price data. Pivot points are calculated using the previous period's high, low, and close prices. If the price is trading above the main pivot point, it is generally considered to indicate bullish sentiment, while a price trading below the pivot point suggests bearish sentiment.

Additionally, traders often look at the first, second, and third support (S1, S2, S3) and resistance levels (R1, R2, R3) derived from pivot points. These levels can serve as potential price targets or areas where reversals may occur. For instance, if the price approaches a resistance level and fails to break through, it may signal a reversal to the downside. Similarly, if the price finds support at a pivot level and holds, it may indicate a potential upward movement.
""",
    "rsi_macd": """
The chart includes the "RSI (Relative Strength Index)" and "MACD (Moving Average Convergence Divergence)" studies, which help identify potential market trends and momentum based on historical price data. Typically, if the RSI is above 50 and the MACD is above zero, the asset is considered to have positive momentum, while an RSI below 50 and a MACD below zero indicate negative momentum. However, it's also important to look for RSI divergence, 
which can signal a potential reversal despite the current momentum.
""",
    "mc_daily": """
**Predicting Oil Prices with Monte Carlo Simulation**

Monte Carlo simulation is a method used to estimate the future price of oil by considering various factors that influence its value. It's like guessing the possible outcomes of a game by rolling dice multiple times.

### How Does it Work?

1. **Understanding Oil Prices**: While oil prices are influenced by factors such as supply, demand, geopolitical events, and economic conditions, Monte Carlo simulation does not require direct input of these factors. Instead, it uses statistical properties such as historical price distributions and volatility.

2. **Simulating Scenarios**: The simulation generates thousands of possible future scenarios for oil prices by applying random variations to the historical price data. This process creates a diverse set of potential future price paths.

3. **Calculating Probabilities**: Each scenario represents a possible outcome, and the simulation calculates the likelihood of each scenario occurring.

4. **Analyzing Results**: By analyzing the range of possible outcomes and their probabilities, we can understand the potential risks and make informed decisions about oil-related strategies.
""",
    "mc_monthly": """
**Predicting Oil Prices with Monte Carlo Simulation (Monthly Average)**

Similar to the the daily Monte Carlo Analysis, it uses historical price to predict possible future scenarios but uses average historical price of every month instead of daily historical price. This will typically lead to lower volatility and a smaller Monte Carlo band.
""",
}

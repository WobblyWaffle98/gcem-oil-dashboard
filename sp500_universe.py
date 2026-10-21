"""Large-cap S&P 500 members used by the equity heatmap: (Yahoo symbol, name, GICS sector).

Yahoo Finance has no index-constituent endpoint, so this is a curated list of roughly the 140 largest members.
To cover all 500, add a file named sp500_constituents.csv next to the app with the columns Symbol, Name, Sector;
it replaces this list automatically. Symbols that Yahoo cannot return are skipped.
"""
import os

import pandas as pd

UNIVERSE = [
    # Information Technology
    ("AAPL", "Apple", "Information Technology"), ("MSFT", "Microsoft", "Information Technology"), ("NVDA", "NVIDIA", "Information Technology"),
    ("AVGO", "Broadcom", "Information Technology"), ("ORCL", "Oracle", "Information Technology"), ("CRM", "Salesforce", "Information Technology"),
    ("AMD", "AMD", "Information Technology"), ("CSCO", "Cisco", "Information Technology"), ("ADBE", "Adobe", "Information Technology"),
    ("ACN", "Accenture", "Information Technology"), ("IBM", "IBM", "Information Technology"), ("QCOM", "Qualcomm", "Information Technology"),
    ("TXN", "Texas Instruments", "Information Technology"), ("INTU", "Intuit", "Information Technology"), ("NOW", "ServiceNow", "Information Technology"),
    ("AMAT", "Applied Materials", "Information Technology"), ("MU", "Micron", "Information Technology"), ("PANW", "Palo Alto Networks", "Information Technology"),
    ("LRCX", "Lam Research", "Information Technology"), ("ANET", "Arista Networks", "Information Technology"), ("KLAC", "KLA", "Information Technology"),
    ("ADI", "Analog Devices", "Information Technology"), ("INTC", "Intel", "Information Technology"),
    # Communication Services
    ("GOOGL", "Alphabet", "Communication Services"), ("META", "Meta Platforms", "Communication Services"), ("NFLX", "Netflix", "Communication Services"),
    ("DIS", "Walt Disney", "Communication Services"), ("TMUS", "T-Mobile US", "Communication Services"), ("VZ", "Verizon", "Communication Services"),
    ("T", "AT&T", "Communication Services"), ("CMCSA", "Comcast", "Communication Services"),
    # Consumer Discretionary
    ("AMZN", "Amazon", "Consumer Discretionary"), ("TSLA", "Tesla", "Consumer Discretionary"), ("HD", "Home Depot", "Consumer Discretionary"),
    ("MCD", "McDonald's", "Consumer Discretionary"), ("LOW", "Lowe's", "Consumer Discretionary"), ("BKNG", "Booking Holdings", "Consumer Discretionary"),
    ("NKE", "Nike", "Consumer Discretionary"), ("SBUX", "Starbucks", "Consumer Discretionary"), ("TJX", "TJX Companies", "Consumer Discretionary"),
    ("CMG", "Chipotle", "Consumer Discretionary"), ("MAR", "Marriott", "Consumer Discretionary"), ("ORLY", "O'Reilly Automotive", "Consumer Discretionary"),
    ("GM", "General Motors", "Consumer Discretionary"), ("F", "Ford", "Consumer Discretionary"), ("ABNB", "Airbnb", "Consumer Discretionary"),
    # Consumer Staples
    ("WMT", "Walmart", "Consumer Staples"), ("COST", "Costco", "Consumer Staples"), ("PG", "Procter & Gamble", "Consumer Staples"),
    ("KO", "Coca-Cola", "Consumer Staples"), ("PEP", "PepsiCo", "Consumer Staples"), ("PM", "Philip Morris", "Consumer Staples"),
    ("MDLZ", "Mondelez", "Consumer Staples"), ("MO", "Altria", "Consumer Staples"), ("CL", "Colgate-Palmolive", "Consumer Staples"),
    ("TGT", "Target", "Consumer Staples"),
    # Health Care
    ("LLY", "Eli Lilly", "Health Care"), ("UNH", "UnitedHealth", "Health Care"), ("JNJ", "Johnson & Johnson", "Health Care"),
    ("ABBV", "AbbVie", "Health Care"), ("MRK", "Merck", "Health Care"), ("TMO", "Thermo Fisher", "Health Care"),
    ("ABT", "Abbott", "Health Care"), ("PFE", "Pfizer", "Health Care"), ("ISRG", "Intuitive Surgical", "Health Care"),
    ("AMGN", "Amgen", "Health Care"), ("DHR", "Danaher", "Health Care"), ("BMY", "Bristol-Myers Squibb", "Health Care"),
    ("GILD", "Gilead", "Health Care"), ("VRTX", "Vertex", "Health Care"), ("MDT", "Medtronic", "Health Care"),
    ("SYK", "Stryker", "Health Care"), ("CVS", "CVS Health", "Health Care"), ("REGN", "Regeneron", "Health Care"),
    ("ELV", "Elevance Health", "Health Care"),
    # Financials
    ("BRK-B", "Berkshire Hathaway", "Financials"), ("JPM", "JPMorgan Chase", "Financials"), ("V", "Visa", "Financials"),
    ("MA", "Mastercard", "Financials"), ("BAC", "Bank of America", "Financials"), ("WFC", "Wells Fargo", "Financials"),
    ("GS", "Goldman Sachs", "Financials"), ("MS", "Morgan Stanley", "Financials"), ("AXP", "American Express", "Financials"),
    ("C", "Citigroup", "Financials"), ("SPGI", "S&P Global", "Financials"), ("BLK", "BlackRock", "Financials"),
    ("SCHW", "Charles Schwab", "Financials"), ("PGR", "Progressive", "Financials"), ("CB", "Chubb", "Financials"),
    ("MMC", "Marsh McLennan", "Financials"),
    # Industrials
    ("GE", "GE Aerospace", "Industrials"), ("CAT", "Caterpillar", "Industrials"), ("RTX", "RTX", "Industrials"),
    ("HON", "Honeywell", "Industrials"), ("UNP", "Union Pacific", "Industrials"), ("BA", "Boeing", "Industrials"),
    ("DE", "Deere", "Industrials"), ("LMT", "Lockheed Martin", "Industrials"), ("UPS", "UPS", "Industrials"),
    ("ETN", "Eaton", "Industrials"), ("ADP", "ADP", "Industrials"), ("WM", "Waste Management", "Industrials"),
    # Energy
    ("XOM", "Exxon Mobil", "Energy"), ("CVX", "Chevron", "Energy"), ("COP", "ConocoPhillips", "Energy"),
    ("EOG", "EOG Resources", "Energy"), ("SLB", "Schlumberger", "Energy"), ("MPC", "Marathon Petroleum", "Energy"),
    ("PSX", "Phillips 66", "Energy"), ("OXY", "Occidental", "Energy"), ("WMB", "Williams", "Energy"),
    ("KMI", "Kinder Morgan", "Energy"), ("VLO", "Valero", "Energy"), ("HAL", "Halliburton", "Energy"),
    ("BKR", "Baker Hughes", "Energy"), ("OKE", "ONEOK", "Energy"),
    # Utilities
    ("NEE", "NextEra Energy", "Utilities"), ("SO", "Southern Company", "Utilities"), ("DUK", "Duke Energy", "Utilities"),
    ("CEG", "Constellation Energy", "Utilities"), ("AEP", "American Electric Power", "Utilities"), ("D", "Dominion Energy", "Utilities"),
    ("SRE", "Sempra", "Utilities"),
    # Real Estate
    ("PLD", "Prologis", "Real Estate"), ("AMT", "American Tower", "Real Estate"), ("EQIX", "Equinix", "Real Estate"),
    ("WELL", "Welltower", "Real Estate"), ("SPG", "Simon Property", "Real Estate"), ("PSA", "Public Storage", "Real Estate"),
    ("O", "Realty Income", "Real Estate"),
    # Materials
    ("LIN", "Linde", "Materials"), ("SHW", "Sherwin-Williams", "Materials"), ("FCX", "Freeport-McMoRan", "Materials"),
    ("ECL", "Ecolab", "Materials"), ("APD", "Air Products", "Materials"), ("NEM", "Newmont", "Materials"),
    ("NUE", "Nucor", "Materials"),
]


def load_universe():
    """sp500_constituents.csv (Symbol, Name, Sector) if present, otherwise the built-in list."""
    path = os.path.join(os.getcwd(), "sp500_constituents.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df = df.rename(columns={c: c.strip().title() for c in df.columns})
            if {"Symbol", "Name", "Sector"} <= set(df.columns):
                return [(str(r.Symbol).replace(".", "-"), r.Name, r.Sector) for r in df.itertuples()]
        except Exception:
            pass
    return UNIVERSE

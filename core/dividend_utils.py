import pandas as pd
from dividend import get_top_dividend_stocks

def get_top_dividends_table(limit=5):
    data = get_top_dividend_stocks(limit)
    if not data:
        return None

    df = pd.DataFrame(data)

    df.rename(columns={
        "symbol": "Symbol",
        "description": "Company Name",
        "dividendYield": "Dividend Yield (%)"
    }, inplace=True)

    df["Dividend Yield (%)"] = df["Dividend Yield (%)"].astype(float)
    df = df.sort_values("Dividend Yield (%)", ascending=False)

    return df.set_index("Symbol")

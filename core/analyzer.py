import pandas_ta as ta
from data import get_price_data, get_pe_ratio
from analysis import compute_indicators
from sentiment import get_news_sentiment

def analyze_stock(ticker: str):
    df = get_price_data(ticker)
    df["RSI"] = ta.rsi(df["Close"])
    macd = ta.macd(df["Close"])
    macd.columns = ["MACD", "MACD_Hist", "MACD_Signal"]
    df = df.join(macd)
    df = compute_indicators(df)

    pe = get_pe_ratio(ticker)
    sentiment = get_news_sentiment(ticker)

    return df, pe, sentiment

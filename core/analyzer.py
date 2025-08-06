import pandas_ta as ta
import sys
import os

# Add parent directory to Python path so we can import data, analysis, sentiment
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from .data import get_price_data, get_pe_ratio
    from .analysis import compute_indicators
    from .sentiment import get_news_sentiment
except ImportError as e:
    # Fallback: try importing from parent directory explicitly
    sys.path.append('..')
    from .data import get_price_data, get_pe_ratio
    from .analysis import compute_indicators
    from .sentiment import get_news_sentiment


def analyze_stock(ticker: str):
    """
    Analyze stock with technical indicators

    Args:
        ticker (str): Stock ticker symbol

    Returns:
        tuple: (DataFrame with OHLC + indicators, PE_ratio, sentiment_score)
    """
    df = get_price_data(ticker)
    df["RSI"] = ta.rsi(df["Close"])
    macd = ta.macd(df["Close"])
    macd.columns = ["MACD", "MACD_Hist", "MACD_Signal"]
    df = df.join(macd)
    df = compute_indicators(df)

    pe = get_pe_ratio(ticker)
    sentiment = get_news_sentiment(ticker)

    return df, pe, sentiment
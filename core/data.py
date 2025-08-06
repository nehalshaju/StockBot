import yfinance as yf
import pandas as pd

def get_price_data(symbol: str, period='6mo', interval='1d') -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval=interval)
    return df

def get_latest_price(symbol: str) -> float:
    return get_price_data(symbol, period='1d')['Close'].iloc[-1]

def get_pe_ratio(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    info = stock.info
    return info.get('trailingPE', None)

def get_price_and_pe_history(symbol: str):
    """Return a DataFrame with price and PE Ratio columns over time"""
    stock = yf.Ticker(symbol)
    df = stock.history(period='6mo', interval='1d')
    df['PE_Ratio'] = get_pe_ratio(symbol)
    return df
